"""
LLM Service - Handles interactions with various LLM providers
Supports OpenAI (GPT-4, GPT-3.5) and Google Gemini
"""

import os
import json
import logging
from typing import Optional, Dict, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate_completion(self, prompt: str, **kwargs) -> str:
        """Generate a completion from the LLM"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict:
        """Get information about the model"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "gpt-4"
        
        try:
            import openai
            openai.api_key = api_key
            self.client = openai.AsyncOpenAI(api_key=api_key)
        except ImportError:
            logger.error("openai library not installed. Install with: pip install openai")
            raise
    
    async def generate_completion(self, prompt: str, 
                                 temperature: float = 0.7,
                                 max_tokens: int = 2000,
                                 **kwargs) -> str:
        """Generate completion using OpenAI API"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert software testing specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.9,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise
    
    def get_model_info(self) -> Dict:
        return {
            "provider": "openai",
            "model": self.model,
            "capabilities": ["text-generation", "code-generation"],
            "max_tokens": 8192,
            "context_window": 8192
        }


class GeminiProvider(LLMProvider):
    """Google Gemini provider"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "gemini-pro"
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.model)
        except ImportError:
            logger.error("google-generativeai library not installed. Install with: pip install google-generativeai")
            raise
    
    async def generate_completion(self, prompt: str,
                                 temperature: float = 0.7,
                                 max_tokens: int = 2000,
                                 **kwargs) -> str:
        """Generate completion using Gemini API"""
        try:
            # Add system context to the prompt
            full_prompt = f"""You are an expert software testing specialist.

User Request:
{prompt}"""
            
            response = self.client.generate_content(
                full_prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                    "top_p": 0.9,
                    "top_k": 40
                }
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            raise
    
    def get_model_info(self) -> Dict:
        return {
            "provider": "gemini",
            "model": self.model,
            "capabilities": ["text-generation", "code-generation"],
            "max_tokens": 2048,
            "context_window": 32000
        }


class LLMService:
    """Main LLM Service - manages provider selection and API calls"""
    
    def __init__(self):
        self.provider = None
        self.provider_name = None
    
    def initialize(self, config: Dict) -> None:
        """
        Initialize the LLM service with a specific provider
        
        Args:
            config: Configuration dictionary with 'provider' and 'api_key'
                   Example: {"provider": "openai", "api_key": "sk-..."}
        """
        provider_name = config.get("provider", "openai").lower()
        api_key = config.get("api_key")
        
        if not api_key:
            # Try to get from environment
            env_key = f"{provider_name.upper()}_API_KEY"
            api_key = os.getenv(env_key)
            
            if not api_key:
                raise ValueError(f"API key not provided and {env_key} not set")
        
        try:
            if provider_name == "openai":
                self.provider = OpenAIProvider(api_key)
                self.provider_name = "openai"
            elif provider_name == "gemini":
                self.provider = GeminiProvider(api_key)
                self.provider_name = "gemini"
            else:
                raise ValueError(f"Unknown provider: {provider_name}")
            
            logger.info(f"LLM Service initialized with {provider_name}")
            
        except Exception as e:
            logger.error(f"Error initializing LLM service: {str(e)}")
            raise
    
    async def generate_tests(self, function_info: Dict, code_context: str) -> Dict:
        """
        Generate tests for a specific function
        
        Args:
            function_info: Information about the function
            code_context: The code change context
            
        Returns:
            Generated test cases
        """
        if not self.provider:
            raise RuntimeError("LLM Service not initialized")
        
        prompt = self._build_test_generation_prompt(function_info, code_context)
        
        try:
            response = await self.provider.generate_completion(
                prompt=prompt,
                temperature=0.5,  # Lower temperature for more consistent tests
                max_tokens=2000
            )
            
            return self._parse_test_response(response, function_info)
            
        except Exception as e:
            logger.error(f"Error generating tests: {str(e)}")
            raise
    
    async def analyze_code(self, code: str) -> Dict:
        """
        Analyze code for testing requirements
        
        Args:
            code: Code to analyze
            
        Returns:
            Analysis results
        """
        if not self.provider:
            raise RuntimeError("LLM Service not initialized")
        
        prompt = f"""Analyze the following code and identify:
1. Key functions/methods and their purposes
2. Input parameters and expected types
3. Return values and side effects
4. Edge cases and error conditions
5. Dependencies and external calls

Code:
```
{code}
```

Provide a structured analysis."""
        
        try:
            response = await self.provider.generate_completion(
                prompt=prompt,
                temperature=0.3,
                max_tokens=2000
            )
            
            return {
                "analysis": response,
                "provider": self.provider_name
            }
            
        except Exception as e:
            logger.error(f"Error analyzing code: {str(e)}")
            raise
    
    def _build_test_generation_prompt(self, function_info: Dict, code_context: str) -> str:
        """Build the prompt for test generation"""
        
        function_name = function_info.get("name", "unknown")
        function_code = function_info.get("code", "")
        parameters = function_info.get("parameters", [])
        return_type = function_info.get("return_type", "unknown")
        language = function_info.get("language", "python")
        
        param_str = ", ".join(parameters) if parameters else "none"
        
        test_framework = "pytest" if language == "python" else "jest"
        
        prompt = f"""Generate comprehensive regression tests for the following function.

Function Name: {function_name}
Language: {language}
Test Framework: {test_framework}
Parameters: {param_str}
Return Type: {return_type}

Function Code:
```{language}
{function_code}
```

Code Context (changes around the function):
```
{code_context[:1000]}
```

Generate test cases that:
1. Test the main happy path
2. Test edge cases and boundary conditions
3. Test error handling
4. Verify the function's behavior after the changes made in the PR
5. Include assertions for all critical paths

Format the response as valid {test_framework} code with clear test names and docstrings.
Include multiple test functions, each testing a specific scenario.

Test Code:
"""
        return prompt
    
    def _parse_test_response(self, response: str, function_info: Dict) -> List[Dict]:
        """Parse the LLM response and extract test cases"""
        
        # Extract code blocks from response
        import re
        code_blocks = re.findall(r'```(?:python|javascript|java|typescript)?\n(.*?)```', response, re.DOTALL)
        
        if not code_blocks:
            # If no code blocks found, return the full response as a single test
            code_blocks = [response]
        
        tests = []
        for idx, code_block in enumerate(code_blocks):
            test_case = {
                "function": function_info.get("name"),
                "code": code_block.strip(),
                "language": function_info.get("language", "python"),
                "framework": "pytest",
                "priority": "high" if idx == 0 else "medium",
                "description": f"Test case {idx + 1} for {function_info.get('name')}"
            }
            tests.append(test_case)
        
        return tests
    
    def get_provider_info(self) -> Dict:
        """Get information about the current provider"""
        if not self.provider:
            return {"status": "not_initialized"}
        
        return self.provider.get_model_info()
