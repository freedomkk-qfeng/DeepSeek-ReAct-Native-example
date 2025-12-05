# DeepSeek-ReAct-Native-example

[中文版本](README.md)

A Python example project showcasing the capabilities of **DeepSeek-V3.2** models combining "Thinking Mode" (Reasoning) with **Tool Calling**.

This project aims to demonstrate an AI Agent example capable of complex logical reasoning, multi-step planning, and autonomous tool calling, based on the DeepSeek-V3.2 feature.

## ✨ Features

*   **Pure Python Implementation**: Minimal dependencies (only `openai` SDK and basic web libraries), no complex Agent framework dependencies.
*   **Modular Design**: Core Agent logic is separated from specific scenarios, making it easy to extend.
*   **Dual Mode Support**: Supports both DeepSeek Official API and Local Deployment (vLLM/SGLang).
*   **Rich Examples**: Includes scenarios for math calculation, text adventure games, and web research.

## 📂 Project Structure

```text
DeepSeek-ReAct-Native-example/
├── config.py           # Configuration (API Key, Base URL, Thinking Params)
├── deepseek_agent.py   # Core Agent Class (Handles reasoning flow & tool loops)
├── demo_math.py        # Demo 1: Math Calculator (Step-by-step arithmetic reasoning)
├── demo_adventure.py   # Demo 2: Text Adventure Game (Spatial reasoning & state tracking)
└── demo_web_search.py  # Demo 3: Web Search Agent (RAG, Time awareness & Calculation)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install openai requests beautifulsoup4
```

### 2. Configure API

Copy `config_example.py` to `config.py`, then enter your API Key:

*   **Official API**: Default configuration, just fill in your `api_key`.
*   **Local Deployment**: Comment out the official config, uncomment the local deployment config, and update `base_url`.

### 3. Run Demos

**Demo 1: Math Calculator**
The model decomposes complex arithmetic problems step-by-step and uses a calculator tool to solve them.
```bash
python demo_math.py
```
<details>
<summary>Click to view actual execution result</summary>

```text
==================== Testing Expression: (32 + 54) * 12 - 15 / 3 ====================
[*] Agent started with model: deepseek-v32

--- Turn 1 ---
[Thinking Process]:
I need to calculate the expression (32 + 54) * 12 - 15 / 3. I must ensure to use the calculator tool for every step.
First, calculate the addition inside the parentheses: 32 + 54.
[Tool Call]: calculate({"num1": 32, "num2": 54, "operator": "+"})
[Tool Result]: 86.0

--- Turn 2 ---
[Thinking Process]:
Now we have (86) * 12 - 15 / 3. Next, calculate 86 * 12.
[Tool Call]: calculate({"num1": 86, "num2": 12, "operator": "*"})
[Tool Result]: 1032.0

--- Turn 3 ---
[Thinking Process]:
Now calculate 15 / 3.
[Tool Call]: calculate({"num1": 15, "num2": 3, "operator": "/"})
[Tool Result]: 5.0

--- Turn 4 ---
[Thinking Process]:
Now the expression becomes 1032 - 5.
[Tool Call]: calculate({"num1": 1032, "num2": 5, "operator": "-"})
[Tool Result]: 1027.0

--- Turn 5 ---
[Thinking Process]:
Therefore, the result is 1027.
[Final Content]:
Expression: (32 + 54) * 12 - 15 / 3.
Final Result: 1027
```
</details>

**Demo 2: Text Adventure Game**
The model plays a game, using tools to look, move, take items, and unlock doors to escape a room. It draws a map based on game feedback.
```bash
python demo_adventure.py
```
<details>
<summary>Click to view actual execution result</summary>

