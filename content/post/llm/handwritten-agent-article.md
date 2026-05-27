---
title: "手写一个 AI Agent：从零理解它的原理和本质"
description: "用 300 行 Python 代码手写一个 ReAct Agent，带你从零理解 AI Agent 的核心原理——LLM + 工具 + 循环。"
date: 2026-05-24T17:00:00+08:00
lastmod: 2026-05-24T17:00:00+08:00
draft: false
tags:
  - AI
  - Agent
  - Python
  - 深度学习
  - 实战
categories:
  - 技术文章
keywords:
  - AI Agent
  - ReAct
  - 手写Agent
  - LLM
  - DeepSeek
  - Python
featured: false
weight: 10
---

# 手写一个 AI Agent：从零理解它的原理和本质

> 用 300 行代码，让你看穿所有 Agent 框架的底牌

## 一、Agent 到底是什么？

这两年 AI 圈最火的概念之一就是 **Agent**。LangChain、LangGraph、AutoGen、CrewAI……框架层出不穷，但如果你扒开这些框架的外衣，会发现最核心的东西只有一句话：

> Agent = LLM + 工具 + 循环

把这句话拆开：
- **LLM**：大脑，负责推理和决策
- **工具**：手脚，让 LLM 能影响外部世界（执行命令、查数据库、发请求）
- **循环**：把上面两个串起来：思考 → 行动 → 观察结果 → 继续思考

这就是 **ReAct (Reasoning + Acting)** 模式，所有 Agent 框架的最底层原语。

本文不教你用框架，而是带你从零手写一个 Agent，让你**亲眼看到**每一轮对话里 LLM 是怎么思考的、Agent 是怎么解析的、工具是怎么被调用的。

## 二、核心流程：ReAct 循环

我们先不看代码，先理解这个循环长什么样。

```
你: "我的机器有几个 CPU 核心？"
                  │
                  ▼
LLM（收到问题，开始推理）:
  "用户想知道 CPU 核心数 -> 用 nproc 命令"
                  │
                  ▼
Agent（解析 LLM 输出 → 发现 Action）:
  执行: nproc
                  │
                  ▼
命令行返回: "8"
                  │
                  ▼
LLM（看到结果，继续推理）:
  "8 个核心 -> 可以回答了"
                  │
                  ▼
你收到: "你的机器有 8 个 CPU 核心 ✅"
```

关键是：**LLM 不是一次输出就完事**，它在"思考→行动→观察→再思考"这个圈里转，直到它能给出最终答案。

这个圈，就是 Agent 的全部秘密。

## 三、动手写一个：逐行解析

我们的实现分四个模块：

### 3.1 LLM 客户端

最外层是调用大模型的接口。DeepSeek 兼容 OpenAI 协议，所以我们直接用 `openai` SDK：

```python
class LLMClient:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL"),
        )

    def chat(self, messages) -> str:
        response = self.client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=messages,
            temperature=0.0,
        )
        return response.choices[0].message.content or ""
```

这段代码没什么神秘的——就是一个 API 封装。关键在后面。

### 3.2 CLI 执行器

Agent 需要"手脚"来做事。我们给它一个能安全执行 CLI 命令的工具：

```python
class CLIExecutor:
    DANGEROUS_PATTERNS = [
        r"\bsudo\b", r"\bmkfs\b", r"\brm\s+-rf\s+/$", ...
    ]

    def run(self, command: str) -> str:
        # 1. 安全检查：拒绝危险命令
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return f"[Safety Error] 危险命令被拦截"

        # 2. 执行命令（带超时）
        result = subprocess.run(
            command, shell=True,
            capture_output=True, text=True,
            timeout=30,
        )

        # 3. 处理输出（截断、报错）
        output = result.stdout + result.stderr
        if result.returncode != 0:
            output = f"[Exit code: {result.returncode}]\n{output}"
        return output[:3000]
```

