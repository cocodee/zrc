"""
Test script to verify Docker environment setup.
"""

def test_docker_environment():
    """Test that the Docker environment is properly set up."""
    import zrc
    import zenoh
    
    # Test that we can create a node (this will fail if Zenoh isn't properly installed)
    try:
        # This will fail to connect but shouldn't raise import errors
        config = {"mode": "client", "connect": {"endpoints": ["tcp/zenoh-router:7447"]}}
        node = zrc.ZRCNode("test_node", config=config)
        node.close()
        print("Docker environment test passed!")
    except Exception as e:
        # We expect connection errors but not import errors
        if "Failed to open Zenoh session" in str(e):
            print("Docker environment test passed! (Connection error expected in test environment)")
        else:
            raise e

if __name__ == "__main__":
    test_docker_environment()