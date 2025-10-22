"""
ZRC (Zenoh Robot Control) Library

A communication library for robotics based on Zenoh, providing:
- Publisher/Subscriber (PubSub) patterns
- Service/Client communication
- Action/Client patterns with feedback and cancellation
"""

from .core import ZRCNode, TopicPrefixes
from .exceptions import ZRCError, ServiceError, ActionError
from .pubsub import Publisher, Subscriber
from .service import ServiceServer, ServiceClient
from .action import ActionServer, ActionClient, ActionHandle, ActionStatus, ActionResult, ActionFeedback

__version__ = "1.1.0"
__author__ = "ZRC Contributors"