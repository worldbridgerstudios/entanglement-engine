"""
Direct comparison: Geometry (ours) vs Correction (QLDPC-style)

Tests both approaches across exponential pool sizes.
"""

import numpy as np
from entanglement_engine import entanglement_params, T
from fault_tolerance import build_crystal_adjacency


def coherence(phases):
    """Kuramoto order parameter."""
    return np.abs(np.mean(np.exp(1j * phases)))


def run_geometry(pool_size: int, max_steps: int = 100, target: float = 0.9) -> dict:
    """
    Our approach: frozen seed + Kuramoto coupling + 3-6-9 rhythm.
    
    Returns: steps, final_coherence, corrections (always 0)
    """
    params = entanglement_params(pool_size)
    K, V, amplitude = params['K'], params['V'], params['amplitude']
    rhythm = params['rhythm']
    
    n_frozen, frozen_adj, layer_indices = build_crystal_adjacency(K)
    n_total = n_frozen + pool_size
    
    # Initialize: frozen at 0, pool random
    phases = np.zeros(n_total)
    phases[n_frozen:] = np.random.uniform(0, 2*np.pi, pool_size)
    
    # Build adjacency
    adj = {i: list(frozen_adj[i]) for i in range(n_frozen)}
    for i in range(n_frozen, n_total):
        adj[i] = []
    
    # Frozen-fluid contacts
    n_contacts = max(1, int(pool_size * 0.1))
    for i in range(n_frozen, n_total):
        contacts = np.random.choice(n_frozen, size=min(n_contacts, n_frozen), replace=False)
        for c in contacts:
            adj[i].append(c)
            adj[c].append(i)
    
    # Fluid-fluid sparse mesh
    fluid_nodes = list(range(n_frozen, n_total))
    for _ in range(pool_size * 2):
        if len(fluid_nodes) >= 2:
            i, j = np.random.choice(fluid_nodes, size=2, replace=False)
            if j not in adj[i]:
                adj[i].append(j)
                adj[j].append(i)
    
    frozen_mask = np.zeros(n_total, dtype=bool)
    frozen_mask[:n_frozen] = True
    
    # Run dynamics
    for step in range(max_steps):
        c = coherence(phases)
        if c >= target:
            return {'steps': step + 1, 'coherence': c, 'corrections': 0, 'success': True}
        
        new_phases = phases.copy()
        
        # Rhythm pulse to frozen seed
        beat_idx = step % 12
        active_layer = rhythm[beat_idx][1]
        layer_keys = ['center', 'triad', 'icosa']
        if active_layer < len(layer_keys):
            layer_key = layer_keys[active_layer]
            if layer_key in layer_indices:
                for i in layer_indices[layer_key]:
                    direction = 1 if (step // 12) % 2 == 0 else -1
                    new_phases[i] = (phases[i] + direction * amplitude) % (2 * np.pi)
        
        # Kuramoto coupling for fluid
        for i in range(n_total):
            if frozen_mask[i]:
                continue
            neighbors = adj[i]
            if neighbors:
                phase_diff_sum = sum(np.sin(phases[j] - phases[i]) for j in neighbors)
                new_phases[i] = phases[i] + 0.1 + (0.3 / len(neighbors)) * phase_diff_sum
                new_phases[i] = new_phases[i] % (2 * np.pi)
        
        phases = new_phases
    
    return {'steps': max_steps, 'coherence': coherence(phases), 'corrections': 0, 'success': False}


def run_correction(pool_size: int, max_steps: int = 100, target: float = 0.9,
                   threshold: float = 0.5, strength: float = 0.3) -> dict:
    """
    QLDPC-style: pure active error correction.
    
    No geometry. No passive coupling. Just:
    1. Detect deviation from reference
    2. Apply correction pulse
    
    This is what they actually do — active intervention only.
    
    Returns: steps, final_coherence, corrections (total count)
    """
    # Initialize all random
    phases = np.random.uniform(0, 2*np.pi, pool_size)
    reference = 0.0  # Target phase
    
    total_corrections = 0
    
    for step in range(max_steps):
        c = coherence(phases)
        if c >= target:
            return {'steps': step + 1, 'coherence': c, 'corrections': total_corrections, 'success': True}
        
        new_phases = phases.copy()
        step_corrections = 0
        
        # Pure error correction: check each node against reference
        for i in range(pool_size):
            # Wrap-aware error
            error = phases[i] - reference
            error = (error + np.pi) % (2 * np.pi) - np.pi  # Wrap to [-π, π]
            
            if abs(error) > threshold:
                # Apply correction pulse
                new_phases[i] = phases[i] - strength * np.sign(error)
                new_phases[i] = new_phases[i] % (2 * np.pi)
                step_corrections += 1
        
        # NO Kuramoto coupling — pure active correction only
        
        phases = new_phases
        total_corrections += step_corrections
    
    return {'steps': max_steps, 'coherence': coherence(phases), 'corrections': total_corrections, 'success': False}


def compare(max_pool: int, trials: int = 3):
    """
    Compare both approaches across exponential pool sizes.
    """
    # Generate test points with finer granularity
    pool_sizes = []
    for exp in range(2, 20):
        for mult in [0.5, 1.0, 2.0, 3.0, 5.0]:
            size = int(mult * (10 ** (exp / 2)))
            if 50 <= size <= max_pool:
                pool_sizes.append(size)
    pool_sizes = sorted(set(pool_sizes))
    
    print("=" * 90)
    print("GEOMETRY vs CORRECTION — Direct Comparison")
    print("=" * 90)
    print(f"Max pool: {max_pool:,}")
    print(f"Trials: {trials}")
    print(f"Test sizes: {len(pool_sizes)}")
    print("=" * 90)
    print()
    print(f"{'Pool':>10} | {'GEOMETRY':^30} | {'CORRECTION':^30} | {'Ratio'}")
    print(f"{'':>10} | {'steps':>8} {'coh':>6} {'seed':>8} | {'steps':>8} {'coh':>6} {'corr':>10} | {'corr:seed'}")
    print("-" * 90)
    
    results = []
    
    for pool in pool_sizes:
        params = entanglement_params(pool)  # Get our params for this pool size
        geo_steps, geo_coh, geo_corr = [], [], []
        cor_steps, cor_coh, cor_corr = [], [], []
        
        for _ in range(trials):
            # Our approach
            g = run_geometry(pool)
            geo_steps.append(g['steps'])
            geo_coh.append(g['coherence'])
            geo_corr.append(g['corrections'])
            
            # Their approach
            c = run_correction(pool)
            cor_steps.append(c['steps'])
            cor_coh.append(c['coherence'])
            cor_corr.append(c['corrections'])
        
        geo = {
            'steps': np.mean(geo_steps),
            'coherence': np.mean(geo_coh),
            'corrections': np.mean(geo_corr),
        }
        cor = {
            'steps': np.mean(cor_steps),
            'coherence': np.mean(cor_coh),
            'corrections': np.mean(cor_corr),
        }
        
        # Real comparison: their corrections vs our seed size
        geo_seed = params['V']  # Our frozen seed size
        cor_work = cor['corrections']
        ratio = cor_work / geo_seed if geo_seed > 0 else float('inf')
        
        print(f"{pool:>10,} | {geo['steps']:>8.1f} {geo['coherence']:>6.3f} {geo_seed:>8} | "
              f"{cor['steps']:>8.1f} {cor['coherence']:>6.3f} {cor_work:>10.0f}  {ratio:>6.0f}:1")
        
        results.append({
            'pool': pool,
            'geometry': geo,
            'correction': cor,
            'seed': params['V'],
            'ratio': cor['corrections'] / params['V'] if params['V'] > 0 else 0,
        })
    
    print()
    print("=" * 90)
    print("SUMMARY")
    print("=" * 90)
    
    # Scaling analysis
    geo_steps_trend = [r['geometry']['steps'] for r in results]
    cor_corr_trend = [r['correction']['corrections'] for r in results]
    ratio_trend = [r['ratio'] for r in results]
    
    print(f"Geometry steps range: {min(geo_steps_trend):.1f} - {max(geo_steps_trend):.1f} (O(1))")
    print(f"Correction count range: {min(cor_corr_trend):.0f} - {max(cor_corr_trend):.0f} (O(N))")
    print(f"Efficiency ratio range: {min(ratio_trend):.0f}:1 - {max(ratio_trend):.0f}:1")
    print()
    print("Their work / Our seed:")
    for r in results:
        bar = "█" * min(50, int(r['ratio'] / 10))
        print(f"  {r['pool']:>10,}: {r['ratio']:>6.0f}:1 {bar}")
    
    return results


if __name__ == '__main__':
    import sys
    max_pool = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    compare(max_pool, trials)
