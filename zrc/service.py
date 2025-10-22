"""
Service implementation for ZRC.
"""

import zenoh
from typing import Any, Callable, Optional, Iterable
from concurrent.futures import TimeoutError
from .core import ZRCNode
from .exceptions import ServiceError, ZRCError

class ServiceServer:
    def __init__(self, session: ZRCNode, service_name: str, callback: Callable[[Any], Any], 
                 serializer: str = 'json', message_type: Optional[Any] = None):
        self.session = session
        self.serializer = serializer
        self.message_type = message_type
        self.service_name = service_name

        def queryable_callback(query: zenoh.Query):
            try:
                # 关键修改 1: 使用 .to_bytes() 获取 payload 的原始字节
                request_payload_bytes = query.payload.to_bytes()
                request_data = session._deserialize(request_payload_bytes, serializer, message_type)
                
                response_data = callback(request_data)
                response_payload = session._serialize(response_data, serializer)
                query.reply(query.key_expr, response_payload)
            except Exception as e:
                print(f"Service server error for {service_name}: {e}")
                # Can choose to return error information
                error_response = {"error": str(e)}
                error_payload = session._serialize(error_response, serializer)
                query.reply(query.key_expr, error_payload )

        key = f"{session.topic_prefixes.service_req}/{service_name}"
        self._queryable: zenoh.Queryable = session.session.declare_queryable(key, queryable_callback)

        session._add_resource(self._queryable)

class ServiceClient:
    def __init__(self, session: ZRCNode, service_name: str, serializer: str = 'json', 
                 message_type: Optional[Any] = None):
        self.session = session
        self.key = f"{session.topic_prefixes.service_req}/{service_name}"
        self.serializer = serializer
        self.message_type = message_type

    def call(self, request_data: Any, timeout: float = 5.0) -> Any:
        payload = self.session._serialize(request_data, self.serializer)
        
        try:
            results: Iterable[zenoh.Result] = self.session.session.get(self.key, payload=payload, timeout=timeout)
            
            for sample_result in results:
                # 关键修改 2: 检查结果是成功 (ok) 还是失败 (err)
                if sample_result.ok:
                    sample = sample_result.ok
                    
                    # 关键修改 3: 使用 .to_bytes() 获取 payload 的原始字节
                    data_bytes = sample.payload.to_bytes()
                    data = self.session._deserialize(data_bytes, self.serializer, self.message_type)
                    
                    # Check if it's an error response
                    if isinstance(data, dict) and "error" in data:
                        # 确保这里抛出的是应用程序级别的错误
                        raise ServiceError(f"Remote service responded with application error: {data['error']}")
                    return data
                
                elif sample_result.err:
                    # 处理 Zenoh 传输或查询失败的错误
                    raise ServiceError(f"Zenoh query failed with error: {sample_result.err}")

            # If the loop finishes without returning, it means no replies were received
            raise TimeoutError(f"Service call to {self.key} timed out or returned no results.")
        
        except zenoh.ZError as e:
            raise ServiceError(f"Zenoh error during service call: {e}")
        except TimeoutError:
            # 重新抛出超时错误
            raise
        except ServiceError:
            # 重新抛出 ServiceError，避免被通用 Exception 捕获
            raise
        except Exception as e:
            raise ServiceError(f"Service call failed: {type(e).__name__}: {e}")