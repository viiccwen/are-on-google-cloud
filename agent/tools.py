import math
import random
from typing import Dict, Any, List
from datetime import datetime


def get_weather(city: str, country: str = "Taiwan") -> Dict[str, Any]:
    weather_conditions = ["晴天", "多雲", "陰天", "小雨", "大雨", "雷陣雨"]
    temperature = random.randint(15, 35)
    humidity = random.randint(40, 90)
    condition = random.choice(weather_conditions)

    return {
        "city": city,
        "country": country,
        "temperature": f"{temperature}°C",
        "condition": condition,
        "humidity": f"{humidity}%",
        "timestamp": datetime.now().isoformat(),
        "source": "模擬天氣服務",
    }


def do_math(expression: str) -> Dict[str, Any]:
    try:
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            raise ValueError("表達式包含不允許的字符")

        result = eval(expression)

        return {
            "expression": expression,
            "result": result,
            "success": True,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "expression": expression,
            "error": str(e),
            "success": False,
            "timestamp": datetime.now().isoformat(),
        }


def get_current_time(timezone: str = "Asia/Taipei") -> Dict[str, Any]:
    now = datetime.now()

    return {
        "timezone": timezone,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "datetime": now.isoformat(),
        "day_of_week": now.strftime("%A"),
        "timestamp": now.timestamp(),
    }


def calculate_distance(point1: List[float], point2: List[float]) -> Dict[str, Any]:
    try:
        if len(point1) != 2 or len(point2) != 2:
            raise ValueError("座標點必須包含 x 和 y 兩個值")

        x1, y1 = point1
        x2, y2 = point2
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        return {
            "point1": point1,
            "point2": point2,
            "distance": round(distance, 2),
            "success": True,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "point1": point1,
            "point2": point2,
            "error": str(e),
            "success": False,
            "timestamp": datetime.now().isoformat(),
        }


TOOLS = {
    "get_weather": {
        "function": get_weather,
        "description": "獲取指定城市的天氣資訊",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市名稱"},
                "country": {"type": "string", "description": "國家名稱，預設為台灣"},
            },
            "required": ["city"],
        },
    },
    "do_math": {
        "function": do_math,
        "description": "執行數學運算",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "數學表達式"}
            },
            "required": ["expression"],
        },
    },
    "get_current_time": {
        "function": get_current_time,
        "description": "獲取當前時間",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {"type": "string", "description": "時區，預設為台北時區"}
            },
            "required": [],
        },
    },
    "calculate_distance": {
        "function": calculate_distance,
        "description": "計算兩點之間的距離",
        "parameters": {
            "type": "object",
            "properties": {
                "point1": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "第一個點的座標 [x, y]",
                },
                "point2": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "第二個點的座標 [x, y]",
                },
            },
            "required": ["point1", "point2"],
        },
    },
}


def execute_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    if tool_name not in TOOLS:
        return {
            "error": f"未知的工具: {tool_name}",
            "success": False,
            "timestamp": datetime.now().isoformat(),
        }

    try:
        tool_func = TOOLS[tool_name]["function"]
        result = tool_func(**parameters)
        return result
    except Exception as e:
        return {
            "error": f"執行工具時發生錯誤: {str(e)}",
            "success": False,
            "timestamp": datetime.now().isoformat(),
        }


def get_available_tools() -> List[Dict[str, Any]]:
    return [
        {
            "name": name,
            "description": tool["description"],
            "parameters": tool["parameters"],
        }
        for name, tool in TOOLS.items()
    ]
