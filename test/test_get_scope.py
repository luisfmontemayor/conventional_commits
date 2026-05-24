import unittest
from unittest.mock import patch, MagicMock
import io
import sys
from pathlib import Path

# Add parent directory to path so we can import get_scope and scopes
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# We'll import get_scope inside test methods or after mocking if needed,
# but let's assume we can import it.
import get_scope

class TestGetScope(unittest.TestCase):

    @patch('scopes.get_staged_scopes')
    def test_default_output_with_staged_scope(self, mock_get_staged_scopes):
        # get_staged_scopes returns formatted scopes like ["(backend/api)", "(frontend)", ""]
        mock_get_staged_scopes.return_value = ["(backend/api)", "(frontend)", ""]
        
        stdout = io.StringIO()
        with patch('sys.stdout', stdout):
            get_scope.main([])
            
        self.assertEqual(stdout.getvalue().strip(), "backend/api")

    @patch('scopes.get_staged_scopes')
    def test_default_output_no_scope(self, mock_get_staged_scopes):
        # Empty string in get_staged_scopes represents NO_SCOPE_STR (None)
        mock_get_staged_scopes.return_value = [""]
        
        stdout = io.StringIO()
        with patch('sys.stdout', stdout):
            get_scope.main([])
            
        self.assertEqual(stdout.getvalue().strip(), "None")

    @patch('scopes.get_staged_scopes')
    def test_json_output(self, mock_get_staged_scopes):
        mock_get_staged_scopes.return_value = ["(backend/api)", "(frontend)", ""]
        
        stdout = io.StringIO()
        with patch('sys.stdout', stdout):
            get_scope.main(["--json"])
            
        import json
        data = json.loads(stdout.getvalue().strip())
        self.assertEqual(data["primary"], "backend/api")
        self.assertEqual(data["alternatives"], ["backend/api", "frontend", "None"])

    @patch('scopes.get_staged_scopes')
    def test_commit_type_prefix(self, mock_get_staged_scopes):
        mock_get_staged_scopes.return_value = ["(backend/api)"]
        
        stdout = io.StringIO()
        with patch('sys.stdout', stdout):
            get_scope.main(["--commit-type", "feat"])
            
        self.assertEqual(stdout.getvalue(), "feat(backend/api): \n")

    @patch('scopes.get_staged_scopes')
    def test_commit_type_prefix_no_scope(self, mock_get_staged_scopes):
        mock_get_staged_scopes.return_value = [""]
        
        stdout = io.StringIO()
        with patch('sys.stdout', stdout):
            get_scope.main(["--commit-type", "feat"])
            
        self.assertEqual(stdout.getvalue(), "feat: \n")

    @patch('scopes.get_staged_scopes')
    def test_commit_type_json(self, mock_get_staged_scopes):
        mock_get_staged_scopes.return_value = ["(backend/api)", ""]
        
        stdout = io.StringIO()
        with patch('sys.stdout', stdout):
            get_scope.main(["--commit-type", "fix", "--json"])
            
        import json
        data = json.loads(stdout.getvalue().strip())
        self.assertEqual(data["prefix"], "fix(backend/api): ")
        self.assertEqual(data["primary"], "backend/api")
        self.assertEqual(data["alternatives"], ["backend/api", "None"])

    def test_invalid_commit_type(self):
        stderr = io.StringIO()
        with patch('sys.stderr', stderr), self.assertRaises(SystemExit) as cm:
            get_scope.main(["--commit-type", "invalid-type"])
            
        self.assertNotEqual(cm.exception.code, 0)
        self.assertIn("invalid-type", stderr.getvalue())

if __name__ == '__main__':
    unittest.main()
