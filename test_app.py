# backend/test_app.py

import unittest
import json
import os
from unittest.mock import patch, MagicMock
from app import app

class TestDDQChatApp(unittest.TestCase):
    """Test cases for the DDQ Chat App Flask application."""
    
    def setUp(self):
        """Set up test client and other test variables."""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'ok')
    
    @patch('app.search_service')
    @patch('app.get_openai_completion')
    @patch('app.blob_service')
    def test_chat_endpoint(self, mock_blob_service, mock_get_openai_completion, mock_search_service):
        """Test the chat endpoint with mocked services."""
        # Mock search service response
        mock_search_results = {
            "count": 1,
            "results": [
                {
                    "id": "doc1",
                    "title": "ESG Policy",
                    "content": "Our ESG policy emphasizes responsible investment.",
                    "source": "ESG Policy",
                    "sourceFile": "ESG_Policy.pdf",
                    "score": 0.95
                }
            ]
        }
        mock_search_service.search_documents.return_value = mock_search_results
        
        # Mock OpenAI response
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = "Based on the ESG Policy, the fund emphasizes responsible investment."
        mock_get_openai_completion.return_value = mock_completion
        
        # Mock blob service response
        mock_blob_service.upload_document.return_value = "https://example.blob.core.windows.net/container/document.docx"
        
        # Test data
        test_data = {
            "prompt": "What is the fund's ESG policy?",
            "history": []
        }
        
        # Make request
        response = self.app.post(
            '/api/chat',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('ai_response', data)
        self.assertIn('document_url', data)
        self.assertIn('sources', data)
        self.assertEqual(data['ai_response'], "Based on the ESG Policy, the fund emphasizes responsible investment.")
        self.assertEqual(data['document_url'], "https://example.blob.core.windows.net/container/document.docx")
        self.assertEqual(data['sources'], ["ESG_Policy.pdf"])
    
    def test_chat_endpoint_missing_prompt(self):
        """Test the chat endpoint with missing prompt."""
        test_data = {
            "history": []
        }
        
        response = self.app.post(
            '/api/chat',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], "No prompt provided")

if __name__ == '__main__':
    unittest.main()
