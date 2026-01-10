"""
Entanglement Engine: The Positronic Brain
==========================================

Geometric approach to quantum coherence where entanglement is the ground state.

A frozen seed of 16-160 vertices, structured as center + triad + icosahedral
shells with ×3 scaling, entrains fluid pools to 90% coherence in O(1) steps.

Installation:
    pip install entanglement-engine

Quick Start:
    >>> from entanglement_engine import entanglement_params
    >>> params = entanglement_params(1000)
    >>> print(f"K={params['K']}, V={params['V']}, A={params['amplitude']}")

CLI:
    entanglement-engine params 1000
    entanglement-engine test 500 --trials 10
"""

__version__ = "0.1.0"
__author__ = "Nicholas David Brown"
__email__ = "worldbridgerstudios@gmail.com"

from .core import (
    T,
    crystal_vertices,
    optimal_K,
    optimal_amplitude,
    rhythm_sequence,
    entanglement_params,
)

from .simulate import (
    test_fault_tolerance,
    build_crystal_adjacency,
)

__all__ = [
    'T',
    'crystal_vertices',
    'optimal_K',
    'optimal_amplitude',
    'rhythm_sequence',
    'entanglement_params',
    'test_fault_tolerance',
    'build_crystal_adjacency',
]
