"""
LangChain-based Documentation Generator

This module provides AI-powered documentation generation using LangChain.
"""

import os
from typing import Any, Dict, Optional
from pathlib import Path

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import BaseLanguageModel
from langchain.chat_models import ChatOpenAI
from langchain.llms import HuggingFaceHub

from mcp.ai.plugin import AIPlugin, AIDocumentationGenerator

class LangChainDocumentationGenerator(AIDocumentationGenerator):
    """
    Documentation generator using LangChain for AI-powered content creation.
    """
    
    name = "langchain_docs"
    version = "0.1.0"
    description = "AI-powered documentation generator using LangChain"
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the documentation generator."""
        super().__init__(config)
        self.llm = self._initialize_llm()
        self.template_dir = self.config.get(
            'template_dir', 
            str(Path(__file__).parent / 'templates')
        )
        self._load_templates()
    
    def _initialize_llm(self) -> BaseLanguageModel:
        """Initialize the language model based on configuration."""
        model_type = self.config.get('model_type', 'openai')
        model_name = self.config.get('model_name', 'gpt-3.5-turbo')
        
        if model_type == 'huggingface':
            return HuggingFaceHub(
                repo_id=model_name,
                model_kwargs={"temperature": 0.5, "max_length": 2000}
            )
        else:  # Default to OpenAI
            return ChatOpenAI(
                model_name=model_name,
                temperature=0.7,
                max_tokens=2000
            )
    
    def _load_templates(self) -> None:
        """Load documentation templates from the template directory."""
        self.templates = {}
        template_dir = Path(self.template_dir)
        
        if not template_dir.exists():
            os.makedirs(template_dir, exist_ok=True)
            self._create_default_templates(template_dir)
        
        for template_file in template_dir.glob('*.j2'):
            with open(template_file, 'r', encoding='utf-8') as f:
                self.templates[template_file.stem] = f.read()
    
    def _create_default_templates(self, template_dir: Path) -> None:
        """Create default templates if they don't exist."""
        default_templates = {
            'mcp_component.md.j2': """# {{ mcp.name }}

{{ mcp.desc }}

## Overview

**Status**: {{ mcp.status|capitalize }}  
**Module**: `{{ mcp.module }}`  
**Documentation**: [View Documentation]({{ mcp.url }})  

## Functions

{% for func in mcp.functions %}
- {{ func }}
{% endfor %}

## AI-Generated Documentation

{{ ai_documentation }}

## Configuration

```yaml
# Example configuration for {{ mcp.name }}
{{ mcp.name|lower }}:
  enabled: true
  # Add your configuration here
```
"""
        }
        
        for filename, content in default_templates.items():
            with open(template_dir / filename, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def generate_documentation(self, mcp_data: Dict[str, Any], **kwargs) -> str:
        """
        Generate documentation for an MCP component using AI.
        
        Args:
            mcp_data: Dictionary containing MCP component data
            **kwargs: Additional arguments for documentation generation
            
        Returns:
            str: Generated documentation
        """
        template_name = kwargs.get('template', 'mcp_component.md.j2')
        
        # Get the template
        if template_name not in self.templates:
            raise ValueError(f"Template not found: {template_name}")
        
        # Generate AI documentation
        ai_docs = self._generate_ai_documentation(mcp_data)
        
        # Render the template
        from jinja2 import Template
        template = Template(self.templates[template_name])
        
        return template.render(
            mcp=mcp_data,
            ai_documentation=ai_docs,
            **kwargs
        )
    
    def _generate_ai_documentation(self, mcp_data: Dict[str, Any]) -> str:
        """Generate AI-powered documentation for an MCP component."""
        prompt_template = """You are an expert technical writer documenting a microservice component.
        
        Component: {name}
        Description: {description}
        Functions: {functions}
        Status: {status}
        
        Please generate comprehensive documentation for this component, including:
        1. A detailed description of what the component does
        2. Explanation of each function's purpose
        3. Common use cases and examples
        4. Any important notes or considerations
        5. Integration guidelines with other components
        
        Documentation:"""
        
        prompt = PromptTemplate(
            input_variables=["name", "description", "functions", "status"],
            template=prompt_template
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        result = chain.run(
            name=mcp_data.get('name', 'Unnamed Component'),
            description=mcp_data.get('desc', 'No description available'),
            functions='\n'.join(f"- {func}" for func in mcp_data.get('functions', [])),
            status=mcp_data.get('status', 'active').capitalize()
        )
        
        return result.strip()


# Plugin entry point
def create_plugin(config: Optional[Dict[str, Any]] = None) -> AIPlugin:
    """Create an instance of the documentation generator plugin."""
    return LangChainDocumentationGenerator(config)
