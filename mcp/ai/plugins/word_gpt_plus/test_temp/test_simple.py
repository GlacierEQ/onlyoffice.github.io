"""
A simple test file to verify the test environment.
"""

def test_addition():
    """Test basic addition."""
    assert 1 + 1 == 2, "1 + 1 should equal 2"

class TestSimple:
    """Simple test class to verify test discovery."""
    
    def test_subtraction(self):
        """Test basic subtraction."""
        assert 2 - 1 == 1, "2 - 1 should equal 1"
