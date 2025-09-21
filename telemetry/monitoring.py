from datetime import datetime
import json
import time
from typing import Dict, Any, Optional
from google.cloud import monitoring_v3
from google.cloud.monitoring_v3 import query
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import timezone
from config.config import Config


class CloudMonitoring:
    def __init__(self):
        self.client = monitoring_v3.MetricServiceClient(credentials=Config.get_credentials())
        self.project_name = f"projects/{Config.PROJECT_ID}"

    def create_custom_metric(
        self, metric_type: str, display_name: str, description: str
    ):
        descriptor = monitoring_v3.MetricDescriptor(
            type=metric_type,
            metric_kind=monitoring_v3.MetricDescriptor.MetricKind.GAUGE,
            value_type=monitoring_v3.MetricDescriptor.ValueType.DOUBLE,
            description=description,
            display_name=display_name,
        )

        try:
            descriptor = self.client.create_metric_descriptor(
                name=self.project_name, descriptor=descriptor
            )
            print(f"Created metric descriptor: {descriptor.name}")
        except Exception as e:
            print(f"Metric descriptor may already exist: {e}")

    def _safe_float(self, value: Any) -> float:
        """Convert value to float safely"""
        if isinstance(value, float):
            return value
        if isinstance(value, int):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                print(f"[WARN] Cannot convert string '{value}' to float")
                return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            print(f"[WARN] Cannot convert {type(value).__name__} '{value}' to float")
            return 0.0

    def write_time_series(
        self, metric_type: str, value: float, labels: Dict[str, str] = None
    ):
        """write time series data"""
        if labels is None:
            labels = {}

        series = monitoring_v3.TimeSeries()
        series.metric.type = metric_type
        series.resource.type = "global"

        # add labels
        for key, value in labels.items():
            series.metric.labels[key] = str(value)

        # create data point
        point = monitoring_v3.Point()
        num_value = self._safe_float(value)
        point.value.double_value = num_value

        now = datetime.now(timezone.utc)
        point.interval = monitoring_v3.TimeInterval(start_time=now, end_time=now)
        
        series.points = [point]

        try:
            self.client.create_time_series(name=self.project_name, time_series=[series])
        except Exception as e:
            print(f"Failed to write time series: {e}")

    def log_function_call_metrics(
        self,
        function_name: str,
        success: bool,
        duration: float,
        user_id: str = None,
        error_type: str = None,
    ):
        """log function call metrics"""
        labels = {
            "function_name": function_name,
            "success": str(success),
            "user_id": user_id or "anonymous",
        }

        if error_type:
            labels["error_type"] = error_type

        # log call count
        self.write_time_series(
            "custom.googleapis.com/function_calls/count", 1.0, labels
        )

        # log execution time
        self.write_time_series(
            "custom.googleapis.com/function_calls/duration", duration, labels
        )

    def log_rag_metrics(
        self,
        query: str,
        documents_found: int,
        response_time: float,
        user_id: str = None,
    ):
        """記錄 RAG 查詢指標"""
        labels = {"user_id": user_id or "anonymous", "query_length": str(len(query))}

        # 記錄查詢次數
        self.write_time_series("custom.googleapis.com/rag/queries/count", 1.0, labels)

        # 記錄找到的文檔數量
        self.write_time_series(
            "custom.googleapis.com/rag/documents_found", float(documents_found), labels
        )

        # 記錄響應時間
        self.write_time_series(
            "custom.googleapis.com/rag/response_time", response_time, labels
        )


# 創建全局實例
monitoring = CloudMonitoring()
