"""
Model Provider
Unified interface for different LLM providers: Ollama, OpenAI, Claude
"""

import subprocess
import os
from typing import Optional
from abc import ABC, abstractmethod


class ModelProvider(ABC):
    """Abstract base class for model providers."""

    @abstractmethod
    def generate(self, prompt: str, timeout: int = 300) -> Optional[str]:
        """Generate a response from the model."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the provider name."""
        pass


class OllamaProvider(ModelProvider):
    """Ollama local model provider."""

    def __init__(self, model: str = "llama3.2:latest"):
        self.model = model

    def generate(self, prompt: str, timeout: int = 300) -> Optional[str]:
        try:
            result = subprocess.run(
                ["ollama", "run", self.model],
                input=prompt.encode('utf-8'),
                capture_output=True,
                timeout=timeout
            )

            if result.returncode != 0:
                error = result.stderr.decode()[:200] if result.stderr else "Unknown error"
                print(f"⚠️  Ollama error: {error}")
                return None

            return result.stdout.decode('utf-8').strip()

        except subprocess.TimeoutExpired:
            print(f"⚠️  Timeout after {timeout}s")
            return None
        except FileNotFoundError:
            print("❌ Ollama not found. Install it and run 'ollama serve'")
            return None
        except Exception as e:
            print(f"⚠️  Error: {e}")
            return None

    def get_name(self) -> str:
        return f"Ollama ({self.model})"


class OpenAIProvider(ModelProvider):
    """OpenAI API provider."""

    def __init__(self, model: str = "gpt-4o-mini", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key.")

    def generate(self, prompt: str, timeout: int = 300) -> Optional[str]:
        try:
            import openai

            client = openai.OpenAI(api_key=self.api_key)

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates professional README documentation for software projects."},
                    {"role": "user", "content": prompt}
                ],
                # max_tokens=4096,
                temperature=0.7,
                timeout=timeout
            )

            return response.choices[0].message.content.strip()

        except ImportError:
            print("❌ OpenAI package not installed. Run: pip install openai")
            return None
        except Exception as e:
            print(f"⚠️  OpenAI error: {e}")
            return None

    def get_name(self) -> str:
        return f"OpenAI ({self.model})"


class ClaudeProvider(ModelProvider):
    """Anthropic Claude API provider."""

    def __init__(self, model: str = "claude-3-5-sonnet-20241022", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY env var or pass api_key.")

    def generate(self, prompt: str, timeout: int = 300) -> Optional[str]:
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)

            response = client.messages.create(
                model=self.model,
                # max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                system="You are a helpful assistant that creates professional README documentation for software projects."
            )

            return response.content[0].text.strip()

        except ImportError:
            print("❌ Anthropic package not installed. Run: pip install anthropic")
            return None
        except Exception as e:
            print(f"⚠️  Claude error: {e}")
            return None

    def get_name(self) -> str:
        return f"Claude ({self.model})"


def create_provider(provider_type: str, model: Optional[str] = None, api_key: Optional[str] = None) -> ModelProvider:
    """
    Factory function to create the appropriate model provider.

    Args:
        provider_type: One of 'ollama', 'openai', 'claude'
        model: Model name (optional, uses defaults)
        api_key: API key for cloud providers (optional, uses env vars)

    Returns:
        ModelProvider instance
    """
    provider_type = provider_type.lower()

    if provider_type == 'ollama':
        return OllamaProvider(model=model or "llama3.2:latest")

    elif provider_type == 'openai':
        return OpenAIProvider(model=model or "gpt-4o-mini", api_key=api_key)

    elif provider_type == 'claude':
        return ClaudeProvider(model=model or "claude-3-5-sonnet-20241022", api_key=api_key)

    else:
        raise ValueError(f"Unknown provider: {provider_type}. Use 'ollama', 'openai', or 'claude'")


def detect_provider_from_model(model_string: str) -> tuple[str, str]:
    """
    Auto-detect provider from model string.

    Examples:
        'gpt-4' -> ('openai', 'gpt-4')
        'claude-3' -> ('claude', 'claude-3')
        'llama3.2:latest' -> ('ollama', 'llama3.2:latest')
        'openai:gpt-4o' -> ('openai', 'gpt-4o')
        'claude:claude-3-opus' -> ('claude', 'claude-3-opus')
    """
    model_string = model_string.strip()

    # Check for explicit provider prefix
    if ':' in model_string and model_string.split(':')[0] in ['openai', 'claude', 'ollama']:
        parts = model_string.split(':', 1)
        return parts[0], parts[1]

    # Auto-detect from model name
    model_lower = model_string.lower()

    if model_lower.startswith('gpt-') or model_lower.startswith('o1'):
        return 'openai', model_string

    if model_lower.startswith('claude'):
        return 'claude', model_string

    # Default to Ollama for everything else
    return 'ollama', model_string
