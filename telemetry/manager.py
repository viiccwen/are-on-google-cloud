import time
import uuid
from typing import Dict, Any, Optional, Callable
from functools import wraps
from .monitoring import monitoring
from .logging import cloud_logger


class TelemetryManager:
    def __init__(self):
        self.monitoring = monitoring
        self.logger = cloud_logger

    def track_function_call(self, function_name: str, user_id: str = None):
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                request_id = str(uuid.uuid4())

                try:
                    # execute function
                    result = func(*args, **kwargs)

                    # calculate execution time
                    duration = time.time() - start_time

                    # log success metrics
                    self.monitoring.log_function_call_metrics(
                        function_name=function_name,
                        success=True,
                        duration=duration,
                        user_id=user_id,
                    )

                    # log detailed log
                    self.logger.log_function_call(
                        function_name=function_name,
                        parameters=kwargs,
                        result=(
                            result if isinstance(result, dict) else {"result": result}
                        ),
                        duration=duration,
                        user_id=user_id,
                    )

                    return result

                except Exception as e:
                    # calculate execution time
                    duration = time.time() - start_time

                    # log error metrics
                    self.monitoring.log_function_call_metrics(
                        function_name=function_name,
                        success=False,
                        duration=duration,
                        user_id=user_id,
                        error_type=type(e).__name__,
                    )

                    # log error log
                    self.logger.log_error(
                        error=e,
                        context={
                            "function_name": function_name,
                            "parameters": kwargs,
                            "request_id": request_id,
                        },
                        user_id=user_id,
                    )

                    raise

            return wrapper

        return decorator

    def track_rag_query(self, user_id: str = None):
        """追蹤 RAG 查詢的裝飾器"""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                request_id = str(uuid.uuid4())

                try:
                    # 執行查詢
                    result = func(*args, **kwargs)

                    # 計算執行時間
                    duration = time.time() - start_time

                    # 提取查詢和文檔信息
                    query = kwargs.get("query", "")
                    documents = (
                        result.get("documents", []) if isinstance(result, dict) else []
                    )

                    # 記錄 RAG 指標
                    self.monitoring.log_rag_metrics(
                        query=query,
                        documents_found=len(documents),
                        response_time=duration,
                        user_id=user_id,
                    )

                    # 記錄詳細日誌
                    self.logger.log_rag_query(
                        query=query,
                        documents=documents,
                        response_time=duration,
                        user_id=user_id,
                    )

                    return result

                except Exception as e:
                    # 計算執行時間
                    duration = time.time() - start_time

                    # 記錄錯誤
                    self.logger.log_error(
                        error=e,
                        context={
                            "operation": "rag_query",
                            "query": kwargs.get("query", ""),
                            "request_id": request_id,
                        },
                        user_id=user_id,
                    )

                    raise

            return wrapper

        return decorator

    def log_user_interaction(
        self, user_id: str, action: str, details: Dict[str, Any] = None
    ):
        """記錄用戶互動"""
        self.logger.log_user_interaction(user_id, action, details)

    def log_performance(
        self,
        operation: str,
        duration: float,
        metrics: Dict[str, Any] = None,
        user_id: str = None,
    ):
        """記錄性能指標"""
        self.logger.log_performance_metrics(operation, duration, metrics, user_id)


# 創建全局實例
telemetry = TelemetryManager()
