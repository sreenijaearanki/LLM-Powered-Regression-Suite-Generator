"""
Code Analyzer Service - Parses diffs and analyzes code changes
"""

import re
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """Analyzes code changes from Git diffs"""

    def __init__(self):
        # Patterns match both top-level and indented (class method) definitions
        self.language_patterns = {
            "python": {
                "function": r'^\s*def\s+(\w+)\s*\(',
                "class":    r'^\s*class\s+(\w+)[\(:]',
                "import":   r'^\s*(?:from|import)\s+',
            },
            "javascript": {
                "function": r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(?.*?\)?\s*=>|(?:const|let|var)\s+(\w+)\s*=\s*function)',
                "class":    r'class\s+(\w+)',
                "import":   r'^(?:import|require)',
            },
            "typescript": {
                "function": r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(?.*?\)?\s*=>|(?:const|let|var)\s+(\w+)\s*=\s*function)',
                "class":    r'class\s+(\w+)',
                "import":   r'^(?:import|require)',
            },
            "java": {
                "function": r'(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+(\w+)\s*\(',
                "class":    r'(?:public\s+)?class\s+(\w+)',
                "import":   r'^import\s+',
            },
        }

    def analyze_changes(self, diff: str) -> Dict:
        """Analyze a unified diff and extract code changes."""
        try:
            changed_files = self._parse_diff(diff)
            changed_functions = self._extract_changed_functions(changed_files)

            # Fallback: if no functions detected, synthesize one from raw changes
            if not changed_functions:
                changed_functions = self._fallback_from_raw(changed_files)

            stats = {
                "additions": sum(len(f.get("added_lines", [])) for f in changed_files.values()),
                "deletions": sum(len(f.get("removed_lines", [])) for f in changed_files.values()),
            }

            return {
                "changed_files": changed_files,
                "changed_functions": changed_functions,
                "stats": stats,
                "total_files": len(changed_files),
            }
        except Exception as e:
            logger.error(f"Error analyzing changes: {e}")
            return {
                "changed_files": {},
                "changed_functions": [],
                "stats": {"additions": 0, "deletions": 0},
                "total_files": 0,
                "error": str(e),
            }

    def _parse_diff(self, diff: str) -> Dict:
        """Parse unified diff format into structured file data."""
        files = {}
        current_file = None

        for line in diff.split('\n'):
            if line.startswith('+++ '):
                filename = line[4:].split('\t')[0].lstrip('b/')
                if filename != '/dev/null':
                    current_file = filename
                    files[current_file] = {
                        "path": filename,
                        "added_lines": [],
                        "removed_lines": [],
                        "language": self._detect_language(filename),
                        "changes": [],
                    }
            elif line.startswith('+') and not line.startswith('+++') and current_file:
                content = line[1:]
                files[current_file]["added_lines"].append(content)
                if content.strip() and not content.strip().startswith('#'):
                    files[current_file]["changes"].append({"type": "addition", "content": content})
            elif line.startswith('-') and not line.startswith('---') and current_file:
                content = line[1:]
                files[current_file]["removed_lines"].append(content)
                if content.strip() and not content.strip().startswith('#'):
                    files[current_file]["changes"].append({"type": "deletion", "content": content})

        return files

    def _detect_language(self, filename: str) -> str:
        """Detect programming language from file extension."""
        ext_map = {
            ".py": "python", ".js": "javascript", ".ts": "typescript",
            ".tsx": "typescript", ".jsx": "javascript", ".java": "java",
            ".go": "go", ".rb": "ruby", ".cpp": "cpp", ".c": "c", ".cs": "csharp",
        }
        for ext, lang in ext_map.items():
            if filename.endswith(ext):
                return lang
        return "unknown"

    def _extract_changed_functions(self, changed_files: Dict) -> List[Dict]:
        """Extract function/method definitions from changed added lines."""
        changed_functions = []

        for filepath, file_data in changed_files.items():
            language = file_data.get("language", "unknown")
            if language not in self.language_patterns:
                continue

            patterns = self.language_patterns[language]
            added_text = '\n'.join(file_data.get("added_lines", []))
            if not added_text.strip():
                continue

            func_pattern = patterns.get("function", "")
            if func_pattern:
                for match in re.finditer(func_pattern, added_text, re.MULTILINE):
                    # Get first non-None group (handles alternation groups)
                    func_name = next((g for g in match.groups() if g), None)
                    if not func_name:
                        continue
                    ctx_start = max(0, match.start() - 200)
                    ctx_end = min(len(added_text), match.end() + 600)
                    context = added_text[ctx_start:ctx_end]
                    changed_functions.append({
                        "name": func_name,
                        "file": filepath,
                        "language": language,
                        "type": "function",
                        "code": context,
                        "parameters": self._extract_parameters(context, language),
                        "return_type": self._extract_return_type(context, language),
                    })

            class_pattern = patterns.get("class", "")
            if class_pattern:
                for match in re.finditer(class_pattern, added_text, re.MULTILINE):
                    class_name = next((g for g in match.groups() if g), None)
                    if not class_name:
                        continue
                    ctx_start = max(0, match.start() - 100)
                    ctx_end = min(len(added_text), match.end() + 400)
                    context = added_text[ctx_start:ctx_end]
                    changed_functions.append({
                        "name": class_name,
                        "file": filepath,
                        "language": language,
                        "type": "class",
                        "code": context,
                        "parameters": [],
                        "return_type": "class",
                    })

        return changed_functions

    def _fallback_from_raw(self, changed_files: Dict) -> List[Dict]:
        """
        Fallback: when no function definitions are detected (e.g. very small
        patches, config changes), synthesize a pseudo-function entry from the
        raw changed lines so the LLM still gets something to work with.
        """
        fallbacks = []
        for filepath, file_data in changed_files.items():
            added = file_data.get("added_lines", [])
            removed = file_data.get("removed_lines", [])
            if not added and not removed:
                continue

            language = file_data.get("language", "unknown")
            code = '\n'.join(added or removed)

            # Try to find any identifier to use as the name
            name_match = re.search(r'def\s+(\w+)|function\s+(\w+)|class\s+(\w+)|(\w+)\s*[=:(]', code)
            name = next((g for g in (name_match.groups() if name_match else []) if g), None)
            if not name:
                name = filepath.split('/')[-1].replace('.', '_')

            fallbacks.append({
                "name": name,
                "file": filepath,
                "language": language,
                "type": "function",
                "code": code,
                "parameters": [],
                "return_type": "unknown",
            })

        logger.info(f"Fallback: synthesized {len(fallbacks)} entries from raw diff")
        return fallbacks

    def _extract_parameters(self, code: str, language: str) -> List[str]:
        """Extract function parameters."""
        if language == "python":
            m = re.search(r'def\s+\w+\s*\((.*?)\):', code, re.DOTALL)
            if m:
                return [p.strip().split('=')[0].split(':')[0].strip()
                        for p in m.group(1).split(',') if p.strip() and p.strip() != 'self']
        elif language in ("javascript", "typescript"):
            m = re.search(r'\((.*?)\)\s*(?:=>|\{)', code, re.DOTALL)
            if m:
                return [p.strip().split('=')[0].strip()
                        for p in m.group(1).split(',') if p.strip()]
        elif language == "java":
            m = re.search(r'\w+\s*\((.*?)\)', code, re.DOTALL)
            if m:
                return [p.strip().split()[-1] for p in m.group(1).split(',') if p.strip()]
        return []

    def _extract_return_type(self, code: str, language: str) -> str:
        """Extract return type hint if available."""
        if language == "python":
            m = re.search(r'->\s*([\w\[\], ]+)', code)
            return m.group(1).strip() if m else "Any"
        elif language == "typescript":
            m = re.search(r'\)\s*:\s*([\w<>\[\] |]+)\s*(?:=>|\{)', code)
            return m.group(1).strip() if m else "any"
        elif language == "java":
            m = re.search(r'(?:public|private|protected|static|\s)+([\w<>\[\]]+)\s+\w+\s*\(', code)
            return m.group(1).strip() if m else "void"
        return "unknown"

    def get_test_coverage_recommendations(self, changed_functions: List[Dict]) -> Dict:
        """Generate test coverage recommendations based on code patterns."""
        recs = {"critical_paths": [], "edge_cases": [], "error_cases": [], "integration_tests": []}
        for func in changed_functions:
            name = func.get("name", "")
            code = func.get("code", "")
            if any(kw in code for kw in ("try", "except", "catch", "throw")):
                recs["error_cases"].append(f"Test error handling in {name}")
            if any(kw in code for kw in ("for ", "while ")):
                recs["critical_paths"].append(f"Test loop conditions in {name}")
            if "if " in code:
                recs["critical_paths"].append(f"Test all branches in {name}")
            if any(kw in code for kw in ("None", "null", "undefined")):
                recs["edge_cases"].append(f"Test None/null cases in {name}")
            if any(kw in code.lower() for kw in ("http", "request", "url")):
                recs["integration_tests"].append(f"Test HTTP integration in {name}")
        return recs
