"""
Document Processor for Word-GPT-Plus MCP plugin.

Handles document operations like chunking, processing, and applying changes.
"""

import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import logging

from .api_client import WordGPTPlusAPIClient

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process documents using AI models."""
    
    def __init__(self, config: Dict[str, Any], api_client: WordGPTPlusAPIClient):
        """Initialize the document processor."""
        self.config = config
        self.api_client = api_client
        
    def process_document(
        self,
        document_path: Union[str, Path],
        instructions: str,
        output_path: Optional[Union[str, Path]] = None,
        format: str = 'markdown'
    ) -> str:
        """
        Process a document with the given instructions.
        
        Args:
            document_path: Path to the input document
            instructions: Instructions for processing the document
            output_path: Path to save the processed document (optional)
            format: Output format ('markdown', 'html', 'docx')
            
        Returns:
            Processed document content
        """
        # Read the document
        content = self._read_document(document_path)
        
        # Process the content
        processed_content = self._process_content(content, instructions)
        
        # Save the result if output path is provided
        if output_path:
            self._write_document(processed_content, output_path, format)
            
        return processed_content
    
    def _read_document(self, path: Union[str, Path]) -> str:
        """Read document content from a file."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {path}")
            
        # Handle different file types
        if path.suffix.lower() == '.txt':
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        elif path.suffix.lower() == '.md':
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        elif path.suffix.lower() == '.docx':
            return self._read_docx(path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
    
    def _read_docx(self, path: Path) -> str:
        """Read content from a DOCX file."""
        try:
            import docx2txt
            return docx2txt.process(str(path))
        except ImportError:
            logger.warning("docx2txt not installed, falling back to text extraction")
            # Fallback to basic text extraction
            import zipfile
            import xml.etree.ElementTree as ET
            
            with zipfile.ZipFile(path) as docx:
                # Extract the document.xml from the docx
                with docx.open('word/document.xml') as f:
                    tree = ET.parse(f)
                    root = tree.getroot()
                    
                    # Extract text from paragraphs
                    namespaces = {
                        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
                    }
                    paragraphs = root.findall('.//w:p', namespaces)
                    text = []
                    
                    for p in paragraphs:
                        text_elements = p.findall('.//w:t', namespaces)
                        paragraph_text = ''.join([elem.text for elem in text_elements if elem.text])
                        if paragraph_text.strip():
                            text.append(paragraph_text)
                            
                    return '\n\n'.join(text)
    
    def _write_document(
        self,
        content: str,
        path: Union[str, Path],
        format: str = 'markdown'
    ) -> None:
        """Write content to a file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == 'markdown':
            with open(path.with_suffix('.md'), 'w', encoding='utf-8') as f:
                f.write(content)
        elif format.lower() == 'html':
            with open(path.with_suffix('.html'), 'w', encoding='utf-8') as f:
                f.write(f"<html><body>\n{content}\n</body></html>")
        elif format.lower() == 'docx':
            self._write_docx(content, path.with_suffix('.docx'))
        else:
            raise ValueError(f"Unsupported output format: {format}")
    
    def _write_docx(self, content: str, path: Path) -> None:
        """Write content to a DOCX file."""
        try:
            from docx import Document
            from docx.shared import Pt
            
            doc = Document()
            
            # Split content into paragraphs
            paragraphs = content.split('\n\n')
            
            for para in paragraphs:
                if para.strip():
                    p = doc.add_paragraph(para)
                    p.style = 'Normal'
            
            doc.save(str(path))
        except ImportError:
            logger.warning("python-docx not installed, saving as text instead")
            with open(path.with_suffix('.txt'), 'w', encoding='utf-8') as f:
                f.write(content)
    
    def _process_content(self, content: str, instructions: str) -> str:
        """Process document content with AI."""
        # Split content into chunks if needed
        chunk_size = self.config['processing']['chunk_size']
        overlap = self.config['processing']['overlap']
        
        if len(content) <= chunk_size:
            chunks = [content]
        else:
            chunks = self._chunk_content(content, chunk_size, overlap)
        
        # Process each chunk
        processed_chunks = []
        
        for i, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {i+1}/{len(chunks)}")
            
            # Add context from previous chunk if available
            context = ""
            if i > 0 and overlap > 0:
                context = chunks[i-1][-overlap:]
            
            # Process the chunk
            processed_chunk = self._process_chunk(chunk, instructions, context)
            processed_chunks.append(processed_chunk)
            
            # Add a small delay between API calls
            time.sleep(0.5)
        
        # Combine processed chunks
        return self._combine_chunks(processed_chunks, overlap)
    
    def _chunk_content(self, content: str, chunk_size: int, overlap: int) -> List[str]:
        """Split content into overlapping chunks."""
        chunks = []
        start = 0
        content_length = len(content)
        
        while start < content_length:
            end = min(start + chunk_size, content_length)
            
            # Try to find a good breaking point (end of paragraph or sentence)
            if end < content_length:
                # Look for paragraph break first
                para_break = content.rfind('\n\n', start, end + 1)
                if para_break != -1 and para_break > start + chunk_size // 2:
                    end = para_break + 2  # Include the newlines
                else:
                    # Look for sentence break
                    sentence_break = max(
                        content.rfind('. ', start, end + 1),
                        content.rfind('! ', start, end + 1),
                        content.rfind('? ', start, end + 1),
                        content.rfind('\n', start, end + 1)
                    )
                    if sentence_break != -1 and sentence_break > start + chunk_size // 2:
                        end = sentence_break + 1  # Include the space or newline
            
            chunks.append(content[start:end])
            start = end - overlap if end - overlap > start else end
        
        return chunks
    
    def _process_chunk(self, chunk: str, instructions: str, context: str = "") -> str:
        """Process a single chunk of content."""
        # Prepare the prompt
        prompt = f"""{instructions}
        
        Context from previous section (for reference only, do not include in your response):
        {context}
        
        Document content to process:
        ```
        {chunk}
        ```
        
        Processed content:
        """
        
        # Call the API
        max_retries = self.config['processing']['max_retries']
        retry_delay = self.config['processing']['retry_delay']
        
        for attempt in range(max_retries):
            try:
                return self.api_client.generate_text(
                    prompt=prompt,
                    temperature=self.config['api']['temperature'],
                    max_tokens=self.config['api']['max_tokens']
                )
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
                time.sleep(retry_delay * (attempt + 1))
        
        return ""  # Should never reach here
    
    def _combine_chunks(self, chunks: List[str], overlap: int) -> str:
        """Combine processed chunks into a single document."""
        if not chunks:
            return ""
            
        if len(chunks) == 1:
            return chunks[0]
        
        # For now, just join with double newlines
        # In a more sophisticated implementation, we might want to:
        # 1. Identify and remove overlapping content
        # 2. Ensure smooth transitions between chunks
        # 3. Handle formatting and structure preservation
        return "\n\n".join(chunks)
