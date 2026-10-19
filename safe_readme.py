#!/usr/bin/env python3
"""Run the unchanged generator and publish README only after it succeeds."""
from pathlib import Path
import subprocess
import sys

from atomic_output import atomic_write

HERE = Path(__file__).parent


def main():
    try:
        result = subprocess.run([sys.executable, str(HERE / 'gen_readme.py')],
                                cwd=HERE, stdout=subprocess.PIPE, check=True)
        atomic_write(HERE / 'README.md', result.stdout)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f'UNVERIFIED README generation/publication failed: {exc}')
        return 2
    print('PASS README.md generated')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
