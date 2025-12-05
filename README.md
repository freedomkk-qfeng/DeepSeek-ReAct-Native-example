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
<details>
<summary>点击查看实际运行结果</summary>

```text
==================== Testing Expression: (32 + 54) * 12 - 15 / 3 ====================
[*] Agent started with model: deepseek-v32

--- Turn 1 ---
[Thinking Process]:
我需要计算表达式 (32 + 54) * 12 - 15 / 3。我应该按运算顺序进行：先计算括号内的加法，然后乘法和除法，最后减法。我 
会在每一步都使用计算工具。                                                                                       
首先，计算括号内的加法：32 + 54。
[Tool Call]: calculate({"num1": 32, "num2": 54, "operator": "+"})
[Tool Result]:
86.0

--- Turn 2 ---
[Thinking Process]:
所以 (32 + 54) = 86。接下来，计算乘法：86 * 12。
[Tool Call]: calculate({"num1": 86, "num2": 12, "operator": "*"})
[Tool Result]:
1032.0

--- Turn 3 ---
[Thinking Process]:
所以 86 * 12 = 1032。接下来，计算除法：15 / 3。
[Tool Call]: calculate({"num1": 15, "num2": 3, "operator": "/"})
[Tool Result]:
5.0

--- Turn 4 ---
[Thinking Process]:
所以 15 / 3 = 5。最后，计算减法：1032 - 5。
[Tool Call]: calculate({"num1": 1032, "num2": 5, "operator": "-"})
[Tool Result]:
1027.0

--- Turn 5 ---
[Thinking Process]:
因此，最终结果是 1027。
现在用中文总结一下。
[Final Content]:
根据运算顺序，逐步计算表达式 **(32 + 54) × 12 - 15 ÷ 3** 的结果如下：
1. **计算括号内的加法**：
   \(32 + 54 = 86\)
2. **计算乘法**：
   \(86 \times 12 = 1032\)
3. **计算除法**：
   \(15 \div 3 = 5\)
4. **最后计算减法**：
   \(1032 - 5 = 1027\)
**最终结果**：**1027**
```
</details>

**示例 2：文字冒险游戏**
模型将扮演玩家，通过观察（look）、移动（move）、拾取（take）和解锁（unlock）来逃离密室。它会根据游戏反馈绘制地图。
```bash
python demo_adventure.py
```
<details>
<summary>点击查看实际运行结果</summary>

