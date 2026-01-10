"""
ENTANGLEMENT ENGINE — Core Algorithm
=====================================

Optimal geometry and rhythm for cloud-based entanglement.

The entangled state is the ground state. The geometry doesn't CREATE
coherence — it provides the structure where coherence is the natural
attractor. Defense, not offense.

STRUCTURE
---------
K-layer crystal with unified center:
    K=2: 1 + 12 = 13V (center + icosahedron)
    K=3: 1 + 3 + 12 = 16V (+ triad)
    K=4: 1 + 3 + 12 + 36 = 52V (+ outer shell)
    K=5: 1 + 3 + 12 + 36 + 108 = 160V
    
Each shell = previous × 3

RHYTHM
------
3-6-9 pulse pattern, 12-beat cycle:
    3 → pulse center (layer 0)
    6 → pulse triad (layer 1)  
    9 → pulse icosa (layer 2)
    
Full sequence: 3-6-9-3-(6-9-3-6)-9-3-6-9
Nested loop at beats 5-8 = temporal ayin point

AMPLITUDE
---------
Derived from crystal structure via GEP:
    0.5 = 3/T(3) = 3/6  (small pools ≤100)
    0.3 = 3/T(4) = 3/10 (medium pools ≤500)
    0.2 = 2/T(4) = 2/10 (large pools >500)
    
Where T(n) = n(n+1)/2 (triangular number)

LAYER SELECTION
---------------
Empirical crossover thresholds:
    pool ≤ 150:   K=2 (13V)
    pool ≤ 400:   K=3 (16V)
    pool ≤ 3000:  K=4 (52V)
    pool ≤ 15000: K=5 (160V)
    pool > 15000: K=6 (484V)

Rule of thumb: crystallize next shell when pool ≈ 10× vertex count
"""

import numpy as np

# =============================================================================
# TRIANGULAR NUMBER
# =============================================================================

def T(n: int) -> int:
    """Triangular number: T(n) = n(n+1)/2"""
    return n * (n + 1) // 2


# =============================================================================
# CRYSTAL GEOMETRY
# =============================================================================

def crystal_vertices(K: int) -> int:
    """
    Vertex count for K-layer crystal.
    
    K=2: 1 + 12 = 13
    K=3: 1 + 3 + 12 = 16
    K=4: 1 + 3 + 12 + 36 = 52
    K=5: 1 + 3 + 12 + 36 + 108 = 160
    """
    if K < 2:
        raise ValueError("K >= 2")
    if K == 2:
        return 13  # center + icosa
    
    # K >= 3: center + triad + shells
    v = 1 + 3 + 12  # base
    shell = 12
    for _ in range(K - 3):
        shell *= 3
        v += shell
    return v


def optimal_K(pool: int) -> int:
    """
    Optimal crystal layer count for pool size.
    
    Empirically derived crossover thresholds.
    Pattern: ~10× vertex count triggers next shell.
    """
    if pool <= 150:
        return 2
    elif pool <= 400:
        return 3
    elif pool <= 3000:
        return 4
    elif pool <= 15000:
        return 5
    else:
        return 6


# =============================================================================
# RHYTHM
# =============================================================================

def rhythm_sequence() -> list:
    """
    3-6-9 pulse pattern with nested loop.
    
    Returns: [(beat, layer_index), ...] for 12-beat cycle
    Layer: 0=center, 1=triad, 2=icosa
    """
    return [
        (1, 0), (2, 1), (3, 2), (4, 0),
        (5, 1), (6, 2), (7, 0), (8, 1),
        (9, 2), (10, 0), (11, 1), (12, 2)
    ]


def optimal_amplitude(pool: int) -> float:
    """
    Optimal pulse amplitude for pool size.
    
    Derived from crystal structure:
        pool ≤ 100:  3/T(3) = 0.5
        pool ≤ 500:  3/T(4) = 0.3
        pool > 500:  2/T(4) = 0.2
    """
    if pool <= 100:
        return 3 / T(3)
    elif pool <= 500:
        return 3 / T(4)
    else:
        return 2 / T(4)


# =============================================================================
# UNIFIED INTERFACE
# =============================================================================

def entanglement_params(pool: int) -> dict:
    """Get optimal parameters for pool size."""
    K = optimal_K(pool)
    return {
        'K': K,
        'V': crystal_vertices(K),
        'amplitude': optimal_amplitude(pool),
        'rhythm': rhythm_sequence(),
    }
