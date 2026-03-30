import os
import json
import argparse
import logging
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
                logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.error(f"Failed to load config: {e}. Using defaults.")
        else:
            logger.info("No config file found. Using defaults.")
        return config

    def _should_exclude(self, path: Path) -> bool:
        return any(part in self.config["exclude_dirs"] for part in path.parts)

    def find_source_files(self) -> List[Path]:
        source_files = []
        extensions = set(self.config["extensions"])
        
        # Check specific source directories first, then fallback to root if none found
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
        # Check prefix
        if name.startswith(self.config["test_prefix"]):
            return True
        # Check suffixes
        for suffix in self.config["test_suffixes"]:
            if stem.endswith(suffix) or name.endswith(f"{suffix}{path.suffix}"):
                return True
        # Check if it's inside a test directory
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
            # Possible test names
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
                # Check for logic-based match (e.g. test_login for login.py)
                stem_match = f"{self.config['test_prefix']}{src.stem}"
                if stem_match in test_stems:
                    found = True

            if not found:
                missing.append(src)

        return sources, tests, missing

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
                rel_path = m.relative_to(self.root_dir)
                report_lines.append(f"- [ ] `{rel_path}`")
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
        
        print("\n" + "\n".join(report_lines[:15])) # Show summary
        print(f"\nFull report saved to: {self.report_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Professional Universal Project Auditor")
    parser.add_argument("--root", default=".", help="Project root directory")
    parser.add_argument("--config", help="Path to config file")
    args = parser.parse_args()

    auditor = ProjectAuditorPro(args.root, args.config)
    auditor.generate_report()
