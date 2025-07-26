"""
API Client for Word-GPT-Plus MCP plugin.

Handles communication with various AI providers.
"""

import json
import time
from typing import Dict, List, Optional, Any, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class WordGPTPlusAPIClient:
    """Client for interacting with AI providers."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the API client."""
        self.config = config
        self.session = self._create_session()
        self.providers = {
            'openai': self._call_openai,
            'azure': self._call_azure,
            'local': self._call_local,
            'ollama': self._call_ollama,
            'groq': self._call_groq,
        }
        
    def _create_session(self):
        """Create a requests session with retry logic."""
        session = requests.Session()
        retries = Retry(
            total=self.config.get('max_retries', 3),
            backoff_factor=self.config.get('retry_delay', 2),
            status_forcelist=[500, 502, 503, 504]
        )
        session.mount('http://', HTTPAdapter(max_retries=retries))
        session.mount('https://', HTTPAdapter(max_retries=retries))
        return session
    
    def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text using the configured AI provider.
        
        Args:
            prompt: The input prompt
            model: Override the default model
            temperature: Override the default temperature
            max_tokens: Override the default max tokens
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text
        """
        provider = self.config['api']['provider']
        if provider not in self.providers:
            raise ValueError(f"Unsupported provider: {provider}")
            
        # Use provided values or fall back to config
        model = model or self.config['api'].get('model')
        temperature = temperature if temperature is not None else self.config['api'].get('temperature', 0.7)
        max_tokens = max_tokens or self.config['api'].get('max_tokens', 2000)
        
        # Call the appropriate provider
        return self.providers[provider](
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def _call_openai(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Call OpenAI API."""
        url = f"{self.config['api'].get('base_url', 'https://api.openai.com/v1')}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config['api']['api_key']}"
        }
        
        messages = [{"role": "user", "content": prompt}]
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        response = self.session.post(
            url,
            headers=headers,
            json=data,
            timeout=self.config['api'].get('timeout', 30)
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    def _call_azure(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Call Azure OpenAI API."""
        if 'deployment_id' not in self.config['api']:
            raise ValueError("Azure deployment_id is required")
            
        url = f"{self.config['api']['base_url']}/openai/deployments/{self.config['api']['deployment_id']}/chat/completions?api-version=2023-05-15"
        
        headers = {
            "Content-Type": "application/json",
            "api-key": self.config['api']['api_key']
        }
        
        messages = [{"role": "user", "content": prompt}]
        
        data = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        response = self.session.post(
            url,
            headers=headers,
            json=data,
            timeout=self.config['api'].get('timeout', 30)
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    def _call_local(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Call a local inference server."""
        url = f"{self.config['api'].get('base_url', 'http://localhost:8080')}/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add API key if provided
        if 'api_key' in self.config['api']:
            headers["Authorization"] = f"Bearer {self.config['api']['api_key']}"
        
        messages = [{"role": "user", "content": prompt}]
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        response = self.session.post(
            url,
            headers=headers,
            json=data,
            timeout=self.config['api'].get('timeout', 60)  # Longer timeout for local
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    def _call_ollama(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Call Ollama API."""
        url = f"{self.config['api'].get('base_url', 'http://localhost:11434')}/api/chat"
        
        messages = [
            {
                "role": "user",
                "content": prompt,
                "images": kwargs.pop('images', None)
            }
        ]
        
        data = {
            "model": model,
            "messages": messages,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                **kwargs
            }
        }
        
        response = self.session.post(
            url,
            json=data,
            timeout=self.config['api'].get('timeout', 300)  # Longer timeout for local
        )
        response.raise_for_status()
        return response.json()['message']['content']
    
    def _call_groq(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Call Groq API."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config['api']['api_key']}"
        }
        
        messages = [{"role": "user", "content": prompt}]
        
        data = {
            "model": model or "mixtral-8x7b-32768",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        response = self.session.post(
            url,
            headers=headers,
            json=data,
            timeout=self.config['api'].get('timeout', 30)
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available models from the provider."""
        provider = self.config['api']['provider']
        
        if provider == 'openai':
            return self._get_openai_models()
        elif provider == 'azure':
            return self._get_azure_models()
        elif provider == 'groq':
            return self._get_groq_models()
        else:
            # For local/ollama, return the configured model
            return [{"id": self.config['api'].get('model', 'local-model')}]
    
    def _get_openai_models(self) -> List[Dict[str, Any]]:
        """Get available models from OpenAI."""
        url = f"{self.config['api'].get('base_url', 'https://api.openai.com/v1')}/models"
        headers = {
            "Authorization": f"Bearer {self.config['api']['api_key']}"
        }
        
        response = self.session.get(url, headers=headers)
        response.raise_for_status()
        
        return [
            {"id": model["id"], "object": model["object"]}
            for model in response.json()["data"]
        ]
    
    def _get_azure_models(self) -> List[Dict[str, Any]]:
        """Get available models from Azure."""
        # Azure doesn't have a direct models endpoint, return the configured model
        return [{"id": self.config['api'].get('deployment_id', 'azure-model')}]
    
    def _get_groq_models(self) -> List[Dict[str, Any]]:
        """Get available models from Groq."""
        url = "https://api.groq.com/openai/v1/models"
        headers = {
            "Authorization": f"Bearer {self.config['api']['api_key']}"
        }
        
        response = self.session.get(url, headers=headers)
        response.raise_for_status()
        
        return [
            {"id": model["id"], "object": model["object"]}
            for model in response.json()["data"]
        ]
