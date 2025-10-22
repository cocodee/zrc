"""
Basic import tests for ZRC library.
"""

def test_imports():
    """Test that all public APIs can be imported."""
    import zrc
    
    # Test core components
    assert hasattr(zrc, 'ZRCNode')
    assert hasattr(zrc, 'TopicPrefixes')
    
    # Test exceptions
    assert hasattr(zrc, 'ZRCError')
    assert hasattr(zrc, 'ServiceError')
    assert hasattr(zrc, 'ActionError')
    
    # Test pubsub components
    assert hasattr(zrc, 'Publisher')
    assert hasattr(zrc, 'Subscriber')
    
    # Test service components
    assert hasattr(zrc, 'ServiceServer')
    assert hasattr(zrc, 'ServiceClient')
    
    # Test action components
    assert hasattr(zrc, 'ActionServer')
    assert hasattr(zrc, 'ActionClient')
    assert hasattr(zrc, 'ActionHandle')
    assert hasattr(zrc, 'ActionStatus')
    assert hasattr(zrc, 'ActionResult')
    assert hasattr(zrc, 'ActionFeedback')

if __name__ == "__main__":
    test_imports()
    print("All imports successful!")