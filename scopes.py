#!/usr/bin/env python3
# Written by Luis Felipe Montemayor, sometime around December of 2025
import os
from pathlib import Path
from typing import Set, List

from constants import (
    INFRA_DIRS,
    INFRA_FILES,
    NO_SCOPE_STR,
    NOTHING_STAGED_STR,
    BLACKLIST,
    WHITELIST,
)

def run_command(command: List[str]) -> str | None:
    import subprocess
    try:
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        return result.stdout.strip() if result.returncode == 0 else None
    except FileNotFoundError:
        return None

def get_staged_files() -> List[str]:
    output = run_command(["git", "diff", "--cached", "--name-only"])
    return output.split("\n") if output else []

def is_infra_file(path: Path) -> bool:
    return path.name in INFRA_FILES or any(d in path.parts for d in INFRA_DIRS)

def get_scope_for_file(filepath: str) -> str:
    path = Path(filepath)
    
    # Rule: README.md at root
    if path.name == "README.md" and len(path.parts) == 1:
        return "README"
    
    # Rule: Docs
    if "docs" in path.parts:
        # If it's in docs/, return docs/<filename>
        docs_index = path.parts.index("docs")
        if len(path.parts) > docs_index + 1:
            return f"docs/{path.stem}"
        return "docs"

    # Rule: Infrastructural
    if is_infra_file(path):
        return f"infra/{path.name}"

    # Tree-aware heuristic
    parts = list(path.parts)
    if not parts:
        return NO_SCOPE_STR
    
    # We want to build a scope path
    significant_parts = []
    current_path = Path(".")
    
    # Root is usually significant
    if parts:
        significant_parts.append(parts[0])
        current_path = current_path / parts[0]

    # Walk through the path parts (excluding the filename itself)
    for i in range(1, len(parts) - 1):
        part = parts[i]
        current_path = current_path / part
        
        if part in BLACKLIST:
            continue
            
        if part in WHITELIST:
            significant_parts.append(part)
            continue
            
        # Branching point heuristic: >= 2 children in filesystem
        try:
            if current_path.exists() and current_path.is_dir():
                children = list(current_path.iterdir())
                if len(children) >= 2:
                    significant_parts.append(part)
        except PermissionError:
            pass

    # Rule: Leaf parent (immediate parent of the file)
    if len(parts) > 1:
        leaf_parent = parts[-2]
        if leaf_parent not in significant_parts and leaf_parent not in BLACKLIST:
            significant_parts.append(leaf_parent)

    if not significant_parts:
        return NO_SCOPE_STR
        
    return "/".join(significant_parts)

def get_staged_scopes() -> List[str]:
    staged_files = get_staged_files()
    if not staged_files:
        return [NOTHING_STAGED_STR]

    unique_scopes: Set[str] = {get_scope_for_file(f) for f in staged_files if f.strip()}
    
    # Explode parents for menu hierarchy
    extended_scopes: Set[str] = set(unique_scopes)
    roots = set()
    for scope in list(unique_scopes):
        if scope == NO_SCOPE_STR or scope == NOTHING_STAGED_STR:
            continue
        
        # Collect top-level roots for the combined option
        root = scope.split("/")[0]
        roots.add(root)

        if scope == "README":
            continue
            
        parts = scope.split("/")
        for i in range(1, len(parts)):
            extended_scopes.add("/".join(parts[:i]))

    # If multiple roots are touched, add a combined option (e.g., "frontend,backend")
    if len(roots) > 1:
        combined_roots = ",".join(sorted(list(roots)))
        extended_scopes.add(combined_roots)

    extended_scopes.add(NO_SCOPE_STR)
    
    def scope_sort_key(s):
        is_none = (s == NO_SCOPE_STR)
        # Combined roots (containing commas) should probably come after individual roots but before None
        has_comma = "," in s
        parts = s.split("/")
        return (is_none, has_comma, parts[0], len(s), s)

    return sorted(list(extended_scopes), key=scope_sort_key)
