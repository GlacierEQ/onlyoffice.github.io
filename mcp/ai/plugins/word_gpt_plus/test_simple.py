"""
Simple test file to verify the test environment is working.
"""

def test_environment():
    """Test that the test environment is working."""
    assert True, "Test environment is working"

class TestSimple:
    """Simple test class to verify test discovery."""
    
    def test_addition(self):
        """Test basic addition."""
        assert 1 + 1 == 2, "Basic addition should work"