这里有个要点：**工具返回的结果会被送回给 LLM**，让它"看到"自己行动的结果。

### 3.3 协议：LLM 怎么告诉 Agent 要干什么？

这是最精妙的部分。LLM 是一个文本输入/文本输出的模型，Agent 要让它"执行命令"，需要一个**约定的格式**。

我们在 System Prompt 里告诉 LLM：

```
可用工具:
- run_command: 执行 shell 命令

输出格式（二选一）:

=== 要执行命令 ===
Thought: <你的推理>
Action: run_command
Action Input: <命令>

=== 要给出答案 ===
Final Answer: <你的回答>
```

Agent 收到 LLM 的输出后，用正则表达式解析：

```python
def parse_response(response: str) -> dict:
    # 是 Final Answer 吗？
    if re.search(r"Final Answer:\s*(.*)", response, re.DOTALL):
        return {"type": "final", "content": "..."}

    # 是 Action 吗？
    if re.search(r"Action:\s*run_command\s*Action Input:\s*(.*)", response):
        return {"type": "action", "command": "..."}

    # 都不是 → 还在思考
    return {"type": "thought", "content": "..."}
```

**这就是 Agent 的核心协议**——双方约定好一套文本格式，LLM 输出 Action，Agent 解析后执行，然后把结果喂回去。

> 所有 Agent 框架（LangChain、AutoGen、OpenAI Function Calling）都是在给这套"文本协议"加语法糖。

### 3.4 ReAct 循环（核心中的核心）

把上面三块串起来：

```python
def run_agent(user_input: str):
    llm = LLMClient()
    executor = CLIExecutor()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]

    for turn in range(1, 11):  # 最多 10 轮
        # 1. 调 LLM
        response = llm.chat(messages)
        parsed = parse_response(response)

        # 2. 根据解析结果做不同的事
        if parsed["type"] == "final":
            print(parsed["content"])
            return

        if parsed["type"] == "action":
            observation = executor.run(parsed["command"])
            # 把"思考"和"观察结果"都追加到消息历史
            messages.append({"role": "assistant", "content": response})
            messages.append({"role": "user", "content": observation})
            # 继续下一轮循环

        if parsed["type"] == "thought":
            # 还没给出明确指令，推它一把
            messages.append({"role": "user", "content": "请给出 Action 或 Final Answer。"})
```

这个循环就是 Agent 的全部。用流程图看更清楚：

```
用户输入
    │
    ▼
┌─────────────────────────────┐
│  给 LLM 发送消息历史          │
│  (system + 之前的对话)        │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  LLM 返回文本                 │
│  "Thought... Action: xxx"    │
└──────────┬──────────────────┘
           │
    ┌──────┴──────┐
    ▼              ▼
 Final?         Action?
    │              │
    ▼              ▼
 输出答案     执行命令 → 拿到结果
                             │
                  ┌──────────┘
                  ▼
            追加到消息历史
                  │
                  ▼
            回到 LLM（继续循环）
```

## 四、Skill 系统：让 Agent 拥有"专业技能"

基础的 ReAct 循环有了，但 LLM 只知道"执行 CLI 命令"这一种能力。如果想让 Agent 能做更专业的事（比如代码审查、技术写作、调试），怎么办？

答案是 **Skill（技能）系统**。

思路很简单：每个 Skill 是一段 **prompt 模板**，描述了特定的专业能力。Agent 启动时把所有 skill 的名称和描述列在 system prompt 里，LLM 在推理过程中如果发现需要某个技能，就通过 `load_skill` action 加载它。

### Skill 文件

```markdown
---
name: code-review
description: 审查代码质量，检查 bug、安全漏洞和代码风格
---

你是一个资深代码审查专家。请从以下维度审查用户提供的代码：
1. 逻辑正确性
2. 安全漏洞
3. 代码风格
4. 性能问题
```

### 加载流程

