import os
import json
import argparse
import logging
import fnmatch
from typing import List, Dict, Set, Any
from pathlib import Path

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ProjectAuditorPro")

DEFAULT_CONFIG = {
    "extensions": [".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs"],
    "source_dirs": ["src", "app", "lib", "core", "pkg"],
    "test_dirs": ["tests", "__tests__", "test", "spec"],
    "test_prefix": "test_",
    "test_suffixes": ["_test", ".test", ".spec"],
    "exclude_dirs": [".git", "node_modules", "__pycache__", ".venv", ".next", "dist", "build", "vendor"],
    "report_file": "audit_report.md"
}

class ProjectAuditorPro:
    def __init__(self, root_dir: str, config_path: str = None):
        self.root_dir = Path(root_dir).resolve()
        self.config = self._load_config(config_path)
        self.gitignore_patterns = self._load_gitignore()
        self.report_path = self.root_dir / self.config.get("report_file", "audit_report.md")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        config = DEFAULT_CONFIG.copy()
        if not config_path:
            config_path = self.root_dir / ".auditor.json"
        
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                    config.update(user_config)
                logger.debug(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.error(f"Failed to load config: {e}. Using defaults.")
        return config

    def _load_gitignore(self) -> List[str]:
        patterns = []
        gitignore_path = self.root_dir / ".gitignore"
        if gitignore_path.exists():
            try:
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            patterns.append(line)
                logger.info(f"Loaded {len(patterns)} patterns from .gitignore")
            except Exception as e:
                logger.error(f"Failed to read .gitignore: {e}")
        return patterns

    def _should_exclude(self, path: Path) -> bool:
        # Check built-in exclude dirs
        if any(part in self.config["exclude_dirs"] for part in path.parts):
            return True
        
        # Check .gitignore patterns
        rel_path = str(path.relative_to(self.root_dir)).replace("\\", "/")
        for pattern in self.gitignore_patterns:
            # Simple fnmatch check. For more complex gitignore logic, a dedicated library is better.
            # But we aim for zero-dependency.
            if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(path.name, pattern):
                return True
            if pattern.endswith("/") and any(fnmatch.fnmatch(part, pattern.rstrip("/")) for part in path.parts):
                return True
        return False

    def find_source_files(self) -> List[Path]:
        source_files = []
        extensions = set(self.config["extensions"])
        
        potential_src_dirs = [self.root_dir / d for d in self.config["source_dirs"] if (self.root_dir / d).is_dir()]
        search_roots = potential_src_dirs if potential_src_dirs else [self.root_dir]

        for root in search_roots:
            for path in root.rglob("*"):
                if path.is_file() and path.suffix in extensions:
                    if not self._should_exclude(path) and not self._is_test_file(path):
                        source_files.append(path)
        return source_files

    def find_test_files(self) -> List[Path]:
        test_files = []
        extensions = set(self.config["extensions"])
        
        potential_test_dirs = [self.root_dir / d for d in self.config["test_dirs"] if (self.root_dir / d).is_dir()]
        search_roots = potential_test_dirs if potential_test_dirs else [self.root_dir]

        for root in search_roots:
            for path in root.rglob("*"):
                if path.is_file() and path.suffix in extensions:
                    if not self._should_exclude(path) and self._is_test_file(path):
                        test_files.append(path)
        return test_files

    def _is_test_file(self, path: Path) -> bool:
        name = path.name
        stem = path.stem
        if name.startswith(self.config["test_prefix"]):
            return True
        for suffix in self.config["test_suffixes"]:
            if stem.endswith(suffix) or name.endswith(f"{suffix}{path.suffix}"):
                return True
        if any(part in self.config["test_dirs"] for part in path.parts):
            return True
        return False

    def analyze_gaps(self):
        sources = self.find_source_files()
        tests = self.find_test_files()
        test_names = {t.name for t in tests}
        test_stems = {t.stem for t in tests}

        missing = []
        for src in sources:
            found = False
            test_variants = [
                f"{self.config['test_prefix']}{src.name}",
                f"{src.stem}{self.config['test_suffixes'][0]}{src.suffix}" if self.config['test_suffixes'] else None,
                f"{src.stem}.test{src.suffix}",
                f"{src.stem}.spec{src.suffix}"
            ]
            
            for variant in filter(None, test_variants):
                if variant in test_names:
                    found = True
                    break
            
            if not found:
                stem_match = f"{self.config['test_prefix']}{src.stem}"
                if stem_match in test_stems:
                    found = True

            if not found:
                missing.append(src)

        return sources, tests, missing

    def _generate_tree(self) -> str:
        """Generates a tree-like string of the project structure excluding ignored files."""
        tree_lines = ["```text"]
        
        def _build_tree(directory: Path, prefix: str = ""):
            items = sorted([item for item in directory.iterdir() if not self._should_exclude(item)], key=lambda x: (not x.is_dir(), x.name))
            for i, item in enumerate(items):
                is_last = (i == len(items) - 1)
                connector = "└── " if is_last else "├── "
                tree_lines.append(f"{prefix}{connector}{item.name}")
                if item.is_dir():
                    _build_tree(item, prefix + ("    " if is_last else "│   "))

        tree_lines.append(self.root_dir.name)
        _build_tree(self.root_dir)
        tree_lines.append("```")
        return "\n".join(tree_lines)

    def update_readme_structure(self):
        readme_path = self.root_dir / "README.md"
        if not readme_path.exists():
            logger.warning("README.md not found in root. Skipping update.")
            return

        tree_str = self._generate_tree()
        marker_start = "<!-- AUDITOR_STRUCTURE_START -->"
        marker_end = "<!-- AUDITOR_STRUCTURE_END -->"

        try:
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()

            if marker_start in content and marker_end in content:
                new_content = content.split(marker_start)[0] + \
                              marker_start + "\n" + tree_str + "\n" + \
                              marker_end + content.split(marker_end)[1]
                with open(readme_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                logger.info("Successfully updated README.md project structure section.")
            else:
                logger.warning(f"Could not find markers '{marker_start}' and '{marker_end}' in README.md. Please add them.")
        except Exception as e:
            logger.error(f"Failed to update README.md: {e}")

    def fix_missing_tests(self):
        _, _, missing = self.analyze_gaps()
        if not missing:
            logger.info("No missing tests found. Nothing to fix.")
            return

        logger.info(f"Generating test scaffolding for {len(missing)} files...")
        
        # Templates per extension
        templates = {
            ".py": "import unittest\n\nclass Test{ClassName}(unittest.TestCase):\n    def test_example(self):\n        self.assertTrue(True)\n\nif __name__ == '__main__':\n    unittest.main()",
            ".js": "describe('{FileName}', () => {{\n  it('should work', () => {{\n    expect(true).toBe(true);\n  }});\n}});",
            ".ts": "describe('{FileName}', () => {{\n  it('should work', () => {{\n    expect(true).toBe(true);\n  }});\n}});",
            ".go": "package {PkgName}\n\nimport \"testing\"\n\nfunc TestExample(t *testing.T) {{\n    // TODO: implement\n}}"
        }

        test_root = self.root_dir / self.config["test_dirs"][0]
        if not test_root.exists():
            test_root.mkdir(parents=True)
            logger.info(f"Created test directory: {test_root}")

        for m in missing:
            ext = m.suffix
            if ext not in templates:
                logger.warning(f"No template for extension {ext}. Skipping {m.name}.")
                continue

            # Determine target test path
            # Simple approach: same relative path under test_root
            try:
                rel_base = m.relative_to(self.root_dir)
                # Remove common source dirs from relative path to flatten or map to tests
                for src_dir in self.config["source_dirs"]:
                    if str(rel_base).startswith(src_dir):
                        rel_base = Path(*rel_base.parts[1:])
                        break
                
                test_file_path = test_root / f"{self.config['test_prefix']}{rel_base.stem}{ext}"
                if not test_file_path.parent.exists():
                    test_file_path.parent.mkdir(parents=True)

                if test_file_path.exists():
                    logger.debug(f"Test file already exists: {test_file_path}. Skipping.")
                    continue

                # Prepare template
                class_name = m.stem.capitalize().replace("_", "")
                content = templates[ext].format(
                    ClassName=class_name,
                    FileName=m.stem,
                    PkgName="main" # simplistic for Go
                )

                with open(test_file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                logger.info(f"Generated: {test_file_path.relative_to(self.root_dir)}")

            except Exception as e:
                logger.error(f"Failed to generate test for {m}: {e}")

    def generate_report(self):
        sources, tests, missing = self.analyze_gaps()
        coverage_pct = (1 - len(missing) / len(sources)) * 100 if sources else 100

        report_lines = [
            "# Project Audit Pro: Report",
            f"Generated on: {Path('.').resolve().name}",
            "",
            "## Summary",
            f"- **Root Directory**: `{self.root_dir}`",
            f"- **Total Source Files**: {len(sources)}",
            f"- **Total Test Files**: {len(tests)}",
            f"- **Test Coverage (File-level)**: {coverage_pct:.2f}%",
            "",
        ]

        if missing:
            report_lines.extend([
                "## Test Coverage Gaps",
                "The following source files do not have matching test files:",
                ""
            ])
            for m in sorted(missing):
                try:
                    rel_path = m.relative_to(self.root_dir)
                except ValueError:
                    rel_path = m
                report_lines.append(f"- [ ] `{rel_path}`")
            
            report_lines.extend([
                "",
                "### 💡 Tip",
                "Run `py -m auditor --fix-tests` to automatically generate skeleton test files for these gaps."
            ])
        else:
            report_lines.append("## ✅ All files have matching tests!")

        report_lines.extend([
            "",
            "## Project Structure",
            "Detected Source Directories: " + ", ".join([d for d in self.config["source_dirs"] if (self.root_dir / d).is_dir()]) or "Root",
            "Detected Test Directories: " + ", ".join([d for d in self.config["test_dirs"] if (self.root_dir / d).is_dir()]) or "None Found",
            "",
            "---",
            "*Generated by Project Auditor Pro Agent*"
        ])

        with open(self.report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))
        
        print("\n" + "\n".join(report_lines[:15]))
        print(f"\nFull report saved to: {self.report_path}")

def main():
    parser = argparse.ArgumentParser(description="Professional Universal Project Auditor")
    parser.add_argument("--root", default=".", help="Project root directory")
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--update-readme", action="store_true", help="Update project structure in README.md")
    parser.add_argument("--fix-tests", action="store_true", help="Generate missing test skeletons")
    args = parser.parse_args()

    auditor = ProjectAuditorPro(args.root, args.config)
    
    if args.update_readme:
        auditor.update_readme_structure()
    
    if args.fix_tests:
        auditor.fix_missing_tests()
    
    # Always generate report if no specific action or along with actions
    auditor.generate_report()

if __name__ == "__main__":
    main()
