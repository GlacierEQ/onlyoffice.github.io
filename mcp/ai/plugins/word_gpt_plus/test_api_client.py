"""
Tests for the WordGPTPlusAPIClient class in the Word-GPT-Plus MCP plugin.
"""

import unittest
import json
from unittest.mock import patch, MagicMock
import requests
from requests.models import Response

# Add the plugin directory to the path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from word_gpt_plus.api_client import WordGPTPlusAPIClient

class TestWordGPTPlusAPIClient(unittest.TestCase):
    """Test cases for the WordGPTPlusAPIClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'api': {
                'provider': 'openai',
                'api_key': 'test-api-key',
                'base_url': 'https://api.openai.com/v1',
                'model': 'gpt-4',
                'temperature': 0.7,
                'max_tokens': 2000,
                'timeout': 30
            },
            'processing': {
                'max_retries': 3,
                'retry_delay': 1
            }
        }
        
        # Create a mock session
        self.mock_session = MagicMock()
        self.mock_response = MagicMock(spec=Response)
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = {
            'choices': [
                {
                    'message': {
                        'content': 'Test response from AI',
                        'role': 'assistant'
                    },
                    'finish_reason': 'stop',
                    'index': 0
                }
            ],
            'model': 'gpt-4',
            'usage': {
                'prompt_tokens': 10,
                'completion_tokens': 20,
                'total_tokens': 30
            }
        }
        self.mock_session.post.return_value = self.mock_response
        
        # Create the API client with the mock session
        with patch('requests.Session', return_value=self.mock_session):
            self.api_client = WordGPTPlusAPIClient(self.config)
    
    def test_initialization(self):
        """Test API client initialization."""
        self.assertEqual(self.api_client.config, self.config)
        self.assertIsNotNone(self.api_client.session)
        self.assertEqual(self.api_client.session.headers['Content-Type'], 'application/json')
    
    def test_generate_text_success(self):
        """Test successful text generation."""
        # Test data
        prompt = "Test prompt"
        model = "gpt-4"
        temperature = 0.8
        max_tokens = 1000
        
        # Make the API call
        response = self.api_client.generate_text(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Check the response
        self.assertEqual(response, 'Test response from AI')
        
        # Check that the API was called with the right parameters
        call_args = self.mock_session.post.call_args
        self.assertEqual(call_args[0][0], 'https://api.openai.com/v1/chat/completions')
        
        # Check the request payload
        request_data = call_args[1]['json']
        self.assertEqual(request_data['model'], model)
        self.assertEqual(request_data['temperature'], temperature)
        self.assertEqual(request_data['max_tokens'], max_tokens)
        self.assertEqual(len(request_data['messages']), 1)
        self.assertEqual(request_data['messages'][0]['role'], 'user')
        self.assertEqual(request_data['messages'][0]['content'], prompt)
    
    def test_generate_text_with_custom_provider(self):
        """Test text generation with a custom provider."""
        # Change the provider to Azure
        self.config['api']['provider'] = 'azure'
        self.config['api']['deployment_id'] = 'test-deployment'
        
        # Re-initialize with the new config
        with patch('requests.Session', return_value=self.mock_session):
            api_client = WordGPTPlusAPIClient(self.config)
        
        # Make the API call
        response = api_client.generate_text("Test prompt")
        
        # Check the response
        self.assertEqual(response, 'Test response from AI')
        
        # Check that the Azure endpoint was used
        call_args = self.mock_session.post.call_args
        self.assertIn('openai/deployments/test-deployment/chat/completions', call_args[0][0])
    
    def test_generate_text_with_retry(self):
        """Test retry logic on API failure."""
        # Setup mock to fail twice then succeed
        error_response = MagicMock(spec=Response)
        error_response.status_code = 500
        
        self.mock_session.post.side_effect = [
            error_response,  # First attempt fails
            error_response,  # Second attempt fails
            self.mock_response  # Third attempt succeeds
        ]
        
        # Make the API call
        response = self.api_client.generate_text("Test prompt with retry")
        
        # Should have succeeded after retries
        self.assertEqual(response, 'Test response from AI')
        self.assertEqual(self.mock_session.post.call_count, 3)
    
    def test_generate_text_with_max_retries_exceeded(self):
        """Test behavior when max retries are exceeded."""
        # Setup mock to always fail
        error_response = MagicMock(spec=Response)
        error_response.status_code = 500
        self.mock_session.post.return_value = error_response
        
        # Make the API call (should raise an exception)
        with self.assertRaises(requests.exceptions.HTTPError):
            self.api_client.generate_text("Test prompt with max retries")
        
        # Should have retried the configured number of times
        self.assertEqual(
            self.mock_session.post.call_count, 
            self.config['processing']['max_retries']
        )
    
    def test_get_available_models(self):
        """Test getting available models from the provider."""
        # Setup mock response for models endpoint
        models_response = {
            'data': [
                {'id': 'gpt-4', 'object': 'model'},
                {'id': 'gpt-3.5-turbo', 'object': 'model'},
            ]
        }
        
        mock_models_response = MagicMock(spec=Response)
        mock_models_response.status_code = 200
        mock_models_response.json.return_value = models_response
        
        # Make the models endpoint return our test data
        self.mock_session.get.return_value = mock_models_response
        
        # Get available models
        models = self.api_client.get_available_models()
        
        # Check the result
        self.assertEqual(len(models), 2)
        self.assertEqual(models[0]['id'], 'gpt-4')
        self.assertEqual(models[1]['id'], 'gpt-3.5-turbo')
        
        # Check that the API was called with the right URL
        call_args = self.mock_session.get.call_args
        self.assertEqual(call_args[0][0], 'https://api.openai.com/v1/models')
    
    def test_azure_get_available_models(self):
        """Test getting available models from Azure provider."""
        # Change to Azure provider
        self.config['api']['provider'] = 'azure'
        self.config['api']['deployment_id'] = 'test-deployment'
        
        # Re-initialize with the new config
        with patch('requests.Session', return_value=self.mock_session):
            api_client = WordGPTPlusAPIClient(self.config)
        
        # Azure doesn't have a models endpoint, so it should return the configured model
        models = api_client.get_available_models()
        self.assertEqual(len(models), 1)
        self.assertEqual(models[0]['id'], 'test-deployment')


if __name__ == '__main__':
    unittest.main()
