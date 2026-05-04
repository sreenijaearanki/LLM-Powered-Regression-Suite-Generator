"""
LLM Service - OpenAI GPT-4 + optional Google Gemini (lazy-loaded).
grpcio is NOT required at build time — Gemini loads only when used.
"""

import os
import re
import logging
from typing import Optional, Dict, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    @abstractmethod
    async def generate_completion(self, prompt: str, **kwargs) -> str:
        pass

    @abstractmethod
    def get_model_info(self) -> Dict:
        pass


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Try best model first, fall back to widely-available ones
        self.models = ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4"]
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=api_key)
        except ImportError:
            raise RuntimeError("openai package not installed.")

    async def generate_completion(self, prompt: str,
                                  temperature: float = 0.5,
                                  max_tokens: int = 2000, **kwargs) -> str:
        last_error = None
        for model in self.models:
            try:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are an expert software testing specialist."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content
            except Exception as e:
                last_error = e
                import logging
                logging.getLogger(__name__).warning(f"Model {model} failed: {e}, trying next...")
                continue
        raise last_error

    def get_model_info(self) -> Dict:
        return {"provider": "openai", "model": self.model}


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "gemini-pro"
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.model)
        except ImportError:
            raise RuntimeError(
                "google-generativeai not installed on this server. "
                "Use OpenAI provider instead, or contact admin."
            )

    async def generate_completion(self, prompt: str,
                                  temperature: float = 0.7,
                                  max_tokens: int = 2000, **kwargs) -> str:
        full_prompt = f"You are an expert software testing specialist.\n\n{prompt}"
        response = self.client.generate_content(
            full_prompt,
            generation_config={"temperature": temperature, "max_output_tokens": max_tokens}
        )
        return response.text

    def get_model_info(self) -> Dict:
        return {"provider": "gemini", "model": self.model}


class LLMService:
    def __init__(self):
        self.provider: Optional[LLMProvider] = None
        self.provider_name: Optional[str] = None

    def initialize(self, config: Dict) -> None:
        provider_name = config.get("provider", "openai").lower()
        api_key = config.get("api_key") or os.getenv(f"{provider_name.upper()}_API_KEY")

        if not api_key:
            raise ValueError(f"API key missing. Set {provider_name.upper()}_API_KEY env var.")

        if provider_name == "openai":
            self.provider = OpenAIProvider(api_key)
        elif provider_name == "gemini":
            self.provider = GeminiProvider(api_key)
        else:
            raise ValueError(f"Unknown provider: {provider_name}")

        self.provider_name = provider_name
        logger.info(f"LLM Service initialized with {provider_name}")

    async def generate_tests(self, function_info: Dict, code_context: str) -> str:
        if not self.provider:
            raise RuntimeError("LLM Service not initialized.")
        prompt = self._build_prompt(function_info, code_context)
        return await self.provider.generate_completion(prompt=prompt, temperature=0.5)

    async def analyze_code(self, code: str) -> Dict:
        if not self.provider:
            raise RuntimeError("LLM Service not initialized.")
        prompt = f"Analyze this code:\n\n```\n{code}\n```"
        response = await self.provider.generate_completion(prompt=prompt, temperature=0.3)
        return {"analysis": response, "provider": self.provider_name}

    def _build_prompt(self, function_info: Dict, code_context: str) -> str:
        name = function_info.get("name", "unknown")
        code = function_info.get("code", "")
        params = ", ".join(function_info.get("parameters", [])) or "none"
        language = function_info.get("language", "python")
        framework = "pytest" if language == "python" else "jest"

        return f"""Generate comprehensive regression tests for this function.

Function: {name}
Language: {language}
Framework: {framework}
Parameters: {params}

Code:
```{language}
{code}
```

PR diff context:
```
{code_context[:800]}
```

Generate valid {framework} test code covering: happy path, edge cases, error handling.
Output ONLY valid code, no explanation.
"""

    def get_provider_info(self) -> Dict:
        if not self.provider:
            return {"status": "not_initialized"}
        return self.provider.get_model_info()
