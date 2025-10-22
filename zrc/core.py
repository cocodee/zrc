"""
Core components of the ZRC library.
"""

import zenoh
import json
import threading
from typing import Any, Dict, Optional, List
from .exceptions import ZRCError

class TopicPrefixes:
    """Topic prefix configuration with customizable namespace."""
    def __init__(self, base_prefix: str = "zrc"):
        self.base = base_prefix
        self.topic = f"{base_prefix}/topic"
        self.service_req = f"{base_prefix}/service/req"
        self.service_resp = f"{base_prefix}/service/resp"
        self.action_goal = f"{base_prefix}/action/goal"
        self.action_feedback = f"{base_prefix}/action/feedback"
        self.action_result = f"{base_prefix}/action/result"
        self.action_cancel = f"{base_prefix}/action/cancel"

class ZRCNode:
    """
    Zenoh Robot Control core node.
    Manages Zenoh session and provides interfaces for PubSub/Service/Action.
    Supports JSON (default), Protobuf, and Raw Bytes serialization.
    """
    def __init__(self, node_name: str, config: Optional[Dict] = None, 
                 topic_prefixes: Optional[TopicPrefixes] = None):
        self.node_name = node_name
        self.topic_prefixes = topic_prefixes or TopicPrefixes()
        
        # Configure Zenoh
        zenoh_config = config if config is not None else {}
        try:
            self.session: zenoh.Session = zenoh.open(zenoh_config)
        except Exception as e:
            raise ZRCError(f"Failed to open Zenoh session: {e}")

        # Track created resources for cleanup
        self._resources: List[Any] = []
        self._lock = threading.RLock()  # For thread safety

    def close(self):
        """Close Zenoh session and clean up resources."""
        with self._lock:
            # Clean up all resources
            for resource in self._resources:
                try:
                    if hasattr(resource, 'undeclare'):
                        resource.undeclare()
                except Exception:
                    pass  # Ignore cleanup errors
            self._resources.clear()
        
        try:
            self.session.close()
        except Exception:
            pass

    def _add_resource(self, resource):
        """Add resource to tracking list"""
        with self._lock:
            self._resources.append(resource)

    # --- Helper methods: Serialization ---
    def _serialize(self, data: Any, serializer: str = 'json') -> bytes:
        """Serialize data to bytes, supporting multiple formats."""
        try:
            if serializer == 'json':
                if isinstance(data, (bytes, str, int, float, bool)):
                    return json.dumps(data).encode('utf-8')
                return json.dumps(data, ensure_ascii=False).encode('utf-8')
            
            elif serializer == 'protobuf':
                # Assume data is an instantiated Protobuf message object
                if hasattr(data, 'SerializeToString'):
                    return data.SerializeToString()
                raise TypeError("Protobuf serializer requires an object with a 'SerializeToString' method.")
            
            elif serializer == 'raw':
                if isinstance(data, bytes):
                    return data
                if isinstance(data, str):
                    return data.encode('utf-8')
                raise TypeError("Raw serializer requires input data to be bytes or string.")
            
            else:
                raise ValueError(f"Unknown serializer: {serializer}")
        except Exception as e:
            raise ZRCError(f"Serialization failed: {e}")

    # --- Helper methods: Deserialization ---
    def _deserialize(self, data: bytes, serializer: str = 'json', message_type: Optional[Any] = None) -> Any:
        """Deserialize bytes to data object."""
        try:
            if serializer == 'json':
                try:
                    return json.loads(data.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return data.decode('utf-8')

            elif serializer == 'protobuf':
                if message_type is None:
                    raise ValueError("Protobuf deserialization requires a specific message_type class.")
                
                msg = message_type()
                msg.ParseFromString(data)
                return msg
            
            elif serializer == 'raw':
                return data
                
            else:
                raise ValueError(f"Unknown serializer: {serializer}")
        except Exception as e:
            raise ZRCError(f"Deserialization failed: {e}")

    # --- Resource creation methods ---
    def create_publisher(self, topic_name: str, serializer: str = 'json'):
        from .pubsub import Publisher
        return Publisher(self, f"{self.topic_prefixes.topic}/{topic_name}", serializer)

    def create_subscriber(self, topic_name: str, callback,
                         serializer: str = 'json', message_type: Optional[Any] = None):
        from .pubsub import Subscriber
        return Subscriber(self, f"{self.topic_prefixes.topic}/{topic_name}", callback, serializer, message_type)

    def create_service_server(self, service_name: str, callback, 
                             serializer: str = 'json', message_type: Optional[Any] = None):
        from .service import ServiceServer
        return ServiceServer(self, service_name, callback, serializer, message_type)

    def create_service_client(self, service_name: str, serializer: str = 'json', 
                             message_type: Optional[Any] = None):
        from .service import ServiceClient
        return ServiceClient(self, service_name, serializer, message_type)

    def create_action_server(self, action_name: str, 
                           execute_callback,
                           data_serializer: str = 'json'):
        from .action import ActionServer
        return ActionServer(self, action_name, execute_callback, data_serializer)

    def create_action_client(self, action_name: str, data_serializer: str = 'json'):
        from .action import ActionClient
        return ActionClient(self, action_name, data_serializer)