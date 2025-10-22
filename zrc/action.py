"""
Action implementation for ZRC.
"""

import zenoh
import json
import time
import threading
import uuid
from typing import Any, Callable, Dict, Optional, Union
from concurrent.futures import Future, TimeoutError
from dataclasses import dataclass
from enum import Enum
from .core import ZRCNode
from .exceptions import ActionError, ZRCError

class ActionStatus(Enum):
    PENDING = 0
    ACTIVE = 1
    PREEMPTING = 2
    SUCCEEDED = 3
    ABORTED = 4
    REJECTED = 5
    PREEMPTED = 6
    LOST = 7

@dataclass
class ActionResult:
    goal_id: str
    status: ActionStatus
    result: Any

@dataclass
class ActionFeedback:
    goal_id: str
    feedback: Any

class ActionHandle:
    """Provides interface for ActionServer callback functions to publish feedback, results and manage cancellation status."""
    def __init__(self, session: ZRCNode, goal_id: str, action_name: str, 
                 feedback_prefix: str, result_prefix: str, serializer: str = 'json'):
        self.session = session
        self.goal_id = goal_id
        self.action_name = action_name
        self.serializer = serializer
        
        # Thread event: used to signal execution thread that goal has been cancelled
        self._cancel_event = threading.Event() 
        
        # Zenoh publishers
        feedback_key = f"{feedback_prefix}/{goal_id}"
        result_key = f"{result_prefix}/{goal_id}"
        self._feedback_pub = session.create_publisher(feedback_key, serializer='json') 
        self._result_pub = session.create_publisher(result_key, serializer='json') 

    def set_cancel_requested(self):
        """Called by ActionServer to notify execution thread of cancellation request."""
        self._cancel_event.set()

    def is_cancel_requested(self) -> bool:
        """Allows ActionServer's execute_callback to check if stopping is needed."""
        return self._cancel_event.is_set()
        
    def publish_feedback(self, feedback_data: Any):
        """Publish feedback information."""
        msg = {"goal_id": self.goal_id, "data": feedback_data, "timestamp": time.time()}
        self._feedback_pub.publish(msg)

    def publish_result(self, result_data: Any, status: ActionStatus = ActionStatus.SUCCEEDED):
        """Publish final result."""
        msg = {
            "goal_id": self.goal_id, 
            "data": result_data, 
            "status": status.value,
            "timestamp": time.time()
        }
        self._result_pub.publish(msg)

class ActionServer:
    def __init__(self, session: ZRCNode, action_name: str, 
                 execute_callback: Callable[[str, Any, ActionHandle], None],
                 data_serializer: str = 'json'):
        
        self.session = session
        self.action_name = action_name
        self.execute_callback = execute_callback
        self.data_serializer = data_serializer
        
        # Store current active ActionHandle instances
        self._active_goals: Dict[str, ActionHandle] = {} 
        self._lock = threading.Lock()  # Thread safety
        
        self._feedback_prefix = f"{session.topic_prefixes.action_feedback}/{action_name}"
        self._result_prefix = f"{session.topic_prefixes.action_result}/{action_name}"

        # 1. Subscribe to goal requests (Goal)
        self.session.create_subscriber(
            f"{session.topic_prefixes.action_goal}/{action_name}", 
            self._handle_goal,
            serializer='json'
        )
        
        # 2. Subscribe to cancellation requests (Cancel)
        self.session.create_subscriber(
            f"{session.topic_prefixes.action_cancel}/{action_name}", 
            self._handle_cancel,
            serializer='json'
        )
    
    def _handle_goal(self, goal_msg: Dict):
        goal_id = goal_msg.get("goal_id")
        goal_data = goal_msg.get("data")
        
        if not goal_id:
            print(f"[{self.action_name} Server] Invalid goal message: missing goal_id")
            return
            
        handle = ActionHandle(
            self.session, goal_id, self.action_name,
            self._feedback_prefix, self._result_prefix, 
            self.data_serializer
        )
        
        with self._lock:
            self._active_goals[goal_id] = handle
        
        # Start execution thread
        t = threading.Thread(target=self._run_execute, args=(goal_id, goal_data, handle))
        t.daemon = True
        t.start()
    
    def _run_execute(self, goal_id: str, goal_data: Any, handle: ActionHandle):
        """Wrap execution callback, ensure cleanup after completion"""
        try:
            self.execute_callback(goal_id, goal_data, handle)
        except Exception as e:
            print(f"Action execution failed for {goal_id}: {e}")
            handle.publish_result({"error": str(e)}, ActionStatus.ABORTED)
        finally:
            with self._lock:
                self._active_goals.pop(goal_id, None)

    def _handle_cancel(self, cancel_msg: Dict):
        goal_id_to_cancel = cancel_msg.get("goal_id") 

        if not goal_id_to_cancel:
            print(f"[{self.action_name} Server] Invalid cancel message: missing goal_id")
            return

        with self._lock:
            if goal_id_to_cancel in self._active_goals:
                handle = self._active_goals[goal_id_to_cancel]
                print(f"[{self.action_name} Server] Received cancel request, Goal ID: {goal_id_to_cancel[:8]}...")
                handle.set_cancel_requested()
            else:
                print(f"[{self.action_name} Server] Cancel request for non-existent goal: {goal_id_to_cancel}")

