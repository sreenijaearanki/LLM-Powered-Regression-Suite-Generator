"""
Test Generator Service - Creates test cases using LLM
"""

import logging
from typing import Dict, List, Optional
import re

logger = logging.getLogger(__name__)

class TestGenerator:
    """Generates regression tests from code changes"""
    
    def __init__(self):
        self.test_templates = {
            "pytest": self._get_pytest_template(),
            "unittest": self._get_unittest_template(),
            "jest": self._get_jest_template(),
            "junit": self._get_junit_template()
        }
    
    def generate_tests(self, function_info: Dict, code_context: str,
                      llm_service, framework: str = "pytest") -> List[Dict]:
        """
        Generate test cases for a function
        
        Args:
            function_info: Information about the function to test
            code_context: The code change context
            llm_service: Initialized LLM service
            framework: Test framework to use
            
        Returns:
            List of generated test cases
        """
        
        try:
            # Build the test generation prompt
            prompt = self._build_prompt(function_info, code_context, framework)
            
            # Call LLM to generate tests
            import asyncio
            test_code = asyncio.run(
                llm_service.generate_tests(function_info, code_context)
            )
            
            # Parse and structure the tests
            tests = self._parse_generated_tests(test_code, function_info, framework)
            
            return tests
            
        except Exception as e:
            logger.error(f"Error generating tests: {str(e)}")
            return []
    
    def _build_prompt(self, function_info: Dict, code_context: str, 
                     framework: str) -> str:
        """Build the test generation prompt"""
        
        func_name = function_info.get("name", "unknown")
        func_code = function_info.get("code", "")
        language = function_info.get("language", "python")
        
        framework_map = {
            "python": "pytest",
            "javascript": "jest",
            "typescript": "jest",
            "java": "junit"
        }
        
        actual_framework = framework_map.get(language, framework)
        
        prompt = f"""Generate comprehensive regression test cases for the following {language} function.

Function Name: {func_name}
Test Framework: {actual_framework}

Function Code:
```{language}
{func_code}
```

Changed Code Context:
```
{code_context[:800]}
```

Create test cases that:
1. Test the happy path with valid inputs
2. Test boundary conditions and edge cases
3. Test error handling and exceptions
4. Test the function's behavior after recent changes
5. Include proper assertions and error messages

Generate valid {actual_framework} code with multiple test functions.
Each test should have a descriptive name and docstring.

Include:
- Positive test cases (expected behavior)
- Negative test cases (error handling)
- Edge cases (boundary values, empty inputs, etc.)
- Integration points if applicable

Output valid {actual_framework} code only:
"""
        return prompt
    
    def _parse_generated_tests(self, llm_response, function_info: Dict, 
                               framework: str) -> List[Dict]:
        """Parse LLM-generated tests into structured format"""
        
        tests = []
        
        # Extract code blocks
        code_blocks = re.findall(
            r'```(?:python|javascript|typescript|java)?\n?(.*?)```',
            llm_response,
            re.DOTALL
        )
        
        if not code_blocks:
            code_blocks = [llm_response]
        
        for idx, code in enumerate(code_blocks):
            test_case = {
                "id": f"{function_info.get('name')}_test_{idx}",
                "name": f"test_{function_info.get('name')}_{idx}",
                "function": function_info.get("name"),
                "file": function_info.get("file"),
                "framework": framework,
                "language": function_info.get("language", "python"),
                "code": code.strip(),
                "type": "regression",
                "priority": "high" if idx == 0 else "medium",
                "description": f"Regression test {idx + 1} for {function_info.get('name')}()",
                "tags": ["regression", function_info.get("name"), framework]
            }
            tests.append(test_case)
        
        return tests
    
    def format_test(self, test_case: Dict, framework: str) -> str:
        """Format a test case for the specified framework"""
        
        code = test_case.get("code", "")
        
        if framework == "pytest":
            return self._format_pytest(code)
        elif framework == "unittest":
            return self._format_unittest(code)
        elif framework == "jest":
            return self._format_jest(code)
        elif framework == "junit":
            return self._format_junit(code)
        
        return code
    
    def _format_pytest(self, code: str) -> str:
        """Format as pytest"""
        
        # Ensure proper pytest structure
        if not code.strip().startswith("def test_"):
            code = f"def test_generated():\n    {code}"
        
        return code
    
    def _format_unittest(self, code: str) -> str:
        """Format as unittest"""
        
        template = """import unittest

class TestGenerated(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    {code}

if __name__ == '__main__':
    unittest.main()
"""
        return template.format(code=code)
    
    def _format_jest(self, code: str) -> str:
        """Format as jest"""
        
        if not code.strip().startswith("describe") and not code.strip().startswith("test"):
            code = f"test('generated test', () => {{\n    {code}\n}})"
        
        return code
    
    def _format_junit(self, code: str) -> str:
        """Format as JUnit"""
        
        if "@Test" not in code:
            code = f"@Test\npublic void testGenerated() {{\n    {code}\n}}"
        
        return code
    
    def _get_pytest_template(self) -> str:
        """Get pytest test template"""
        return """
import pytest
from unittest.mock import Mock, patch, MagicMock

class TestFunction:
    \"\"\"Test suite for function\"\"\"
    
    def setup_method(self):
        \"\"\"Set up test fixtures\"\"\"
        pass
    
    def teardown_method(self):
        \"\"\"Clean up after tests\"\"\"
        pass
    
    def test_happy_path(self):
        \"\"\"Test normal operation\"\"\"
        assert True
    
    def test_edge_cases(self):
        \"\"\"Test boundary conditions\"\"\"
        assert True
    
    def test_error_handling(self):
        \"\"\"Test error cases\"\"\"
        assert True
    
    @pytest.mark.parametrize("input,expected", [
        ("valid", "result"),
        ("edge", "special"),
    ])
    def test_parametrized(self, input, expected):
        \"\"\"Test with multiple parameters\"\"\"
        assert True
"""
    
    def _get_unittest_template(self) -> str:
        """Get unittest test template"""
        return """
import unittest
from unittest.mock import Mock, patch

class TestFunction(unittest.TestCase):
    
    def setUp(self):
        \"\"\"Set up test fixtures\"\"\"
        pass
    
    def tearDown(self):
        \"\"\"Clean up after tests\"\"\"
        pass
    
    def test_happy_path(self):
        \"\"\"Test normal operation\"\"\"
        self.assertTrue(True)
    
    def test_edge_cases(self):
        \"\"\"Test boundary conditions\"\"\"
        self.assertTrue(True)
    
    def test_error_handling(self):
        \"\"\"Test error cases\"\"\"
        with self.assertRaises(Exception):
            pass

if __name__ == '__main__':
    unittest.main()
"""
    
    def _get_jest_template(self) -> str:
        """Get jest test template"""
        return """
describe('Function', () => {
    beforeEach(() => {
        // Setup before each test
    });
    
    afterEach(() => {
        // Cleanup after each test
    });
    
    test('happy path', () => {
        expect(true).toBe(true);
    });
    
    test('edge cases', () => {
        expect(true).toBe(true);
    });
    
    test('error handling', () => {
        expect(() => {
            // Should throw
        }).toThrow();
    });
    
    test.each([
        ['input1', 'output1'],
        ['input2', 'output2'],
    ])('parametrized test with %s', (input, expected) => {
        expect(true).toBe(true);
    });
});
"""
    
    def _get_junit_template(self) -> str:
        """Get JUnit test template"""
        return """
import org.junit.Test;
import org.junit.Before;
import org.junit.After;
import static org.junit.Assert.*;

public class FunctionTest {
    
    @Before
    public void setUp() {
        // Setup before each test
    }
    
    @After
    public void tearDown() {
        // Cleanup after each test
    }
    
    @Test
    public void testHappyPath() {
        assertTrue(true);
    }
    
    @Test
    public void testEdgeCases() {
        assertTrue(true);
    }
    
    @Test
    public void testErrorHandling() {
        try {
            fail("Should have thrown exception");
        } catch (Exception e) {
            // Expected
        }
    }
}
"""
