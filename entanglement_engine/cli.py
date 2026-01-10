"""
CLI for Entanglement Engine.
"""

import argparse
import json
from .core import entanglement_params, crystal_vertices
from .simulate import test_fault_tolerance


def main():
    parser = argparse.ArgumentParser(
        description='Entanglement Engine: Geometric quantum coherence'
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # params command
    p_params = subparsers.add_parser('params', help='Get optimal parameters for pool size')
    p_params.add_argument('pool', type=int, help='Pool size')
    p_params.add_argument('--json', action='store_true', help='Output as JSON')

    # test command
    p_test = subparsers.add_parser('test', help='Test fault tolerance')
    p_test.add_argument('pool', type=int, help='Pool size')
    p_test.add_argument('--trials', type=int, default=5, help='Number of trials')
    p_test.add_argument('--corruption', type=float, default=0.5, help='Corruption fraction')
    p_test.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    p_test.add_argument('--json', action='store_true', help='Output as JSON')

    # crystal command
    p_crystal = subparsers.add_parser('crystal', help='Crystal vertex counts')
    p_crystal.add_argument('--max-k', type=int, default=6, help='Maximum K value')

    args = parser.parse_args()

    if args.command == 'params':
        params = entanglement_params(args.pool)
        if args.json:
            params['rhythm'] = [(b, l) for b, l in params['rhythm']]
            print(json.dumps(params, indent=2))
        else:
            print(f"Pool size: {args.pool}")
            print(f"  K (layers): {params['K']}")
            print(f"  V (vertices): {params['V']}")
            print(f"  Amplitude: {params['amplitude']:.3f}")

    elif args.command == 'test':
        print(f"Testing fault tolerance: pool={args.pool}, corruption={args.corruption}")
        result = test_fault_tolerance(
            args.pool,
            corruption=args.corruption,
            trials=args.trials,
            verbose=args.verbose
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\nResults:")
            print(f"  Crystal: K={result['K']}, V={result['V']}")
            print(f"  Amplitude: {result['amplitude']:.3f}")
            print(f"  Success rate: {result['success_rate']*100:.0f}%")
            print(f"  Avg steps: {result['avg_steps']:.1f}")
            print(f"  Avg coherence: {result['avg_coherence']:.3f}")

    elif args.command == 'crystal':
        print("Crystal vertex counts:")
        for k in range(2, args.max_k + 1):
            print(f"  K={k}: {crystal_vertices(k)} vertices")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
