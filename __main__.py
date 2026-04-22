#!/usr/bin/env python3
# Written by Luis Felipe Montemayor, sometime around December of 2025
# https://youtu.be/lBueLHd2Ojw?t=1083

import argparse
import shutil
import signal
import subprocess
import sys
from pathlib import Path

# Add the current directory to sys.path to allow absolute imports when run as a script
script_dir = Path(__file__).resolve().parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from common import cli
from common.logs import setup_logger
from constants import COMMIT_TYPES, NO_SCOPE_STR
from scopes import get_staged_scopes

logger = setup_logger("commit")

git_commit_cmd = ["git", "commit", "-m"]


def signal_handler(sig, frame):
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description="Conventional Commits Wizard")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help=f"<Commit type ({', '.join(COMMIT_TYPES)})>	<commit message>",
    )

    parsed_args = parser.parse_args()

    commit_type = None
    preselected_message = ""

    if parsed_args.args:
        if parsed_args.args[0] in COMMIT_TYPES:
            commit_type = parsed_args.args[0]
            preselected_message = " ".join(parsed_args.args[1:])
        else:
            preselected_message = " ".join(parsed_args.args)

    if not commit_type:
        if not parsed_args.interactive:
            if parsed_args.args and parsed_args.args[0] not in COMMIT_TYPES:
                logger.error(f"'{parsed_args.args[0]}' is not a valid commit type. Valid types: {', '.join(COMMIT_TYPES)}")
            else:
                logger.error("Commit type is required in non-interactive mode.")
            sys.exit(1)
        commit_type = cli.gum_choose("Choose a commit type", COMMIT_TYPES)
        if not commit_type:
            sys.exit(0)

    possible_scope_choices = get_staged_scopes()
    
    if not parsed_args.interactive:
        scope = possible_scope_choices[0] if possible_scope_choices else ""
    else:
        scope = cli.gum_choose("Choose a commit scope", list(possible_scope_choices))
        if scope is None:
            sys.exit(0)

    commit_prefix = f"{commit_type}{scope}: "

    if preselected_message:
        conventional_commit_message = f"{commit_prefix} {preselected_message}"
    else:
        if not parsed_args.interactive:
            logger.error("Commit message is required in non-interactive mode.")
            sys.exit(1)
        gum_result = subprocess.run(
            [
                "gum",
                "input",
                "--placeholder",
                "Summary of changes",
                "--prompt",
                f"> {commit_prefix} ",
            ],
            text=True,
            stdout=subprocess.PIPE,  # Capture the result
            stderr=None,
        )

        if not gum_result or gum_result.returncode != 0:
            logger.error("Aborted.")
            sys.exit(1)

        conventional_commit_message = f"{commit_prefix} {gum_result.stdout.strip()}"

    _ = subprocess.run(git_commit_cmd + [conventional_commit_message])


if __name__ == "__main__":
    main()
