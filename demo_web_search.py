import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from deepseek_agent import DeepSeekAgent
from config import API_CONFIG
import datetime

# --- Tool Implementation ---
def get_current_time():
    """Get the current date and time"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

def visit_page(url):
    """Visit a webpage and extract its main text content"""
    print(f"[*] Visiting: {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for script in soup(["script", "style", "noscript", "iframe", "svg"]):
            script.extract()

        # Handle links: Convert <a> tags to Markdown format [Text](URL)
        for a in soup.find_all('a', href=True):
            text = a.get_text(strip=True)
            if text:
                href = a['href']
                full_url = urljoin(url, href)
                a.replace_with(f" [{text}]({full_url}) ")

        text = soup.get_text(separator='\n')
        lines = (line.strip() for line in text.splitlines())
        text = '\n'.join(line for line in lines if line)
        
        return text[:50000] + ("\n...(content truncated)..." if len(text) > 50000 else "")
        
    except Exception as e:
        return f"Error visiting page: {str(e)}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "visit_page",
            "description": "Visits a specified URL and returns the text content of the web page. Use this to retrieve information from websites.",
            "parameters": {
                "type": "object", 
                "properties": {
                    "url": {"type": "string", "description": "The URL of the web page to visit. Must start with http:// or https://"}
                }, 
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Gets the current date and time. Use this when the question involves relative time concepts like 'today', 'this year', or 'next year'.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Performs basic arithmetic operations (add, subtract, multiply, divide). Use this tool for calculations, such as calculating years or age.",
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

TOOL_MAP = {"visit_page": visit_page, "get_current_time": get_current_time, "calculate": calculate}

# --- Main Program ---
if __name__ == "__main__":
    agent = DeepSeekAgent(**API_CONFIG)
    
    question = "明年是计算机系成立多少周年？"
    print(f"\n{'='*20} Starting Web Research Task {'='*20}")
    print(f"Task Goal: {question}")
    
    messages = [
        {"role": "user", "content": f"请帮我回答这个问题：{question}。你可以使用 visit_page 工具来访问网页。建议先访问华东师范大学的主页 (https://www.ecnu.edu.cn/) 寻找线索。"}
    ]
    
    agent.run(messages, tools, TOOL_MAP, max_turns=15)
