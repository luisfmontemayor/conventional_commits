#!/usr/bin/env python3
# Written by Luis Felipe Montemayor, sometime around December of 2025
import os
import sys
from pathlib import Path

# Add the script directory to sys.path so we can import from the package
script_dir = Path(__file__).resolve().parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

import scopes

if __name__ == "__main__":
    for scope in scopes.get_staged_scopes():
        print(scope)
