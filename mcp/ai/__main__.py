"""
MCP AI Service Entry Point

This module serves as the main entry point for the MCP AI service.
It handles environment setup, configuration, and service initialization.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mcp_ai.log')
    ]
)

logger = logging.getLogger(__name__)

def setup_environment():
    """Set up the environment for the AI service."""
    # Load environment variables from .env file if it exists
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        logger.info(f"Loaded environment from {env_path}")
    else:
        logger.warning(f"No .env file found at {env_path}")
    
    # Ensure required environment variables are set
    required_vars = [
        'OPENAI_API_KEY',
        'HUGGINGFACE_API_KEY',
        'LANGCHAIN_API_KEY'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.warning(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.warning("Some features may not work as expected.")

def main():
    """Main entry point for the MCP AI service."""
    try:
        # Set up environment
        setup_environment()
        
        # Import here to ensure environment is set up first
        from mcp.ai.service import get_ai_service
        
        logger.info("Starting MCP AI Service...")
        
        # Initialize and start the AI service
        ai_service = get_ai_service()
        if not ai_service.initialize():
            logger.error("Failed to initialize AI service")
            return 1
        
        logger.info("MCP AI Service is running. Press Ctrl+C to exit.")
        
        # Keep the service running
        import time
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down MCP AI Service...")
        return 0
    except Exception as e:
        logger.exception(f"Error in MCP AI Service: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