```
User: "帮我审查这段代码"
                      │
                      ▼
LLM（看到 system prompt 里的 skill 列表）:
  "这需要 code-review skill"
  Action: load_skill
  Action Input: code-review
                      │
                      ▼
Agent（加载 skill.md 文件）:
  把 skill 的 prompt 追加为 system message
                      │
                      ▼
LLM（现在拥有了审查专家的指令）:
  开始按 skill 要求工作
  Action: run_command
  Action Input: cat file.py
  ...
```

关键要点：
- **只把 skill 的"名称+描述"放进 system prompt**（节省 token）
- **完整 prompt 只在被调用时才加载**
- **不额外调用 LLM**（匹配发生在 LLM 的正常推理过程中）

这和 MCP（Model Context Protocol）的设计哲学相似：工具/技能的描述轻量挂载，按需加载。

## 五、Agent 的"协议"本质

回看整个过程，你会发现一个规律：

> 所谓的 Agent，本质上是把 LLM 的"对话接口"扩展成了"指令接口"

- 普通对话：用户问 → LLM 答
- Agent：用户问 → LLM 思考 → LLM 发出指令 → Agent 执行指令 → 结果喂回 → LLM 继续

这套"指令协议"是手工约定的（正则解析），到了 OpenAI Function Calling 和 Anthropic Tool Use 层面，它被标准化了——但本质没变。

你完全可以自己定义协议：

```
// 不用 Action/Final Answer，用 XML
<tool_call>
  <name>search_web</name>
  <args>{"q": "weather in Beijing"}</args>
</tool_call>

// 或者用 JSON
{"tool": "search_web", "params": {"q": "weather"}}

// 或者用任意你喜欢的格式
→ SEARCH: weather in Beijing ←
```

**协议只是形式，循环才是灵魂。**

## 六、从手写到框架

理解了这 300 行代码的顺序，你就理解了所有 Agent 框架：

| 框架 | 等价于我们做的 |
|------|------------|
| LangChain | AgentExecutor + Tool abstractions |
| LangGraph | State machine 化的 ReAct 循环 |
| OpenAI Assistants | 托管版的 ReAct + 工具管理 |
| AutoGen / CrewAI | 多 Agent + 消息路由 |
| MCP | 标准化工具发现和调用协议 |

框架解决的是工程问题（并发、持久化、多 Agent 编排、错误恢复），但核心逻辑和我们这 300 行代码一模一样。

## 七、试试看

你可以在这个仓库里看到完整代码，跟着步骤运行：

```bash
# 1. 配置 API Key
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY

# 2. 安装依赖
uv sync

# 3. 运行
uv run python agent.py
```

然后试试这些话：

- `whoami` — 最简单的 ReAct 测试
- `我有哪些 Python 文件？` — LLM 会调用 `find` 或 `ls`
- `帮我审查一下 agent.py 的代码质量` — 加载 code-review skill 再审查
- `看下系统有多少内存` — 会用 `free` 或 `cat /proc/meminfo`

每一轮对话你都会看到：
1. Agent 发送给 LLM 的**完整消息列表**（上下文怎么积累的）
2. LLM 的**原始输出**（它怎么思考的）
3. **解析结果**（Agent 从文本中提取了什么）
4. **命令执行输出**（工具调用的结果）

看完这些日志，你对 Agent 就再也不会有"魔法感"了。

## 八、写在最后

AI Agent 不是一个产品，而是一种**计算模式**。

把 LLM 从"对话机器人"变成"自主执行者"，只需要一个循环 + 一个协议。框架会帮你管理复杂度，但不要被框架迷惑——回到原点，它就是一个 `while` 循环加几个 `if` 判断。

如果你看懂了这里的 300 行代码，下次再听到"Agent"这个词，你脑海里浮现的不再是某个框架的黑盒，而是一个清晰的循环：

> LLM 说：我要做 X
> Agent 做 X
> LLM 看到结果，说：那我该做 Y 了

就这么简单。
