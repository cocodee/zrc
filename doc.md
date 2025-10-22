# ZRC (Zenoh Robot Control) 库 - 完整文档

## 概述

ZRC (Zenoh Robot Control) 是一个基于 [Zenoh](https://zenoh.io/) 的机器人控制通信库，旨在为机器人应用提供高效、低延迟的分布式通信。该库提供了三种核心通信模式：

- **Publisher/Subscriber (PubSub)**: 用于实时数据流和状态广播
- **Service/Client**: 用于同步请求-响应通信
- **Action/Client**: 用于长时间运行的任务，支持反馈、结果和取消

## 架构设计

### 核心组件

- **ZRCNode**: 核心节点类，管理Zenoh会话和所有通信资源
- **TopicPrefixes**: 主题前缀配置类，支持自定义命名空间
- **ZRCError**: 基础异常类

### 通信模式

所有通信模式都支持多种序列化格式：
- **JSON**: 默认格式，人类可读
- **Protobuf**: 高效的二进制格式
- **Raw**: 原始字节格式

## 安装与依赖

```bash
pip install zenoh
```

## 快速开始

### 基本用法示例

```python
import zenoh_robot_control as zrc

# 1. 创建节点
config = {"mode": "peer", "connect": {"endpoints": ["tcp/localhost:7447"]}}
node = zrc.ZRCNode("my_robot", config=config)

try:
    # 2. 创建发布者和订阅者
    def message_callback(data):
        print(f"Received: {data}")
    
    publisher = node.create_publisher("sensor_data")
    subscriber = node.create_subscriber("sensor_data", message_callback)
    
    # 3. 发送数据
    publisher.publish({"temperature": 25.5, "unit": "celsius"})
    
finally:
    node.close()
```

## 详细API文档

### ZRCNode

#### 构造函数

```python
ZRCNode(node_name: str, 
        config: Optional[Dict] = None, 
        topic_prefixes: Optional[TopicPrefixes] = None)
```

**参数:**
- `node_name` (str): 节点名称，用于标识
- `config` (Optional[Dict]): Zenoh配置字典
- `topic_prefixes` (Optional[TopicPrefixes]): 主题前缀配置

**示例:**
```python
# 使用默认配置
node = ZRCNode("robot_controller")

# 使用自定义配置
config = {
    "mode": "peer",
    "connect": {"endpoints": ["tcp/localhost:7447"]},
    "listen": {"endpoints": ["tcp/0.0.0.0:7447"]}
}
node = ZRCNode("robot_controller", config=config)

# 使用自定义主题前缀
prefixes = zrc.TopicPrefixes(base_prefix="my_robot")
node = ZRCNode("robot_controller", topic_prefixes=prefixes)
```

#### 方法

##### `close()`
关闭Zenoh会话并清理所有资源。

```python
node.close()
```

##### `create_publisher(topic_name: str, serializer: str = 'json') -> Publisher`
创建发布者实例。

**参数:**
- `topic_name` (str): 主题名称（不含前缀）
- `serializer` (str): 序列化格式 ('json', 'protobuf', 'raw')

**返回:** `Publisher` 实例

##### `create_subscriber(topic_name: str, callback: Callable[[Any], None], serializer: str = 'json', message_type: Optional[Any] = None) -> Subscriber`
创建订阅者实例。

**参数:**
- `topic_name` (str): 主题名称（不含前缀）
- `callback` (Callable): 接收到消息时的回调函数
- `serializer` (str): 序列化格式
- `message_type` (Optional[Any]): Protobuf消息类型（仅在protobuf序列化时需要）

**返回:** `Subscriber` 实例

##### `create_service_server(service_name: str, callback: Callable[[Any], Any], serializer: str = 'json', message_type: Optional[Any] = None) -> ServiceServer`
创建服务服务器实例。

**参数:**
- `service_name` (str): 服务名称
- `callback` (Callable): 处理请求的回调函数
- `serializer` (str): 序列化格式
- `message_type` (Optional[Any]): Protobuf消息类型

**返回:** `ServiceServer` 实例

##### `create_service_client(service_name: str, serializer: str = 'json', message_type: Optional[Any] = None) -> ServiceClient`
创建服务客户端实例。

**参数:**
- `service_name` (str): 服务名称
- `serializer` (str): 序列化格式
- `message_type` (Optional[Any]): Protobuf消息类型

**返回:** `ServiceClient` 实例

##### `create_action_server(action_name: str, execute_callback: Callable[[str, Any, ActionHandle], None], data_serializer: str = 'json') -> ActionServer`
创建动作服务器实例。

**参数:**
- `action_name` (str): 动作名称
- `execute_callback` (Callable): 执行动作的回调函数
- `data_serializer` (str): 数据序列化格式

**返回:** `ActionServer` 实例

##### `create_action_client(action_name: str, data_serializer: str = 'json') -> ActionClient`
创建动作客户端实例。

**参数:**
- `action_name` (str): 动作名称
- `data_serializer` (str): 数据序列化格式

**返回:** `ActionClient` 实例

### TopicPrefixes

主题前缀配置类，用于自定义命名空间。

#### 构造函数

```python
TopicPrefixes(base_prefix: str = "zrc")
```

**参数:**
- `base_prefix` (str): 基础前缀，默认为 "zrc"

**生成的前缀:**
- `topic`: `{base_prefix}/topic`
- `service_req`: `{base_prefix}/service/req`
- `service_resp`: `{base_prefix}/service/resp`
- `action_goal`: `{base_prefix}/action/goal`
- `action_feedback`: `{base_prefix}/action/feedback`
- `action_result`: `{base_prefix}/action/result`
- `action_cancel`: `{base_prefix}/action/cancel`

### Publisher

#### 方法

##### `publish(data: Any)`
发布数据到主题。

**参数:**
- `data` (Any): 要发布的数据

### Subscriber

订阅者自动在构造时开始监听，无需额外启动。

### ServiceServer

服务服务器自动在构造时开始监听请求。

### ServiceClient

#### 方法

##### `call(request_data: Any, timeout: float = 5.0) -> Any`
同步调用服务。

**参数:**
- `request_data` (Any): 请求数据
- `timeout` (float): 超时时间（秒）

**返回:** 服务响应数据

**异常:**
- `ServiceError`: 服务调用失败
- `TimeoutError`: 调用超时

### ActionServer

动作服务器自动在构造时开始监听目标请求。

#### 执行回调函数签名

```python
def execute_callback(goal_id: str, goal_data: Any, handle: ActionHandle) -> None
```

- `goal_id` (str): 目标唯一标识符
- `goal_data` (Any): 目标数据
- `handle` (ActionHandle): 操作句柄

### ActionClient

#### 方法

##### `send_goal(goal_data: Any, feedback_callback: Optional[Callable[[Any], None]] = None, result_callback: Optional[Callable[[Any], None]] = None) -> str`
发送目标到动作服务器。

**参数:**
- `goal_data` (Any): 目标数据
- `feedback_callback` (Optional[Callable]): 反馈回调函数
- `result_callback` (Optional[Callable]): 结果回调函数

**返回:** 目标ID (str)

##### `cancel_goal(goal_id: str)`
取消指定的目标。

**参数:**
- `goal_id` (str): 要取消的目标ID

##### `wait_for_result(goal_id: str, timeout: float = 30.0) -> ActionResult`
同步等待目标结果。

**参数:**
- `goal_id` (str): 目标ID
- `timeout` (float): 超时时间（秒）

**返回:** `ActionResult` 实例

### ActionHandle

提供给动作服务器执行回调的接口。

#### 方法

##### `is_cancel_requested() -> bool`
检查是否收到取消请求。

**返回:** True if cancel requested, False otherwise

##### `publish_feedback(feedback_data: Any)`
发布反馈信息。

**参数:**
- `feedback_data` (Any): 反馈数据

##### `publish_result(result_data: Any, status: ActionStatus = ActionStatus.SUCCEEDED)`
发布最终结果。

**参数:**
- `result_data` (Any): 结果数据
- `status` (ActionStatus): 执行状态

### ActionStatus

动作执行状态枚举。

```python
class ActionStatus(Enum):
    PENDING = 0      # 等待执行
    ACTIVE = 1       # 正在执行
    PREEMPTING = 2   # 正在抢占
    SUCCEEDED = 3    # 成功完成
    ABORTED = 4      # 执行失败
    REJECTED = 5     # 请求被拒绝
    PREEMPTED = 6    # 被抢占
    LOST = 7         # 丢失连接
```

### ActionResult

动作结果数据类。

#### 属性

- `goal_id` (str): 目标ID
- `status` (ActionStatus): 执行状态
- `result` (Any): 结果数据

## 高级用法示例

### 1. 自定义序列化

```python
import json

# 使用自定义JSON序列化
node = zrc.ZRCNode("robot")

# 自定义序列化器示例（Protobuf）
class MyMessage:
    def SerializeToString(self):
        # 实现序列化逻辑
        pass
    
    def ParseFromString(self, data):
        # 实现反序列化逻辑
        pass

publisher = node.create_publisher("my_topic", serializer='protobuf')
```

### 2. 错误处理

```python
try:
    result = service_client.call({"command": "move"})
except zrc.ServiceError as e:
    print(f"Service error: {e}")
except TimeoutError:
    print("Service call timed out")
```

### 3. 动作取消

```python
def execute_move(goal_id, goal_data, handle):
    target_position = goal_data["position"]
    
    for step in range(100):
        if handle.is_cancel_requested():
            handle.publish_result({"cancelled": True}, zrc.ActionStatus.PREEMPTED)
            return
        
        # 执行移动步骤
        current_progress = step / 100
        handle.publish_feedback({"progress": current_progress, "target": target_position})
        
        # 模拟移动
        time.sleep(0.1)
    
    handle.publish_result({"reached": target_position}, zrc.ActionStatus.SUCCEEDED)

# 客户端代码
goal_id = action_client.send_goal({"position": [1.0, 2.0, 3.0]})

# 5秒后取消目标
time.sleep(5)
action_client.cancel_goal(goal_id)
```

### 4. 配置网络

```python
# 配置Zenoh网络
config = {
    "mode": "peer",  # 或 "client"
    "connect": {
        "endpoints": ["tcp/192.168.1.100:7447", "tcp/localhost:7447"]
    },
    "listen": {
        "endpoints": ["tcp/0.0.0.0:7447"]
    }
}

node = zrc.ZRCNode("robot", config=config)
```

## 异常处理

### 自定义异常类

- `ZRCError`: 基础异常类
- `ActionError`: 动作相关异常
- `ServiceError`: 服务相关异常

## 性能优化建议

1. **序列化选择**: 对于高频数据流，推荐使用Protobuf或Raw格式
2. **资源管理**: 确保在程序结束时调用`node.close()`
3. **线程安全**: 所有操作都是线程安全的，但避免在回调函数中执行长时间操作
4. **网络配置**: 根据网络环境调整Zenoh配置以获得最佳性能

## 限制与注意事项

1. **Action模式**: 当前实现基于PubSub，不支持原生的请求-响应模式
2. **可靠性**: 依赖Zenoh的可靠性保证，可能需要应用层确认机制
3. **资源清理**: 必须调用`close()`方法清理资源
4. **版本兼容性**: 依赖特定版本的Zenoh Python API

## 故障排除

### 常见问题

1. **连接失败**: 检查Zenoh代理是否运行，网络配置是否正确
2. **资源泄漏**: 确保调用`close()`方法
3. **序列化错误**: 检查数据格式和序列化器配置
4. **线程问题**: 避免在回调中执行长时间阻塞操作

### 调试技巧

```python
# 启用Zenoh日志
import os
os.environ['RUST_LOG'] = 'debug'
```

## 版本历史

- **v1.0**: 初始版本，支持PubSub、Service、Action
- **v1.1**: 修复Action设计，增强错误处理，改进资源管理

---

*本文档基于ZRC库v1.1版本生成*