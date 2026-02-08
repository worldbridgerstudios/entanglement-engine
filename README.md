# Entanglement Engine

Optimal geometry and rhythm for cloud-based quantum entanglement.

## Installation

```bash
pip install entanglement-engine
```

## Core Insight

The entangled state is the ground state. This geometry doesn't *create* coherence — it provides the structure where coherence is the natural attractor.

Defense, not offense.

## Algorithm

### Structure

K-layer crystal with unified center:
- K=2: 1 + 12 = 13V (center + icosahedron)
- K=3: 1 + 3 + 12 = 16V (+ triad)
- K=4: 1 + 3 + 12 + 36 = 52V (+ outer shell)
- K=5: 1 + 3 + 12 + 36 + 108 = 160V

Each shell = previous × 3

### Rhythm

3-6-9 pulse pattern, 12-beat cycle addressing layers by index.

### Amplitude

Derived from crystal structure via genetic expression programming:
- 0.5 = 3/T(3) = 3/6 (small pools ≤100)
- 0.3 = 3/T(4) = 3/10 (medium pools ≤500)
- 0.2 = 2/T(4) = 2/10 (large pools >500)

Where T(n) = n(n+1)/2 (triangular number)

## Usage

```python
from entanglement_engine import entanglement_params

params = entanglement_params(pool_size=1000)
# {'K': 4, 'V': 52, 'amplitude': 0.2, 'rhythm': [...]}
```

## Scaling Test

```bash
# Quick test
python3 run_scaling_test.py --max-pool 10000 --trials 3

# Overnight run
nohup python3 run_scaling_test.py --max-pool 1000000 --trials 10 > scaling.log 2>&1 &
```

## Results

Tested pool sizes 50-3000 with 50% corruption:
- 100% recovery to 90% coherence
- 12-16 steps regardless of scale
- Steps *decrease* as pool grows

## License

CC0 1.0 Universal

## Author

Nicholas David Brown  
Independent Researcher
