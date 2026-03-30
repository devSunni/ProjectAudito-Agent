import unittest
import os
import json
import shutil
import tempfile
from pathlib import Path
from auditor import ProjectAuditorPro

class TestProjectAuditorPro(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory structure for testing
        self.test_dir = tempfile.mkdtemp()
        self.root = Path(self.test_dir)
        
        # Create dummy source and test files
        (self.root / "src").mkdir()
        (self.root / "tests").mkdir()
        
        (self.root / "src" / "main.py").write_text("print('hello')")
        (self.root / "src" / "utils.py").write_text("def add(a, b): return a + b")
        (self.root / "tests" / "test_main.py").write_text("import main")
        
        # No test for utils.py -> should be identified as a gap

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_load_config_default(self):
        auditor = ProjectAuditorPro(self.test_dir)
        self.assertEqual(auditor.config["extensions"], [".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs"])

    def test_find_source_files(self):
        auditor = ProjectAuditorPro(self.test_dir)
        sources = auditor.find_source_files()
        source_names = [s.name for s in sources]
        self.assertIn("main.py", source_names)
        self.assertIn("utils.py", source_names)
        self.assertEqual(len(sources), 2)

    def test_find_test_files(self):
        auditor = ProjectAuditorPro(self.test_dir)
        tests = auditor.find_test_files()
        self.assertEqual(len(tests), 1)
        self.assertEqual(tests[0].name, "test_main.py")

    def test_analyze_gaps(self):
        auditor = ProjectAuditorPro(self.test_dir)
        sources, tests, missing = auditor.analyze_gaps()
        
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0].name, "utils.py")

    def test_custom_config(self):
        config = {
            "extensions": [".js"],
            "source_dirs": ["lib"],
            "test_dirs": ["__tests__"]
        }
        config_path = self.root / ".auditor.json"
        with open(config_path, "w") as f:
            json.dump(config, f)
            
        (self.root / "lib").mkdir()
        (self.root / "lib" / "index.js").write_text("console.log('test')")
        
        auditor = ProjectAuditorPro(self.test_dir)
        sources = auditor.find_source_files()
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].name, "index.js")

if __name__ == "__main__":
    unittest.main()