```text
==================== Starting Text Adventure Game ====================
Goal: Escape from this place!
[*] Agent started with model: deepseek-v32

--- Turn 1 ---
[Thinking Process]:
I first need to observe the current environment using the look tool.
[Tool Call]: look({})
[Tool Result]:
You are in a dimly lit stone room... Exits: north.
Map:
      [Exit] -X- [Hallway] --- [Storage]
                     |
                 [Start]*

--- Turn 2 ---
[Thinking Process]:
I see a map... I'll try moving north to see what happens.
[Tool Call]: move({"direction": "north"})
[Tool Result]:
You move north.
You are standing in a long hallway. To the west is a huge iron door...

--- Turn 3 ---
[Thinking Process]:
I am now in the Hallway... I'll check what's to the east.
[Tool Call]: move({"direction": "east"})
[Tool Result]:
You move east.
This is a cluttered storage room... There is: key.

--- Turn 4 ---
[Thinking Process]:
Great! There is a key in the storage room. I pick it up.
[Tool Call]: take({"item": "key"})
[Tool Result]: You picked up key.

--- Turn 5 ---
[Thinking Process]:
Now I have the key... Move west back to Hallway.
[Tool Call]: move({"direction": "west"})
[Tool Result]: You move west...

--- Turn 6 ---
[Thinking Process]:
Now I'm back in Hallway... Let me try unlocking the west door.
[Tool Call]: unlock({"direction": "west"})
[Tool Result]: You unlocked the west door with the key!

--- Turn 7 ---
[Thinking Process]:
The door is open! Now I can move west.
[Tool Call]: move({"direction": "west"})
[Tool Result]: You successfully escaped! Sunlight hits your face. Congratulations!
```
</details>

**Demo 3: Web Research Agent**
Simulates human web browsing behavior (instead of using Search Engine APIs). The model autonomously retrieves and synthesizes information by visiting URLs, parsing page content, and following links. Combined with current time and calculator tools, it answers questions requiring real-time information.
```bash
python demo_web_search.py
```
<details>
<summary>Click to view actual execution result</summary>

```text
==================== Starting Web Research Task ====================
Task Goal: How many years has it been since the Computer Science Department was founded next year?
[*] Agent started with model: deepseek-v32

--- Turn 1 ---
[Thinking Process]:
I need to find out when the CS Department of ECNU was founded... Let me get the current date first.
[Tool Call]: get_current_time({})
[Tool Result]: 2025-12-05 12:19:45

--- Turn 2 ---
[Thinking Process]:
It is 2025... First visit ECNU homepage.
[Tool Call]: visit_page({"url": "https://www.ecnu.edu.cn/"})
[Tool Result]: ECNU Homepage... [Department Settings]...

--- Turn 3 ---
[Thinking Process]:
There is a "Department Settings" link. Let's click it.
[Tool Call]: visit_page({"url": "https://www.ecnu.edu.cn/wzcd/xxgk/yxsz.htm"})
[Tool Result]: Department Settings...

--- Turn 4 ---
[Thinking Process]:
I see "School of Computer Science and Technology"... Click it.
[Tool Call]: visit_page({"url": "https://cs.ecnu.edu.cn/"})
[Tool Result]: School of Computer Science and Technology... [History]...

--- Turn 5 ---
[Thinking Process]:
I see a "History" link in the navigation. This likely contains the founding year.
[Tool Call]: visit_page({"url": "https://cs.ecnu.edu.cn/lsyg/list.htm"})
[Tool Result]: History... May 7, 1979, Department of Computer Science established...

--- Turn 6 ---
[Thinking Process]:
Great! The history page shows: "May 7, 1979...".
Now calculate the anniversary for next year (2026). 2026 - 1979 = 47.
[Tool Call]: calculate({"num1": 2026, "num2": 1979, "operator": "-"})
[Tool Result]: 47.0

--- Turn 7 ---
[Thinking Process]:
Okay. Now give the final answer.
[Final Content]:
According to the official history page, the Department was founded on May 7, 1979.
Therefore, next year (2026) will be the 47th anniversary.
```
</details>

## 🧠 Core Principle

This project is implemented based on the [Tool Calling in Thinking Mode](https://api-docs.deepseek.com/zh-cn/guides/thinking_mode) guide from DeepSeek's official documentation.

The core mechanism is: **The model can perform multiple rounds of thinking and tool calling BEFORE outputting the final answer.**

The workflow is as follows:
1.  **Thinking**: The model first outputs a chain of thought (`reasoning_content`), analyzing the problem and deciding if tools are needed.
2.  **Acting**: If needed, the model generates tool call requests (`tool_calls`).
3.  **Execution**: The Agent executes the tools and feeds the results back to the model.
4.  **Re-thinking**: The model receives the tool results and continues its thinking process (the previous `reasoning_content` must be passed back to the API to maintain thought continuity).
5.  **Final Answer**: When the model has sufficient information, it outputs the final answer (`content`).

The `DeepSeekAgent` class in this project fully implements this loop, specifically handling the correct passing of `reasoning_content` and context management.

## 📝 License

MIT License