class ActionClient:
    def __init__(self, session: ZRCNode, action_name: str, data_serializer: str = 'json'):
        self.session = session
        self.action_name = action_name
        self.data_serializer = data_serializer
        
        # Publishers
        self._goal_pub = session.create_publisher(f"{session.topic_prefixes.action_goal}/{action_name}", serializer='json')
        self._cancel_pub = session.create_publisher(f"{session.topic_prefixes.action_cancel}/{action_name}", serializer='json')
        
        # Store goal-related callbacks
        self._goal_callbacks: Dict[str, Dict[str, Optional[Callable]]] = {}
        self._subscribers: Dict[str, Any] = {}  # Using Any to avoid circular import issues

    def send_goal(self, goal_data: Any, 
                  feedback_callback: Optional[Callable[[Any], None]] = None,
                  result_callback: Optional[Callable[[Any], None]] = None) -> str:
        
        goal_id = str(uuid.uuid4())  # Use uuid4 instead of uuid
        
        # Create subscribers
        if feedback_callback:
            feedback_key = f"{self.session.topic_prefixes.action_feedback}/{self.action_name}/{goal_id}"
            feedback_sub = self.session.create_subscriber(feedback_key, feedback_callback, serializer='json')
            self._subscribers[f"feedback_{goal_id}"] = feedback_sub
            
        if result_callback:
            result_key = f"{self.session.topic_prefixes.action_result}/{self.action_name}/{goal_id}"
            result_sub = self.session.create_subscriber(result_key, result_callback, serializer='json')
            self._subscribers[f"result_{goal_id}"] = result_sub
        
        # Store callback references
        self._goal_callbacks[goal_id] = {
            'feedback': feedback_callback,
            'result': result_callback
        }
        
        # Publish goal
        goal_msg = {"goal_id": goal_id, "data": goal_data, "timestamp": time.time()}
        self._goal_pub.publish(goal_msg)
        
        return goal_id

    def cancel_goal(self, goal_id: str):
        """Send request to server to cancel specific goal."""
        cancel_msg = {"goal_id": goal_id, "timestamp": time.time()}
        self._cancel_pub.publish(cancel_msg)
        
        # Clean up related subscribers
        for key_type in ['feedback', 'result']:
            key = f"{key_type}_{goal_id}"
            if key in self._subscribers:
                try:
                    self._subscribers[key]._subscriber.undeclare()
                except:
                    pass
                del self._subscribers[key]

    def wait_for_result(self, goal_id: str, timeout: float = 30.0) -> ActionResult:
        """Synchronously wait for result"""
        future = Future()
        result_received = threading.Event()
        
        def result_handler(data):
            if isinstance(data, dict) and data.get("goal_id") == goal_id:
                status = ActionStatus(data.get("status", ActionStatus.SUCCEEDED.value))
                result = ActionResult(goal_id=goal_id, status=status, result=data.get("data"))
                future.set_result(result)
                result_received.set()
        
        # Create temporary subscriber
        result_key = f"{self.session.topic_prefixes.action_result}/{self.action_name}/{goal_id}"
        temp_sub = self.session.create_subscriber(result_key, result_handler, serializer='json')
        
        try:
            if result_received.wait(timeout):
                return future.result(timeout=0.1)
            else:
                raise TimeoutError(f"Timeout waiting for result of goal {goal_id}")
        finally:
            try:
                temp_sub._subscriber.undeclare()
            except:
                pass