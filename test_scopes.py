from pathlib import Path
import os
import shutil
import tempfile
import unittest
from scopes import get_scope_for_file

class TestScopes(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.test_dir)

    def create_structure(self, paths):
        for path in paths:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.touch()

    def test_readme_root(self):
        self.create_structure(["README.md"])
        self.assertEqual(get_scope_for_file("README.md"), "README")

    def test_docs(self):
        self.create_structure(["docs/setup.md", "docs/api/index.md"])
        self.assertEqual(get_scope_for_file("docs/setup.md"), "docs/setup")
        self.assertEqual(get_scope_for_file("docs/api/index.md"), "docs/index")

    def test_infra(self):
        self.create_structure(["pyproject.toml", ".gitignore"])
        self.assertEqual(get_scope_for_file("pyproject.toml"), "infra/pyproject.toml")
        self.assertEqual(get_scope_for_file(".gitignore"), "infra/.gitignore")

    def test_branching_heuristic(self):
        # repo/frontend/src/app/index.ts where frontend/ only has src/
        # but src/ has app/ and assets/ (branching point)
        self.create_structure([
            "frontend/src/app/index.ts",
            "frontend/src/assets/logo.png"
        ])
        # Expected: frontend (root) / src (branching) / app (leaf parent)
        self.assertEqual(get_scope_for_file("frontend/src/app/index.ts"), "frontend/src/app")

    def test_single_child_collapse(self):
        # repo/frontend/src/app/index.ts where all have 1 child except root
        self.create_structure([
            "frontend/src/app/index.ts"
        ])
        # Expected: frontend (root) / app (leaf parent) - src is collapsed
        self.assertEqual(get_scope_for_file("frontend/src/app/index.ts"), "frontend/app")

    def test_blacklist(self):
        self.create_structure(["project/src/main.py", "project/src/utils.py"])
        # src is blacklisted, so it should be skipped even if branching
        self.assertEqual(get_scope_for_file("project/src/main.py"), "project")

if __name__ == "__main__":
    unittest.main()
