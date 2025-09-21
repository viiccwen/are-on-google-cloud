from typing import List, Dict, Any
import vertexai
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration
from config.config import Config
from agent.tools import execute_tool, get_available_tools

vertexai.init(
    project=Config.PROJECT_ID,
    location=Config.LOCATION,
    credentials=Config.get_credentials(),
)


class FunctionCaller:
    def __init__(self):
        self.available_tools = get_available_tools()
        self.tools = self._convert_to_gemini_tools()
        self.model = GenerativeModel(Config.MODEL_NAME, tools=self.tools)

    def _convert_to_gemini_tools(self) -> List[Tool]:
        function_declarations = []

        for tool in self.available_tools:
            name = tool["name"]
            description = tool["description"]
            parameters = tool["parameters"]

            gemini_schema = {
                "type": "object",
                "properties": {},
                "required": parameters.get("required", []),
            }

            if "properties" in parameters:
                for param_name, param_info in parameters["properties"].items():
                    gemini_schema["properties"][param_name] = {
                        "type": param_info.get("type", "string"),
                        "description": param_info.get("description", ""),
                    }

            function_declaration = FunctionDeclaration(
                name=name, description=description, parameters=gemini_schema
            )
            function_declarations.append(function_declaration)

        return [Tool(function_declarations=function_declarations)]

    def _execute_function_calls(
        self, function_calls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        results = []

        for call in function_calls:
            tool_name = call.get("name")
            parameters = call.get("args", {})

            if tool_name not in [tool["name"] for tool in self.available_tools]:
                results.append(
                    {
                        "tool_name": tool_name,
                        "success": False,
                        "error": f"未知的工具: {tool_name}",
                        "result": {},
                    }
                )
                continue

            try:
                result = execute_tool(tool_name, parameters)
                results.append(
                    {
                        "tool_name": tool_name,
                        "success": result.get("success", True),
                        "result": result,
                        "error": result.get("error"),
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "tool_name": tool_name,
                        "success": False,
                        "error": str(e),
                        "result": {},
                    }
                )

        return results

    def _format_function_calls_for_response(
        self, function_calls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        formatted_calls = []
        for call in function_calls:
            formatted_calls.append(
                {"name": call.get("name"), "parameters": call.get("args", {})}
            )
        return formatted_calls

    def process_message(self, message: str) -> Dict[str, Any]:
        try:
            response = self.model.generate_content(
                message,
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 2048,
                },
            )

            function_calls = []
            if response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        function_calls.append(
                            {
                                "name": part.function_call.name,
                                "args": dict(part.function_call.args),
                            }
                        )

            results = []
            if function_calls:
                results = self._execute_function_calls(function_calls)

                if results:
                    function_results_text = "函數調用結果：\n"
                    for result in results:
                        if result["success"]:
                            tool_name = result["tool_name"]
                            tool_result = result["result"]

                            if tool_name == "get_weather":
                                city = tool_result.get("city", "")
                                temp = tool_result.get("temperature", "")
                                condition = tool_result.get("condition", "")
                                function_results_text += (
                                    f"- {city}的天氣是{condition}，溫度{temp}\n"
                                )

                            elif tool_name == "do_math":
                                expression = tool_result.get("expression", "")
                                result_val = tool_result.get("result", "")
                                function_results_text += (
                                    f"- {expression} = {result_val}\n"
                                )

                            elif tool_name == "get_current_time":
                                date = tool_result.get("date", "")
                                time = tool_result.get("time", "")
                                day = tool_result.get("day_of_week", "")
                                function_results_text += (
                                    f"- 今天是{date} {day}，現在時間是{time}\n"
                                )

                            elif tool_name == "calculate_distance":
                                point1 = tool_result.get("point1", [])
                                point2 = tool_result.get("point2", [])
                                distance = tool_result.get("distance", 0)
                                function_results_text += (
                                    f"- 點{point1}到點{point2}的距離是{distance}\n"
                                )
                        else:
                            function_results_text += f"- 執行 {result['tool_name']} 時發生錯誤：{result['error']}\n"

                    final_response = self.model.generate_content(
                        f"基於以下函數調用結果，生成一個自然友好的回應給用戶：\n\n{function_results_text}\n\n請生成一個簡潔、友好的回應，整合這些結果。",
                        generation_config={
                            "temperature": 0.3,
                            "max_output_tokens": 1024,
                        },
                    )
                    final_response_text = final_response.text
                else:
                    final_response_text = "執行完成，但沒有返回結果。"
            else:
                final_response_text = response.text

            return {
                "message": message,
                "function_calls": self._format_function_calls_for_response(
                    function_calls
                ),
                "results": results,
                "response": final_response_text,
                "success": True,
            }

        except Exception as e:
            return {
                "message": message,
                "function_calls": [],
                "results": [],
                "response": f"處理消息時發生錯誤：{str(e)}",
                "success": False,
                "error": str(e),
            }


function_caller = FunctionCaller()