```text
==================== Starting Text Adventure Game ====================
Goal: Escape from this place!
[*] Agent started with model: deepseek-v32

--- Turn 1 ---
[Thinking Process]:
我首先需要观察当前环境，使用look工具。
[Tool Call]: look({})
[Tool Result]:
你在一间昏暗的石室里。空气中弥漫着灰尘的味道。 出口有: north. (当前持有物品: 无)
Map:
      [Exit] -X- [Hallway] --- [Storage]
                     |
                 [Start]*

--- Turn 2 ---
[Thinking Process]:
我看到一个地图：当前位置是[Start]，北边是[Exit]，但中间有一个锁着的门（-X-）。走廊连接着[Storage]。我需要先探索周
围，看看有没有钥匙。目前房间里没有物品，只有北边的出口。我先向北走试试看？但地图显示北边有一个锁着的门，可能需要 钥匙。我先尝试向北移动，看看会发生什么。
[Tool Call]: move({"direction": "north"})
[Tool Result]:
你向 north 移动。
你站在一条长长的走廊上。西边有一扇巨大的铁门，看起来锁得很紧。 出口有: south, east, west. (当前持有物品: 无)
Map:
      [Exit] -X- [Hallway]* --- [Storage]
                      |
                   [Start]

--- Turn 3 ---
[Thinking Process]:
我现在在走廊[Hallway]。出口有南边（返回Start）、东边和西边。西边有一扇巨大的铁门，看起来锁得很紧。东边呢？地图显 
示走廊连接着[Storage]，那应该是东边吧？地图上显示[Hallway] --- [Storage]，所以东边应该是Storage。西边是锁着的铁门，可能就是通向[Exit]的门？但地图显示[Exit] -X- [Hallway]，所以锁着的门在北边？等等，地图上[Exit]在[Hallway]的北边，并且有一个-X-表示锁着的门。但我刚才从Start向北移动，到达了Hallway。那么北边的锁门应该在Hallway和Exit之间。但我 现在在Hallway，描述说西边有一扇巨大的铁门锁着，这可能是另一个锁着的门？也许地图简化了，实际方向可能有偏差。我先看看东边是什么。
[Tool Call]: move({"direction": "east"})
[Tool Result]:
你向 east 移动。
这是一个杂乱的储藏室，堆满了旧箱子。 这里有: key. 出口有: west. (当前持有物品: 无)
Map:
      [Exit] -X- [Hallway] --- [Storage]*
                     |
                  [Start]

--- Turn 4 ---
[Thinking Process]:
太好了！储藏室里有一把钥匙。我捡起钥匙。
[Tool Call]: take({"item": "key"})
[Tool Result]: 你捡起了 key。

--- Turn 5 ---
[Thinking Process]:
现在我有了钥匙。我需要解锁那扇锁着的门。地图显示锁着的门在Hallway和Exit之间，方向是北边。但我之前在Hallway看到西 
边也有一扇锁着的铁门。可能有两个锁着的门？我需要回到Hallway。向西走回到Hallway。
[Tool Call]: move({"direction": "west"})
[Tool Result]:
你向 west 移动。
你站在一条长长的走廊上。西边有一扇巨大的铁门，看起来锁得很紧。 出口有: south, east, west. (当前持有物品: key)
Map:
      [Exit] -X- [Hallway]* --- [Storage]
                      |
                   [Start]

--- Turn 6 ---
[Thinking Process]:
现在我回到了Hallway。我需要解锁哪个门？地图显示锁着的门在Hallway和Exit之间，方向是北边。但描述说西边有一扇巨大的 
铁门锁着。这可能是因为地图方向是简化的，实际上北边的门就是西边的门？让我试试解锁西边的门。使用unlock工具，方向west。
[Tool Call]: unlock({"direction": "west"})
[Tool Result]: 你用钥匙打开了 west 边的门！

--- Turn 7 ---
[Thinking Process]:
门打开了！现在我可以向西移动了。让我向西走。
[Tool Call]: move({"direction": "west"})
[Tool Result]: 你成功逃出来了！阳光洒在你的脸上。恭喜通关！
Map:
      [Exit]* --- [Hallway] --- [Storage]
                      |
                   [Start]
```
</details>

**示例 3：网页调研 Agent**
模拟人类的网页浏览行为。模型通过访问指定 URL、解析页面内容并提取链接，自主进行信息检索和整合。结合当前时间和计算器工具，回答需要实时信息的问题。
```bash
python demo_web_search.py
```
<details>
<summary>点击查看实际运行结果</summary>

