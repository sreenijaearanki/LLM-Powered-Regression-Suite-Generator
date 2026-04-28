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
        self.language_patterns = {
            "python": {
                "function": r'^def\s+(\w+)\s*\(',
                "class": r'^class\s+(\w+)[\(:]',
                "import": r'^(?:from|import)\s+',
                "extension": ".py"
            },
            "javascript": {
                "function": r'(?:function|const|let|var)\s+(\w+)\s*(?:=\s*)?(?:function)?\s*\(',
                "class": r'class\s+(\w+)(?:\s+extends)?',
                "import": r'^(?:import|require)',
                "extension": ".js"
            },
            "typescript": {
                "function": r'(?:function|const|let|var)\s+(\w+)\s*(?:=\s*)?(?:function)?\s*\(',
                "class": r'class\s+(\w+)(?:\s+extends)?',
                "import": r'^(?:import|require)',
                "extension": ".ts"
            },
            "java": {
                "function": r'(?:public|private|protected)?\s+(?:static)?\s+(\w+)\s+(\w+)\s*\(',
                "class": r'(?:public)?\s+class\s+(\w+)',
                "import": r'^import\s+',
                "extension": ".java"
            }
        }
    
    def analyze_changes(self, diff: str) -> Dict:
        """
        Analyze a unified diff and extract code changes
        
        Args:
            diff: Unified diff format string
            
        Returns:
            Analysis dictionary with changed files and functions
        """
        try:
            changed_files = self._parse_diff(diff)
            changed_functions = self._extract_changed_functions(changed_files)
            
            stats = {
                "additions": len([line for file_data in changed_files.values() 
                                 for line in file_data.get("added_lines", [])]),
                "deletions": len([line for file_data in changed_files.values() 
                                 for line in file_data.get("removed_lines", [])])
            }
            
            return {
                "changed_files": changed_files,
                "changed_functions": changed_functions,
                "stats": stats,
                "total_files": len(changed_files)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing changes: {str(e)}")
            return {
                "changed_files": {},
                "changed_functions": [],
                "stats": {"additions": 0, "deletions": 0},
                "total_files": 0,
                "error": str(e)
            }
    
    def _parse_diff(self, diff: str) -> Dict:
        """Parse unified diff format"""
        
        files = {}
        current_file = None
        current_content_added = []
        current_content_removed = []
        
        lines = diff.split('\n')
        
        for line in lines:
            # Detect file headers
            if line.startswith('+++') or line.startswith('---'):
                if line.startswith('+++'):
                    # Extract filename
                    filename = line[6:].split('\t')[0]
                    if filename != '/dev/null':
                        current_file = filename
                        files[current_file] = {
                            "path": filename,
                            "added_lines": [],
                            "removed_lines": [],
                            "language": self._detect_language(filename),
                            "changes": []
                        }
            elif line.startswith('+') and not line.startswith('+++'):
                if current_file:
                    added_content = line[1:]
                    current_content_added.append(added_content)
                    files[current_file]["added_lines"].append(added_content)
                    if added_content.strip() and not added_content.strip().startswith('#'):
                        files[current_file]["changes"].append({
                            "type": "addition",
                            "content": added_content
                        })
            elif line.startswith('-') and not line.startswith('---'):
                if current_file:
                    removed_content = line[1:]
                    current_content_removed.append(removed_content)
                    files[current_file]["removed_lines"].append(removed_content)
                    if removed_content.strip() and not removed_content.strip().startswith('#'):
                        files[current_file]["changes"].append({
                            "type": "deletion",
                            "content": removed_content
                        })
        
        return files
    
    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename"""
        
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
            ".java": "java",
            ".go": "go",
            ".rb": "ruby",
            ".cpp": "cpp",
            ".c": "c",
            ".cs": "csharp"
        }
        
        for ext, lang in extension_map.items():
            if filename.endswith(ext):
                return lang
        
        return "unknown"
    
    def _extract_changed_functions(self, changed_files: Dict) -> List[Dict]:
        """Extract function/method definitions from changed files"""
        
        changed_functions = []
        
        for filepath, file_data in changed_files.items():
            language = file_data.get("language", "unknown")
            
            if language not in self.language_patterns:
                continue
            
            patterns = self.language_patterns[language]
            
            # Analyze added lines for new/modified functions
            added_text = '\n'.join(file_data.get("added_lines", []))
            
            # Find function definitions
            func_pattern = patterns.get("function", "")
            if func_pattern:
                matches = re.finditer(func_pattern, added_text, re.MULTILINE)
                for match in matches:
                    func_name = match.group(1)
                    
                    # Extract context around function
                    context_start = max(0, match.start() - 200)
                    context_end = min(len(added_text), match.end() + 500)
                    context = added_text[context_start:context_end]
                    
                    changed_functions.append({
                        "name": func_name,
                        "file": filepath,
                        "language": language,
                        "type": "function",
                        "code": context,
                        "parameters": self._extract_parameters(context, language),
                        "return_type": self._extract_return_type(context, language)
                    })
            
            # Find class definitions
            class_pattern = patterns.get("class", "")
            if class_pattern:
                matches = re.finditer(class_pattern, added_text, re.MULTILINE)
                for match in matches:
                    class_name = match.group(1)
                    
                    context_start = max(0, match.start() - 100)
                    context_end = min(len(added_text), match.end() + 300)
                    context = added_text[context_start:context_end]
                    
                    changed_functions.append({
                        "name": class_name,
                        "file": filepath,
                        "language": language,
                        "type": "class",
                        "code": context,
                        "parameters": [],
                        "return_type": "class"
                    })
        
        return changed_functions
    
    def _extract_parameters(self, code: str, language: str) -> List[str]:
        """Extract function parameters from code"""
        
        if language == "python":
            # Match def function_name(params)
            pattern = r'def\s+\w+\s*\((.*?)\):'
            match = re.search(pattern, code)
            if match:
                params_str = match.group(1)
                params = [p.strip().split('=')[0].split(':')[0] 
                         for p in params_str.split(',') if p.strip()]
                return params
        
        elif language in ["javascript", "typescript"]:
            # Match function name(params)
            pattern = r'(?:function|const|let|var)\s+\w+\s*\((.*?)\)'
            match = re.search(pattern, code)
            if match:
                params_str = match.group(1)
                params = [p.strip().split('=')[0] 
                         for p in params_str.split(',') if p.strip()]
                return params
        
        elif language == "java":
            # Match visibility type name(params)
            pattern = r'(?:public|private|protected)?\s+(?:static)?\s+\w+\s+\w+\s*\((.*?)\)'
            match = re.search(pattern, code)
            if match:
                params_str = match.group(1)
                params = [p.strip().split()[-1] 
                         for p in params_str.split(',') if p.strip()]
                return params
        
        return []
    
    def _extract_return_type(self, code: str, language: str) -> str:
        """Extract function return type from code"""
        
        if language == "python":
            # Look for type hints
            pattern = r'->\s*(\w+)'
            match = re.search(pattern, code)
            return match.group(1) if match else "Any"
        
        elif language in ["typescript"]:
            # Look for type hints
            pattern = r'\):\s*(\w+)'
            match = re.search(pattern, code)
            return match.group(1) if match else "any"
        
        elif language == "java":
            # Match return type before method name
            pattern = r'(?:public|private|protected)?\s+(?:static)?\s+(\w+)\s+\w+\s*\('
            match = re.search(pattern, code)
            return match.group(1) if match else "void"
        
        return "unknown"
    
    def get_test_coverage_recommendations(self, changed_functions: List[Dict]) -> Dict:
        """Get recommendations for test coverage"""
        
        recommendations = {
            "critical_paths": [],
            "edge_cases": [],
            "error_cases": [],
            "integration_tests": []
        }
        
        for func in changed_functions:
            func_name = func.get("name")
            code = func.get("code", "")
            
            # Check for error handling
            if "try" in code or "except" in code or "catch" in code:
                recommendations["error_cases"].append(
                    f"Test error handling in {func_name}"
                )
            
            # Check for loops
            if "for " in code or "while " in code:
                recommendations["critical_paths"].append(
                    f"Test loop conditions in {func_name}"
                )
            
            # Check for conditionals
            if "if " in code or "else" in code:
                recommendations["critical_paths"].append(
                    f"Test all branches in {func_name}"
                )
            
            # Check for None/null handling
            if "is None" in code or "== null" in code:
                recommendations["edge_cases"].append(
                    f"Test None/null cases in {func_name}"
                )
            
            # Check for external calls
            if "http" in code.lower() or "request" in code.lower():
                recommendations["integration_tests"].append(
                    f"Test HTTP integration in {func_name}"
                )
        
        return recommendations
