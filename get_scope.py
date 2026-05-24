#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

# Add the script directory to sys.path to allow absolute imports
script_dir = Path(__file__).resolve().parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from constants import COMMIT_TYPES
import scopes

def unwrap_scope(scope_str: str) -> str:
    if not scope_str:
        return "None"
    if scope_str.startswith("(") and scope_str.endswith(")"):
        return scope_str[1:-1]
    return scope_str

def main(args=None):
    parser = argparse.ArgumentParser(description="Get the primary changes scope and/or prefix programmatically.")
    parser.add_argument(
        "-j", "--json",
        action="store_true",
        help="Output in JSON format."
    )
    parser.add_argument(
        "-t", "--commit-type",
        help=f"Optional commit type ({', '.join(COMMIT_TYPES)}). If provided, prints the full prefix."
    )
    
    parsed_args = parser.parse_args(args)
    
    if parsed_args.commit_type and parsed_args.commit_type not in COMMIT_TYPES:
        sys.stderr.write(
            f"Error: '{parsed_args.commit_type}' is not a valid commit type. "
            f"Valid types are: {', '.join(COMMIT_TYPES)}\n"
        )
        sys.exit(1)
        
    staged_scopes = scopes.get_staged_scopes()
    
    # Process scopes
    unwrapped_scopes = [unwrap_scope(s) for s in staged_scopes]
    
    primary_scope = unwrapped_scopes[0] if unwrapped_scopes else "None"
    alternatives = unwrapped_scopes
    
    # If the primary scope is empty/None but there are alternatives, or if we need to filter None
    # Wait, scopes.get_staged_scopes already returns unique, sorted scopes including "" at the end.
    
    prefix = None
    if parsed_args.commit_type:
        if primary_scope == "None" or not primary_scope:
            prefix = f"{parsed_args.commit_type}: "
        else:
            prefix = f"{parsed_args.commit_type}({primary_scope}): "
            
    if parsed_args.json:
        result = {
            "primary": primary_scope,
            "alternatives": alternatives
        }
        if prefix is not None:
            result["prefix"] = prefix
        print(json.dumps(result))
    else:
        if prefix is not None:
            print(prefix)
        else:
            print(primary_scope)

if __name__ == "__main__":
    main()