```text
==================== Starting Web Research Task ====================
Task Goal: 明年是计算机系成立多少周年？
[*] Agent started with model: deepseek-v32

--- Turn 1 ---
[Thinking Process]:
我需要找出华东师范大学计算机系成立于哪一年，然后计算明年（2025年）是它成立的多少周年。首先，我得获取当前年份，然 
后寻找计算机系的成立年份。                                                                                       
让我先获取当前日期。
[Tool Call]: get_current_time({})
[Tool Result]:
2025-12-05 12:19:45

--- Turn 2 ---
[Thinking Process]:
现在是2025年12月5日。明年是2026年。所以我需要计算计算机系到2026年成立多少周年。这需要找到成立年份。
首先访问华东师范大学主页寻找相关信息。
[Tool Call]: visit_page({"url": "https://www.ecnu.edu.cn/"})
[Tool Result]: 华东师范大学 language [English](http://english.ecnu.edu.cn/) [Français](http://french.ecnu.edu.cn/
) [Русский](https://russian.ecnu.edu.cn) 网站菜单 [学校概况](https://www.ecnu.edu.cn/wzcd/xxgk.htm) [学校章程](https://w...
...(content truncated)...

--- Turn 3 ---
[Thinking Process]:
主页上有很多信息，但我需要找到计算机系。可能“计算机系”指的是“计算机科学与技术学院”或“软件工程学院”。华东师大可能 
有一个“计算机科学与技术学院”或者“信息学部”。让我看看“院系设置”的链接。主页上有一个“院系设置”的链接。点进去看看。 
[Tool Call]: visit_page({"url": "https://www.ecnu.edu.cn/wzcd/xxgk/yxsz.htm"})
[Tool Result]: 院系设置-华东师范大学 中文 [English](https://english.ecnu.edu.cn/) [Français](https://french.ecnu.
edu.cn/) [Русский](https://russian.ecnu.edu.cn/) [首页](https://www.ecnu.edu.cn/index.htm) [学校概况](https://www.ecnu.e...
...(content truncated)...

--- Turn 4 ---
[Thinking Process]:
我看到有“计算机科学与技术学院”和“软件工程学院”。问题中提到“计算机系”，这可能指的是“计算机科学与技术学院”。我需要 
找到该学院的成立年份。最好访问计算机科学与技术学院的网站，那里可能会有“学院简介”或“历史沿革”页面。点进去看看。   
[Tool Call]: visit_page({"url": "https://cs.ecnu.edu.cn/"})
[Tool Result]: 华东师范大学计算机科学与技术学院 [EN](https://cs.ecnu.edu.cn/) [首页](http://cs.ecnu.edu.cn/main.h
tm) [学院概况](https://cs.ecnu.edu.cn/xygk/list.htm) [学院简介](https://cs.ecnu.edu.cn/xyjj/list.htm) [历史沿革](https://cs.ecnu.edu...
...(content truncated)...

--- Turn 5 ---
[Thinking Process]:
在导航栏中，我看到了“历史沿革”的链接。这很可能包含成立年份。点开看看。
[Tool Call]: visit_page({"url": "https://cs.ecnu.edu.cn/lsyg/list.htm"})
[Tool Result]: 历史沿革 [EN](https://cs.ecnu.edu.cn/lsyg/list.htm) [首页](http://cs.ecnu.edu.cn/main.htm) [学院概
况](https://cs.ecnu.edu.cn/xygk/list.htm) [学院简介](https://cs.ecnu.edu.cn/xyjj/list.htm) [历史沿革](https://cs.ecnu.ed...
...(content truncated)...

--- Turn 6 ---
[Thinking Process]:
太好了！历史沿革页面显示：“1979年5月7日，建立华东师范大学计算机科学系”。所以计算机系成立于1979年。
现在我们需要计算明年（2026年）是成立多少周年。2026年减去1979年等于47年。不过我们需要确认，周年纪念日是否按年份差 
计算，还是需要具体到日期？题目是“明年是计算机系成立多少周年？”。由于明年是2026年，而成立年份是1979年，那么2026 - 1979 = 47。但我们需要考虑，如果明年（2026年）的周年纪念日是在5月7日之后，那么就是47周年。然而，题目可能只要求给出年份差。通常来说，“多少周年”指的是从成立起到明年所经过的整年数。既然明年是2026年，那么就是47周年。               
但为了更精确，我们最好确认一下当前日期。今天是2025年12月5日。明年是2026年。到2026年5月7日，计算机系将成立47周年。
因为从1979年5月7日到2026年5月7日是47年。                                                                         
所以答案是：明年（2026年）是计算机系成立47周年。
不过，我们也可以引用历史沿革页面中的描述。我会据此给出答案。
让我们再检查一下页面，看看是否有其他相关信息。也许有关于“计算机建系40周年特辑”的链接，这暗示着40周年纪念。但既然 
页面提到了“计算机建系40周年特辑”，那可能指的是2019年（1979年+40年=2019年）。这表明2019年是40周年纪念。那么到2026 年就是47周年。这没问题。                                                                                         
因此，答案是：明年（2026年）是计算机系成立47周年。
现在，我需要用中文给出答案。提供解释和引用来源。
接下来，我将使用计算工具来确认一下计算。
[Tool Call]: calculate({"num1": 2026, "num2": 1979, "operator": "-"})
[Tool Result]: 47.0

--- Turn 7 ---
[Thinking Process]:
好的。
现在给出最终答案。
[Final Content]:
根据华东师范大学计算机科学与技术学院官网的“历史沿革”页面记载，**华东师范大学计算机科学系成立于1979年5月7日**。   
- 成立年份：1979年
- 明年年份：2026年（当前为2025年12月）
- 周年计算：2026年 - 1979年 = 47周年
因此，**明年（2026年）将是计算机系成立47周年**。
> 参考资料：华东师范大学计算机科学与技术学院《历史沿革》页面（https://cs.ecnu.edu.cn/lsyg/list.htm）中明确写道：“
1979年5月7日，建立华东师范大学计算机科学系”。
```
</details>

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
