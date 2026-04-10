"""
Calculator Tool - Mathematical calculations
"""
import math
from tools.base import Tool, ToolResult


class CalculatorTool(Tool):
    """Perform mathematical calculations"""

    @property
    def name(self) -> str:
        return "calculate"

    @property
    def description(self) -> str:
        return "Perform mathematical calculations. Supports: add, subtract, multiply, divide, sqrt, power, sin, cos, tan"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide", "sqrt", "power", "sin", "cos", "tan"],
                    "description": "Mathematical operation"
                },
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number (not needed for sqrt, sin, cos, tan)"}
            },
            "required": ["operation", "a"]
        }

    def execute(self, operation: str, a: float, b: float = None) -> ToolResult:
        try:
            operations = {
                "add": lambda x, y: x + y,
                "subtract": lambda x, y: x - y,
                "multiply": lambda x, y: x * y,
                "divide": lambda x, y: x / y if y != 0 else "Error: Division by zero",
                "sqrt": lambda x, y: math.sqrt(x),
                "power": lambda x, y: math.pow(x, y),
                "sin": lambda x, y: math.sin(math.radians(x)),
                "cos": lambda x, y: math.cos(math.radians(x)),
                "tan": lambda x, y: math.tan(math.radians(x)),
            }

            func = operations.get(operation)
            if not func:
                return ToolResult(success=False, output=None, error=f"Unknown operation: {operation}")

            result = func(a, b) if b is not None else func(a, None)

            if isinstance(result, str):  # Error message
                return ToolResult(success=False, output=None, error=result)

            return ToolResult(success=True, output=result)

        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))
