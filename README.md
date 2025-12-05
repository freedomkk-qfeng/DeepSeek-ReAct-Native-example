# DeepSeek-ReAct-Native-example

[English Version](README_EN.md)

这是一个展示 **DeepSeek-v3.2** 模型“思考模式”与**工具调用**（Tool Calling）结合能力的 Python 示例项目。

本项目旨在演示基于 DeepSeek-V3.2 这一特性，原生的构建能够进行复杂逻辑推理、多步规划并自主调用工具的 AI Agent 示例。

## ✨ 项目特点

*   **原生 Python 实现**：仅依赖 `openai` SDK 和基础网络库，无复杂的 Agent 框架依赖。
*   **模块化设计**：核心 Agent 逻辑与具体业务场景分离，易于扩展。
*   **双模式支持**：同时支持 DeepSeek 官方 API 和本地部署（vLLM/SGLang）模型。
*   **丰富的示例**：包含数学计算、文字游戏、网页调研等多个场景。

## 📂 目录结构

```text
DeepSeek-ReAct-Native-example/
├── config.py           # 配置文件 (API Key, Base URL, Thinking 参数)
├── deepseek_agent.py   # 核心 Agent 类 (处理思考流、工具调用循环)
├── demo_math.py        # 示例 1: 数学计算器 (展示多步算术推理)
├── demo_adventure.py   # 示例 2: 文字冒险游戏 (展示空间推理与状态记忆)
└── demo_web_search.py  # 示例 3: 网页调研 (展示网页抓取、时间感知与计算能力)
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install openai requests beautifulsoup4
```

### 2. 配置 API

将 `config_example.py` 文件复制为 `config.py`，然后填入你的 API Key：

*   **官方 API**：默认配置，直接填入 `api_key` 即可。
*   **本地部署**：注释掉官方配置，取消本地部署配置的注释，并修改相关配置。

### 3. 运行示例

**示例 1：数学计算器**
模型将逐步分解复杂的四则运算，并调用计算器工具得出结果。
```bash
python demo_math.py
```

**示例 2：文字冒险游戏**
模型将扮演玩家，通过观察（look）、移动（move）、拾取（take）和解锁（unlock）来逃离密室。它会根据游戏反馈绘制地图。
```bash
python demo_adventure.py
```

**示例 3：网页调研 Agent**
模拟人类的网页浏览行为。模型通过访问指定 URL、解析页面内容并提取链接，自主进行信息检索和整合。结合当前时间和计算器工具，回答需要实时信息的问题。
```bash
python demo_web_search.py
```

## 🧠 核心原理

核心机制在于：**模型在输出最终答案之前，可以进行多轮的思考与工具调用。**，详见 DeepSeek 的官方文档 [思考模式下工具调用](https://api-docs.deepseek.com/zh-cn/guides/thinking_mode)

具体流程如下：
1.  **思考 (Thinking)**：模型首先输出一段思维链 (`reasoning_content`)，分析问题并决定是否需要调用工具。
2.  **行动 (Acting)**：如果需要，模型生成工具调用请求 (`tool_calls`)。
3.  **执行 (Execution)**：Agent 执行工具，并将结果反馈给模型。
4.  **再思考 (Re-thinking)**：模型接收工具结果，继续进行下一轮思考（必须将上一轮的 `reasoning_content` 回传给 API 以保持思维连续性）。
5.  **最终回答 (Final Answer)**：当模型认为收集了足够信息后，输出最终答案 (`content`)。

因此我们在这个机制下，agent 的 ReAct 实现可以非常的优雅，不需要额外的结构化处理，reasoning，tools，content 非常天然的通过原生的接口字段来区分。

## 📝 许可证

MIT License
