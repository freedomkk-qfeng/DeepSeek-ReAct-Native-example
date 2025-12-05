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

**Demo 2: Text Adventure Game**
The model plays a game, using tools to look, move, take items, and unlock doors to escape a room. It draws a map based on game feedback.
```bash
python demo_adventure.py
```

**Demo 3: Web Research Agent**
Simulates human web browsing behavior (instead of using Search Engine APIs). The model autonomously retrieves and synthesizes information by visiting URLs, parsing page content, and following links. Combined with current time and calculator tools, it answers questions requiring real-time information.
```bash
python demo_web_search.py
```

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
