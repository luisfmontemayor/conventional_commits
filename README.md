# Conventional Commits Wizard

A lightweight, filesystem-aware tool for generating Conventional Commits. It supports both a standalone interactive CLI and a deep integration with Lazygit.

## Features

- Filesystem-aware scope generation using a branching heuristic.
- Automatic identification of docs, README, and infrastructural changes.
- Dual mode: Interactive CLI (via gum) or Lazygit custom command.
- Zero non-standard dependencies (standard Python 3.10+).

## Installation

### Prerequisites

- Python 3.10 or higher.
- gum (optional, required for standalone CLI mode).

### Manual Setup

1. Copy the contents of this repository into your project (e.g., under a `scripts/` directory).
2. Ensure the `common/` directory is present in the same folder as the main scripts.

### Lazygit Integration

To integrate the wizard into Lazygit:

1. Run the setup script:
   ```bash
   bash lazygit_wizard_setup.sh
   ```
2. This will copy the necessary logic to your `.git/` folder and create a `.git/lazygit.yml` configuration.
3. In Lazygit, you can now press `W` to start the wizard.

## Usage

### Standalone CLI

The wizard operates in **non-interactive mode** by default. It automatically selects the most likely scope based on staged files. You must provide the commit type and message as positional arguments:

```bash
python3 __main__.py feat "add new login logic"
```

To run the wizard in **interactive mode** (which prompts you to select the type, scope, and message using `gum`), use the `-i` flag:

```bash
python3 __main__.py -i
```

You can also view the help menu:

```bash
python3 __main__.py -h

# usage: __main__.py [-h] [-i] ...
# 
# Conventional Commits Wizard
# 
# positional arguments:
#   args               [type] [message...]
# 
# options:
#   -h, --help         show this help message and exit
#   -i, --interactive  Interactive mode
```

### Lazygit

Press `W` from any context in Lazygit. You will be prompted to:
1. Select a commit type (feat, fix, etc.).
2. Select a scope (dynamically generated based on staged files).
3. Enter a commit message.

## Commit Format

The wizard generates messages following the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```text
<type>(<scope>): <message>
```

If the scope is "None", the wizard automatically omits the parentheses:

```text
<type>: <message>
```

## Examples

The following examples illustrate how the branching heuristic and special rules map file changes to scopes:

| File Changed | Generated Scope | Resulting Commit Example |
| :--- | :--- | :--- |
| `README.md` (root) | `README` | `docs(README): update installation steps` |
| `docs/setup.md` | `docs/setup` | `docs(docs/setup): add api keys section` |
| `pyproject.toml` | `infra/pyproject.toml` | `chore(infra/pyproject.toml): bump version` |
| `common/cli.py` | `common` | `refactor(common): optimize gum input` |
| `frontend/src/app/auth/login.ts` | `frontend/auth` | `feat(frontend/auth): add oauth support` |
| `backend/api/routes.py` | `backend/api` | `fix(backend/api): fix cors headers` |
| Multiple (e.g., `frontend/`, `backend/`) | `backend,frontend` | `feat(backend,frontend): sync auth state` |

*Note: In the `frontend` example, if `src` and `app` only contain one child, they are collapsed to keep the scope concise.*

## Scope Generation Logic

The wizard uses a "Branching Heuristic" to determine meaningful scopes. It avoids deep, uninformative paths (like `src/main/app/`) by following these rules:

1. Combined Roots: If staged files span multiple top-level directories (e.g., changing both `frontend` and `backend`), a comma-separated root scope (e.g., `frontend,backend`) is added as a menu option.
2. Branching Points: A directory is included in the scope if it contains two or more children (files or subdirectories) in the filesystem.
2. Leaf Parent: The immediate parent directory of a changed file is always included.
3. Root Retention: The top-level directory of a module is always included.
4. Blacklist: Common generic containers (e.g., `src`, `lib`, `node_modules`) are skipped unless they are leaf parents.
5. Special Cases: 
   - Root `README.md` is scoped as `README`.
   - Files in `docs/` are scoped as `docs/<filename>`.
   - Configuration files (e.g., `.gitignore`, `pyproject.toml`) are scoped as `infra/<filename>`.

## Configuration

You can customize the behavior by editing `constants.py`:

- BLACKLIST: Directories to always skip in the scope path.
- WHITELIST: Directories to always treat as significant scope roots.
- INFRA_FILES / INFRA_DIRS: Files and folders to be categorized under the `infra` scope.
