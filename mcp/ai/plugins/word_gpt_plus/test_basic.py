"""
Basic test file to verify the test environment is working.
This test doesn't rely on any external packages or modules.
"""

def test_environment():
    """Test that the test environment is working."""
    assert True, "Test environment is working"

class TestBasic:
    """Basic test class to verify test discovery."""
    
    def test_addition(self):
        """Test basic addition."""
        assert 1 + 1 == 2, "Basic addition should work"
