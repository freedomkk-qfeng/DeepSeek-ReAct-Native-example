from deepseek_agent import DeepSeekAgent
from config import API_CONFIG

# --- Tool Definitions ---
def calculate(num1, num2, operator):
    """Perform basic arithmetic operations"""
    try:
        n1 = float(num1)
        n2 = float(num2)
    except ValueError:
        return "Error: Invalid numbers"

    if operator == '+':
        return str(n1 + n2)
    elif operator == '-':
        return str(n1 - n2)
    elif operator == '*':
        return str(n1 * n2)
    elif operator == '/':
        if n2 == 0:
            return "Error: Division by zero"
        return str(n1 / n2)
    else:
        return f"Error: Unsupported operator {operator}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Performs basic arithmetic operations (add, subtract, multiply, divide). Use this tool for every step of the calculation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "num1": {"type": "number", "description": "The first number"},
                    "num2": {"type": "number", "description": "The second number"},
                    "operator": {"type": "string", "enum": ["+", "-", "*", "/"], "description": "The operator"}
                },
                "required": ["num1", "num2", "operator"]
            }
        }
    }
]

TOOL_MAP = {"calculate": calculate}

# --- Main Program ---
if __name__ == "__main__":
    agent = DeepSeekAgent(**API_CONFIG)
    
    expression = "(32 + 54) * 12 - 15 / 3"
    print(f"\n{'='*20} Testing Expression: {expression} {'='*20}")
    messages = [
        {"role": "user", "content": f"请计算以下表达式的结果：{expression}。请在每一步都使用 calculate 工具。"}
    ]
    agent.run(messages, tools, TOOL_MAP)
