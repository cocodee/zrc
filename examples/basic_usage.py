"""
Basic usage example for ZRC library.
"""

import time
import zrc
import zenoh
import json
def example_usage():
    # Create node
    config_dict = {"mode": "peer", "connect": {"endpoints": ["tcp/localhost:7447"]}}
    config = zenoh.Config()
    # 从配置文件读取 Zenoh 服务器地址
    config.from_json5(json.dumps(config_dict))
    node = zrc.ZRCNode("test_node", config=config)
    
    try:
        # Publisher/Subscriber
        def on_message(data):
            print(f"Received: {data}")
        
        pub = node.create_publisher("test_topic")
        sub = node.create_subscriber("test_topic", on_message)
        
        pub.publish({"hello": "world"})
        
        # Service
        def service_callback(request):
            return {"response": f"Hello {request.get('name', 'World')}"}
        
        server = node.create_service_server("test_service", service_callback)
        client = node.create_service_client("test_service")
        
        result = client.call({"name": "Zenoh"})
        print(f"Service result: {result}")
        
        # Action
        def execute_action(goal_id, goal_data, handle):
            print(f"Executing goal {goal_id} with data {goal_data}")
            for i in range(5):
                if handle.is_cancel_requested():
                    handle.publish_result({"cancelled": True}, zrc.ActionStatus.PREEMPTED)
                    return
                handle.publish_feedback({"progress": i})
                time.sleep(1)
            handle.publish_result({"completed": True}, zrc.ActionStatus.SUCCEEDED)
        
        action_server = node.create_action_server("test_action", execute_action)
        action_client = node.create_action_client("test_action")
        
        def on_feedback(feedback):
            print(f"Feedback: {feedback}")
        
        def on_result(result):
            print(f"Result: {result}")
        
        goal_id = action_client.send_goal(
            {"task": "move_to_position"}, 
            feedback_callback=on_feedback,
            result_callback=on_result
        )
        
        print(f"Sent goal with ID: {goal_id}")
        
        # Wait for a while
        time.sleep(10)
        
    finally:
        node.close()

if __name__ == "__main__":
    example_usage()