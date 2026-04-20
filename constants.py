# Written by Luis Felipe Montemayor, sometime around December of 2025

COMMIT_TYPES: list[str] = ["feat", "fix", "refactor", "test", "chore", "docs"]

INFRA_FILES: set[str] = {
    "pyproject.toml",
    "uv.lock",
    "ruff.toml",
    ".gitattributes",
    ".gitignore",
    "lazygit.yml",
    "LICENSE",
    "README.md",
}

INFRA_DIRS: set[str] = {".git", ".vscode", ".config/mise/conf.d/"}

# Directories to skip in the scope path (e.g., generic containers)
BLACKLIST: set[str] = {
    "src",
    "lib",
    "include",
    "bin",
    "node_modules",
    "venv",
    ".venv",
}

# Directories to always treat as significant scope roots
WHITELIST: set[str] = {
    "common",
    "docs",
    "infra",
    "scripts",
    "tests",
}

INFRA_PREFIX: str = "infra"

# Map glob patterns to scope strings. Support {stem} replacement.
# Examples: 
#   "web/app/*.ts": "frontend/{stem}"
#   "api/v1/users.py": "api/users"
MAPPINGS: dict[str, str] = {}

NO_SCOPE_STR = "None"
NOTHING_STAGED_STR = "Nothing Staged"
