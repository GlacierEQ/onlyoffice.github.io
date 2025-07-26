"""
Tests for the DocumentProcessor class in the Word-GPT-Plus MCP plugin.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the plugin directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent))

from word_gpt_plus.document_processor import DocumentProcessor

class TestDocumentProcessor(unittest.TestCase):
    """Test cases for the DocumentProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.TemporaryDirectory()
        
        # Create test files
        self.test_files = {}
        
        # Text file
        self.test_files['txt'] = Path(self.test_dir.name) / 'test.txt'
        with open(self.test_files['txt'], 'w', encoding='utf-8') as f:
            f.write("This is a test text file.\nIt has multiple lines.\n")
        
        # Create a larger text file for chunking tests
        self.large_text = "\n\n".join([f"This is paragraph {i}." * 50 for i in range(10)])
        self.test_files['large.txt'] = Path(self.test_dir.name) / 'large.txt'
        with open(self.test_files['large.txt'], 'w', encoding='utf-8') as f:
            f.write(self.large_text)
        
        # Create a test config
        self.config = {
            'api': {
                'provider': 'openai',
                'model': 'gpt-4',
                'temperature': 0.7,
                'max_tokens': 2000
            },
            'processing': {
                'chunk_size': 1000,
                'overlap': 100,
                'max_retries': 3,
                'retry_delay': 1
            },
            'templates': {
                'default_prompt': 'Process this text: {content}'
            }
        }
        
        # Create a mock API client
        self.mock_api_client = MagicMock()
        self.mock_api_client.generate_text.return_value = "Processed text output"
        
        # Initialize the document processor
        self.processor = DocumentProcessor(self.config, self.mock_api_client)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.test_dir.cleanup()
    
    def test_read_text_file(self):
        """Test reading a text file."""
        content = self.processor._read_document(self.test_files['txt'])
        self.assertIn("This is a test text file", content)
        self.assertIn("It has multiple lines", content)
    
    @patch('docx2txt.process')
    def test_read_docx_file(self, mock_docx2txt):
        """Test reading a DOCX file."""
        # Mock docx2txt to return test content
        mock_docx2txt.return_value = "Mocked DOCX content"
        
        # Create a dummy DOCX file
        docx_path = Path(self.test_dir.name) / 'test.docx'
        docx_path.touch()
        
        content = self.processor._read_document(docx_path)
        self.assertEqual(content, "Mocked DOCX content")
        mock_docx2txt.assert_called_once()
    
    @patch('PyPDF2.PdfReader')
    def test_read_pdf_file(self, mock_pdf_reader):
        """Test reading a PDF file."""
        # Mock PDF reader
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Page 1 content\n"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page, mock_page]
        mock_pdf_reader.return_value = mock_reader
        
        # Create a dummy PDF file
        pdf_path = Path(self.test_dir.name) / 'test.pdf'
        pdf_path.touch()
        
        content = self.processor._read_document(pdf_path)
        self.assertEqual(content, "Page 1 content\n\nPage 1 content\n")
    
    def test_chunk_content(self):
        """Test content chunking."""
        # Test with a small chunk size to force multiple chunks
        self.processor.chunk_size = 50
        self.processor.chunk_overlap = 10
        
        chunks = self.processor._chunk_content(
            "This is a test. " * 20,  # About 300 chars
            chunk_size=50,
            overlap=10
        )
        
        # Should be more than one chunk
        self.assertGreater(len(chunks), 1)
        
        # Check that chunks don't exceed max size
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 50)
        
        # Check that chunks overlap properly
        for i in range(1, len(chunks)):
            overlap = set(chunks[i-1].split()) & set(chunks[i].split())
            self.assertGreater(len(overlap), 0)
    
    def test_process_document(self):
        """Test document processing."""
        # Setup mock API response
        self.mock_api_client.generate_text.return_value = "Processed chunk"
        
        # Process the document
        output_path = Path(self.test_dir.name) / 'output.txt'
        result = self.processor.process_document(
            self.test_files['large.txt'],
            "Summarize this text",
            output_path=output_path
        )
        
        # Check that the API was called
        self.mock_api_client.generate_text.assert_called()
        
        # Check that output file was created
        self.assertTrue(output_path.exists())
        
        # Check that the result contains our mock response
        self.assertIn("Processed chunk", result)
    
    def test_process_chunk(self):
        """Test processing a single chunk."""
        # Setup test data
        test_chunk = "This is a test chunk of text."
        instructions = "Make this more formal."
        
        # Setup mock API response
        self.mock_api_client.generate_text.return_value = "This is a formal test chunk of text."
        
        # Process the chunk
        result = self.processor._process_chunk(test_chunk, instructions)
        
        # Check that the API was called with the right prompt
        call_args = self.mock_api_client.generate_text.call_args[1]
        self.assertIn(test_chunk, call_args['prompt'])
        self.assertIn(instructions, call_args['prompt'])
        
        # Check the result
        self.assertEqual(result, "This is a formal test chunk of text.")
    
    def test_combine_chunks(self):
        """Test combining processed chunks."""
        # Test data
        chunks = [
            "First part of the document.",
            "Second part with some overlap.",
            "Final part of the document."
        ]
        
        # Test with no overlap
        result = self.processor._combine_chunks(chunks, overlap=0)
        self.assertEqual(result, "\n\n".join(chunks))
        
        # Test with overlap (should handle deduplication)
        # This is a simplified test - actual implementation would need more sophisticated checking
        result = self.processor._combine_chunks(chunks, overlap=10)
        self.assertIn("First part", result)
        self.assertIn("Second part", result)
        self.assertIn("Final part", result)


if __name__ == '__main__':
    unittest.main()
