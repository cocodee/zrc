"""
Publisher/Subscriber implementation for ZRC.
"""

import zenoh
from typing import Any, Callable, Optional
from .core import ZRCNode
from .exceptions import ZRCError

class Publisher:
    def __init__(self, session: ZRCNode, key_expr: str, serializer: str = 'json'):
        self.session = session
        self.key_expr = key_expr
        self.serializer = serializer
        self._publisher = session.session.declare_publisher(key_expr)
        session._add_resource(self._publisher)

    def publish(self, data: Any):
        """Publish data using the specified serializer."""
        payload = self.session._serialize(data, self.serializer)
        try:
            self._publisher.put(payload)
        except Exception as e:
            raise ZRCError(f"Failed to publish to {self.key_expr}: {e}")

class Subscriber:
    def __init__(self, session: ZRCNode, key_expr: str, callback: Callable[[Any], None],
                 serializer: str = 'json', message_type: Optional[Any] = None):
        
        def zenoh_callback(sample: zenoh.Sample):
            try:
                payload = sample.payload
                payload_data = session._deserialize(payload.to_bytes(), serializer, message_type)
                callback(payload_data)
            except Exception as e:
                print(f"Error in subscriber callback: {e}")  # Log error but don't interrupt

        self.session = session
        self.key_expr = key_expr
        self._subscriber = session.session.declare_subscriber(key_expr, zenoh_callback)
        session._add_resource(self._subscriber)