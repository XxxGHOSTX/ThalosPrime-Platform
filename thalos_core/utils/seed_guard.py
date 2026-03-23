"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import sys


def require_seed(argv=None) -> int:
    args = argv if argv is not None else sys.argv
    if "--seed" not in args:
        print("ERROR: --seed required")
        raise SystemExit(1)
    idx = args.index("--seed")
    if idx + 1 >= len(args):
        print("ERROR: --seed required")
        raise SystemExit(1)
    try:
        return int(args[idx + 1])
    except (ValueError, TypeError):
        print("ERROR: --seed required")
        raise SystemExit(1)
