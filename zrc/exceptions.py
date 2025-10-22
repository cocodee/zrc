"""
Custom exceptions for the ZRC library.
"""

class ZRCError(Exception):
    """Base exception class for ZRC library."""
    pass

class ActionError(ZRCError):
    """Exception related to Action operations."""
    pass

class ServiceError(ZRCError):
    """Exception related to Service operations."""
    pass

class SerializationError(ZRCError):
    """Exception related to serialization operations."""
    pass