"""
Test Generator Service - Creates framework-specific test cases via LLM.
"""

import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class TestGenerator:

    async def generate_tests(self, function_info: Dict, code_context: str,
                             llm_service, framework: str = "pytest") -> List[Dict]:
        """Async - must be awaited inside FastAPI background tasks."""
        try:
            response = await llm_service.generate_tests(function_info, code_context)
            return self._parse(response, function_info, framework)
        except Exception as e:
            logger.error(f"Error generating tests for {function_info.get('name')}: {e}")
            return []

    def _parse(self, response: str, function_info: Dict, framework: str) -> List[Dict]:
        blocks = re.findall(
            r'```(?:python|javascript|typescript|java)?\n?(.*?)```',
            response, re.DOTALL
        )
        if not blocks:
            blocks = [response]

        return [
            {
                "id": f"{function_info.get('name', 'fn')}_test_{i}",
                "name": f"test_{function_info.get('name', 'fn')}_{i}",
                "function": function_info.get("name"),
                "file": function_info.get("file"),
                "framework": framework,
                "language": function_info.get("language", "python"),
                "code": block.strip(),
                "type": "regression",
                "priority": "high" if i == 0 else "medium",
                "description": f"Regression test {i + 1} for {function_info.get('name')}()",
                "tags": ["regression", function_info.get("name", ""), framework],
            }
            for i, block in enumerate(blocks)
            if block.strip()
        ]

    # ── Framework templates ──────────────────────────────────────────────────

    def get_template(self, framework: str) -> str:
        templates = {
            "pytest": (
                "import pytest\n\n"
                "def test_example():\n"
                "    assert True\n"
            ),
            "unittest": (
                "import unittest\n\n"
                "class TestExample(unittest.TestCase):\n"
                "    def test_example(self):\n"
                "        self.assertTrue(True)\n\n"
                "if __name__ == '__main__':\n"
                "    unittest.main()\n"
            ),
            "jest": (
                "describe('Example', () => {\n"
                "  test('should work', () => {\n"
                "    expect(true).toBe(true);\n"
                "  });\n"
                "});\n"
            ),
            "junit": (
                "import org.junit.jupiter.api.Test;\n"
                "import static org.junit.jupiter.api.Assertions.*;\n\n"
                "class ExampleTest {\n"
                "    @Test\n"
                "    void testExample() {\n"
                "        assertTrue(true);\n"
                "    }\n"
                "}\n"
            ),
        }
        return templates.get(framework, templates["pytest"])
