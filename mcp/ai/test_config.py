"""
Test script for the MCP AI configuration system.
"""

import os
import sys
import io
from pathlib import Path

# Set console output encoding to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from mcp.ai.config import AIConfig, get_config, init_config
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Current Python path:", sys.path)
    raise

def test_config_initialization():
    """Test that the configuration initializes correctly."""
    print("Testing configuration initialization...")
    
    try:
        # Test with default configuration
        config = AIConfig()
        assert config is not None, "Failed to initialize AIConfig"
        
        # Test getting a value
        openai_key = config.get('ai.providers.openai.api_key')
        assert openai_key is not None, "Failed to get OpenAI API key"
        
        print("[PASS] Configuration initialization test passed!")
        return True
    except Exception as e:
        print(f"[FAIL] Configuration initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_global_config():
    """Test the global configuration instance."""
    print("\nTesting global configuration...")
    
    try:
        # Get the global config
        config = get_config()
        assert config is not None, "Failed to get global config"
        
        # Test setting and getting a value
        test_value = "test_value_123"
        config.set('test.key', test_value)
        assert config.get('test.key') == test_value, "Failed to set/get config value"
        
        print("[PASS] Global configuration test passed!")
        return True
    except Exception as e:
        print(f"[FAIL] Global configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_save_load():
    """Test saving and loading configuration."""
    print("\nTesting configuration save/load...")
    
    import tempfile
    import shutil
    
    try:
        # Create a temporary directory for testing
        temp_dir = Path(tempfile.mkdtemp())
        config_path = temp_dir / 'test_config.yaml'
        
        try:
            # Create a new config and save it
            config = AIConfig()
            test_value = "test_save_load_value"
            config.set('test.save_load', test_value)
            config.save(config_path)
            
            # Verify the file was created
            assert config_path.exists(), "Config file was not created"
            
            # Load the saved config
            loaded_config = AIConfig(str(config_path))
            loaded_value = loaded_config.get('test.save_load')
            assert loaded_value == test_value, f"Failed to load saved config. Expected '{test_value}', got '{loaded_value}'"
            
            print("[PASS] Configuration save/load test passed!")
            return True
        finally:
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception as e:
        print(f"[FAIL] Configuration save/load test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting MCP AI Configuration Tests...")
    print("====================================")
    
    passed = 0
    total = 3
    
    # Run tests
    if test_config_initialization():
        passed += 1
    
    if test_global_config():
        passed += 1
    
    if test_config_save_load():
        passed += 1
    
    # Print summary
    print("\nTest Summary:")
    print("============")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\nAll tests passed successfully!")
        sys.exit(0)
    else:
        print(f"\n{total - passed} tests failed!")
        sys.exit(1)
