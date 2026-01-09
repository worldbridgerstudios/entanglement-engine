#!/usr/bin/env python3
"""
Overnight scaling test for Entanglement Engine.

Usage:
    python3 run_scaling_test.py
    python3 run_scaling_test.py --max-pool 100000 --trials 10
    python3 run_scaling_test.py --output results.json
    
    nohup python3 run_scaling_test.py --max-pool 1000000 > scaling.log 2>&1 &
"""

import argparse
import json
import time
from datetime import datetime
from fault_tolerance import test_fault_tolerance
from entanglement_engine import entanglement_params


def run_scaling_test(max_pool: int = 100000, trials: int = 5, 
                     output: str = None, verbose: bool = True):
    """
    Run scaling test across pool sizes.
    
    Tests: 50, 100, 200, 500, 1K, 2K, 5K, 10K, 20K, 50K, 100K, ...
    """
    # Generate test points: geometric progression
    pool_sizes = []
    base_points = [50, 100, 200, 500]
    multiplier = 1
    
    while True:
        for bp in base_points:
            size = bp * multiplier
            if size <= max_pool:
                pool_sizes.append(size)
            else:
                break
        if base_points[0] * multiplier > max_pool:
            break
        multiplier *= 10
    
    pool_sizes = sorted(set(pool_sizes))
    
    print("=" * 70)
    print("ENTANGLEMENT ENGINE — SCALING TEST")
    print("=" * 70)
    print(f"Started:    {datetime.now().isoformat()}")
    print(f"Max pool:   {max_pool:,}")
    print(f"Trials:     {trials}")
    print(f"Test sizes: {len(pool_sizes)}")
    print("=" * 70)
    print()
    
    results = []
    start_time = time.time()
    
    for i, pool in enumerate(pool_sizes):
        print(f"[{i+1}/{len(pool_sizes)}] Pool {pool:>10,}...", flush=True)
        
        t0 = time.time()
        r = test_fault_tolerance(pool, trials=trials, verbose=False)
        elapsed = time.time() - t0
        
        r['test_time_sec'] = elapsed
        results.append(r)
        
        status = "✓" if r['success_rate'] == 1.0 else "✗"
        print(f"    {status} K={r['K']}, V={r['V']:>4}, "
              f"steps={r['avg_steps']:>5.1f} ({r['min_steps']}-{r['max_steps']}), "
              f"coh={r['avg_coherence']:.3f}, "
              f"success={r['success_rate']*100:.0f}%, "
              f"time={elapsed:.1f}s")
        
        # Save intermediate results
        if output:
            with open(output, 'w') as f:
                json.dump({
                    'started': datetime.now().isoformat(),
                    'max_pool': max_pool,
                    'trials': trials,
                    'completed': len(results),
                    'total': len(pool_sizes),
                    'results': results
                }, f, indent=2)
    
    total_time = time.time() - start_time
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Completed:  {datetime.now().isoformat()}")
    print(f"Duration:   {total_time/3600:.2f} hours")
    print(f"Tests run:  {len(results)}")
    
    # Success analysis
    failures = [r for r in results if r['success_rate'] < 1.0]
    if failures:
        print(f"Failures:   {len(failures)}")
        for f in failures:
            print(f"  - Pool {f['pool']:,}: {f['success_rate']*100:.0f}% success")
    else:
        print(f"Failures:   0 (100% success across all scales)")
    
    # Step trend
    print()
    print("Step trend:")
    for r in results:
        bar = "█" * int(r['avg_steps'] / 2)
        print(f"  {r['pool']:>10,}: {r['avg_steps']:>5.1f} {bar}")
    
    # Save final results
    if output:
        with open(output, 'w') as f:
            json.dump({
                'started': results[0].get('started', ''),
                'completed': datetime.now().isoformat(),
                'duration_hours': total_time / 3600,
                'max_pool': max_pool,
                'trials': trials,
                'total_tests': len(results),
                'all_passed': len(failures) == 0,
                'results': results
            }, f, indent=2)
        print(f"\nResults saved to: {output}")
    
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Entanglement Engine scaling test')
    parser.add_argument('--max-pool', type=int, default=100000,
                        help='Maximum pool size to test (default: 100000)')
    parser.add_argument('--trials', type=int, default=5,
                        help='Trials per pool size (default: 5)')
    parser.add_argument('--output', '-o', type=str, default='scaling_results.json',
                        help='Output JSON file (default: scaling_results.json)')
    
    args = parser.parse_args()
    
    run_scaling_test(
        max_pool=args.max_pool,
        trials=args.trials,
        output=args.output
    )
