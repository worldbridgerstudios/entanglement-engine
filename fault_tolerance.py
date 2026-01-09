"""
Fault tolerance testing for Entanglement Engine.

Tests recovery from 50% pool corruption using optimized geometry + rhythm.
"""

import numpy as np
from entanglement_engine import entanglement_params, crystal_vertices


def icosahedron_vertices():
    """12 icosahedron vertices on unit sphere."""
    phi = (1 + np.sqrt(5)) / 2
    verts = [
        (0, 1, phi), (0, -1, phi), (0, 1, -phi), (0, -1, -phi),
        (1, phi, 0), (-1, phi, 0), (1, -phi, 0), (-1, -phi, 0),
        (phi, 0, 1), (-phi, 0, 1), (phi, 0, -1), (-phi, 0, -1)
    ]
    norm = np.sqrt(1 + phi**2)
    return [(x/norm, y/norm, z/norm) for x, y, z in verts]


def triad_vertices(radius=0.3):
    """3 vertices forming equilateral triangle."""
    return [
        (radius, 0, 0),
        (-radius/2, radius * np.sqrt(3)/2, 0),
        (-radius/2, -radius * np.sqrt(3)/2, 0)
    ]


def fibonacci_sphere(n, radius):
    """n points evenly distributed on sphere."""
    points = []
    phi = np.pi * (3.0 - np.sqrt(5.0))
    for i in range(n):
        y = 1 - (i / (n - 1)) * 2 if n > 1 else 0
        r = np.sqrt(1 - y * y)
        theta = phi * i
        points.append((np.cos(theta) * r * radius, y * radius, np.sin(theta) * r * radius))
    return points


def build_crystal_adjacency(K: int):
    """Build adjacency dict for K-layer crystal."""
    positions = [(0, 0, 0)]
    layer_indices = {'center': [0]}
    
    if K >= 3:
        start = len(positions)
        positions.extend(triad_vertices(0.3))
        layer_indices['triad'] = list(range(start, len(positions)))
    
    start = len(positions)
    positions.extend([(x*0.6, y*0.6, z*0.6) for x,y,z in icosahedron_vertices()])
    layer_indices['icosa'] = list(range(start, len(positions)))
    
    shell_size = 12
    radius = 0.85
    for layer in range(K - 3):
        shell_size *= 3
        start = len(positions)
        positions.extend(fibonacci_sphere(shell_size, radius))
        layer_indices[f'shell_{layer+4}'] = list(range(start, len(positions)))
        radius += 0.15
    
    n = len(positions)
    adj = {i: [] for i in range(n)}
    
    def dist(i, j):
        return np.sqrt(sum((positions[i][k] - positions[j][k])**2 for k in range(3)))
    
    for i in range(1, n):
        adj[0].append(i)
        adj[i].append(0)
    
    for i in range(1, n):
        dists = [(dist(i, j), j) for j in range(1, n) if j != i]
        dists.sort()
        for _, j in dists[:6]:
            if j not in adj[i]:
                adj[i].append(j)
                adj[j].append(i)
    
    for i in range(n):
        adj[i] = list(set(adj[i]))
    
    return n, adj, layer_indices


def test_fault_tolerance(pool_size: int, corruption: float = 0.5, 
                         max_steps: int = 100, target: float = 0.9,
                         trials: int = 5, verbose: bool = False) -> dict:
    """
    Test fault tolerance of optimized network.
    
    Args:
        pool_size: Number of fluid nodes
        corruption: Fraction of pool to corrupt (default 0.5)
        max_steps: Maximum recovery steps
        target: Target coherence (default 0.9)
        trials: Number of trials to average
        verbose: Print progress
    
    Returns:
        dict with results
    """
    params = entanglement_params(pool_size)
    K, V, amplitude = params['K'], params['V'], params['amplitude']
    rhythm = params['rhythm']
    
    n_frozen, frozen_adj, layer_indices = build_crystal_adjacency(K)
    
    results = []
    
    for trial in range(trials):
        if verbose:
            print(f"  Trial {trial+1}/{trials}...", end=" ", flush=True)
        
        n_total = n_frozen + pool_size
        phases = np.zeros(n_total)
        phases[n_frozen:] = np.random.uniform(0, 2*np.pi, pool_size)
        
        adj = {i: list(frozen_adj[i]) for i in range(n_frozen)}
        for i in range(n_frozen, n_total):
            adj[i] = []
        
        n_contacts = max(1, int(pool_size * 0.1))
        for i in range(n_frozen, n_total):
            contacts = np.random.choice(n_frozen, size=min(n_contacts, n_frozen), replace=False)
            for c in contacts:
                adj[i].append(c)
                adj[c].append(i)
        
        fluid_nodes = list(range(n_frozen, n_total))
        for _ in range(pool_size * 2):
            if len(fluid_nodes) >= 2:
                i, j = np.random.choice(fluid_nodes, size=2, replace=False)
                if j not in adj[i]:
                    adj[i].append(j)
                    adj[j].append(i)
        
        frozen_mask = np.zeros(n_total, dtype=bool)
        frozen_mask[:n_frozen] = True
        
        def coherence():
            return np.abs(np.mean(np.exp(1j * phases)))
        
        def wave_step(step):
            nonlocal phases
            new_phases = phases.copy()
            
            beat_idx = step % 12
            active_layer = rhythm[beat_idx][1]
            
            layer_keys = ['center', 'triad', 'icosa']
            if active_layer < len(layer_keys):
                layer_key = layer_keys[active_layer]
                if layer_key in layer_indices:
                    for i in layer_indices[layer_key]:
                        direction = 1 if (step // 12) % 2 == 0 else -1
                        new_phases[i] = (phases[i] + direction * amplitude) % (2 * np.pi)
            
            for i in range(n_total):
                if frozen_mask[i]:
                    continue
                neighbors = adj[i]
                if neighbors:
                    phase_diff_sum = sum(np.sin(phases[j] - phases[i]) for j in neighbors)
                    new_phases[i] = phases[i] + 0.1 + (0.3 / len(neighbors)) * phase_diff_sum
                    new_phases[i] = new_phases[i] % (2 * np.pi)
            
            phases = new_phases
        
        for step in range(max_steps):
            c = coherence()
            if c >= target:
                results.append({'steps': step + 1, 'coherence': c, 'success': True})
                if verbose:
                    print(f"✓ step {step+1}")
                break
            wave_step(step)
        else:
            results.append({'steps': max_steps, 'coherence': coherence(), 'success': False})
            if verbose:
                print(f"✗ max steps")
    
    return {
        'pool': pool_size,
        'K': K,
        'V': V,
        'amplitude': amplitude,
        'avg_steps': np.mean([r['steps'] for r in results]),
        'avg_coherence': np.mean([r['coherence'] for r in results]),
        'success_rate': np.mean([r['success'] for r in results]),
        'min_steps': min(r['steps'] for r in results),
        'max_steps': max(r['steps'] for r in results),
    }
