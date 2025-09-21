import json
import logging
import traceback
from typing import Dict, Any
from datetime import datetime
from google.cloud import logging as cloud_logging
from config.config import Config


class CloudLogger:
    """Google Cloud Logging client"""

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # initialize Cloud Logging
        try:
            self.cloud_client = cloud_logging.Client(project=Config.PROJECT_ID, credentials=Config.get_credentials())
            self.cloud_client.setup_logging()
            self.cloud_logger = self.cloud_client.logger("are-rag-api")
        except Exception as e:
            print(f"Failed to initialize Cloud Logging: {e}")
            self.cloud_logger = None

    def _create_log_entry(
        self, level: str, message: str, extra_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """create standardized log entry"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "service": "are-rag-api",
            "version": "1.0.0",
        }

        if extra_data:
            log_entry.update(extra_data)

        return log_entry

    def log_function_call(
        self,
        function_name: str,
        parameters: Dict[str, Any],
        result: Dict[str, Any],
        duration: float,
        user_id: str = None,
    ):
        """log function call details"""
        log_data = {
            "event_type": "function_call",
            "function_name": function_name,
            "parameters": parameters,
            "result": result,
            "duration_ms": duration * 1000,
            "user_id": user_id or "anonymous",
            "success": result.get("success", True),
        }

        log_entry = self._create_log_entry(
            "INFO", f"Function call: {function_name}", log_data
        )

        # local log
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))

        # Cloud Logging
        if self.cloud_logger:
            try:
                self.cloud_logger.log_struct(log_entry, severity="INFO")
            except Exception as e:
                print(f"Failed to log to Cloud Logging: {e}")

    def log_rag_query(
        self, query: str, documents: list, response_time: float, user_id: str = None
    ):
        """log RAG query details"""
        log_data = {
            "event_type": "rag_query",
            "query": query,
            "documents_count": len(documents),
            "documents": documents,
            "response_time_ms": response_time * 1000,
            "user_id": user_id or "anonymous",
        }

        log_entry = self._create_log_entry("INFO", f"RAG query processed", log_data)

        # local log
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))

        # Cloud Logging
        if self.cloud_logger:
            try:
                self.cloud_logger.log_struct(log_entry, severity="INFO")
            except Exception as e:
                print(f"Failed to log to Cloud Logging: {e}")

    def log_error(
        self, error: Exception, context: Dict[str, Any] = None, user_id: str = None
    ):
        """log error information"""
        log_data = {
            "event_type": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "user_id": user_id or "anonymous",
        }

        if context:
            log_data["context"] = context

        log_entry = self._create_log_entry(
            "ERROR", f"Error occurred: {str(error)}", log_data
        )

        # local log
        self.logger.error(json.dumps(log_entry, ensure_ascii=False))

        # Cloud Logging
        if self.cloud_logger:
            try:
                self.cloud_logger.log_struct(log_entry, severity="ERROR")
            except Exception as e:
                print(f"Failed to log error to Cloud Logging: {e}")

    def log_user_interaction(
        self, user_id: str, action: str, details: Dict[str, Any] = None
    ):
        """log user interaction"""
        log_data = {
            "event_type": "user_interaction",
            "user_id": user_id,
            "action": action,
        }

        if details:
            log_data["details"] = details

        log_entry = self._create_log_entry(
            "INFO", f"User interaction: {action}", log_data
        )

        # local log
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))

        # Cloud Logging
        if self.cloud_logger:
            try:
                self.cloud_logger.log_struct(log_entry, severity="INFO")
            except Exception as e:
                print(f"Failed to log to Cloud Logging: {e}")

    def log_performance_metrics(
        self,
        operation: str,
        duration: float,
        metrics: Dict[str, Any] = None,
        user_id: str = None,
    ):
        """log performance metrics"""
        log_data = {
            "event_type": "performance",
            "operation": operation,
            "duration_ms": duration * 1000,
            "user_id": user_id or "anonymous",
        }

        if metrics:
            log_data["metrics"] = metrics

        log_entry = self._create_log_entry(
            "INFO", f"Performance: {operation}", log_data
        )

        # local log
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))

        # Cloud Logging
        if self.cloud_logger:
            try:
                self.cloud_logger.log_struct(log_entry, severity="INFO")
            except Exception as e:
                print(f"Failed to log to Cloud Logging: {e}")


# 創建全局實例
cloud_logger = CloudLogger()
