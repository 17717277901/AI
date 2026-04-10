# WorkAI Agent

Python 实现的 Agent 项目，具备 LLM + Tools + Memory + Planning 能力。

## 功能特性

- **LLM**: 基于 Anthropic Claude API 的语言模型
- **Tools**: 实时工具集成（天气、计算器）
- **Memory**: 对话历史管理，支持上下文窗口
- **Planning**: 任务分解与规划

## 项目结构

```
workAI/
├── agent/           # Agent 核心模块
│   ├── agent.py     # 主 Agent 类
│   └── llm.py       # LLM 客户端
├── tools/           # 工具模块
│   ├── base.py      # 工具基类
│   ├── weather.py   # 天气工具
│   └── calculator.py# 计算器工具
├── memory/          # 记忆模块
│   ├── conversation.py  # 对话记忆
│   └── summary.py   # 摘要记忆
├── planning/        # 规划模块
│   └── planner.py   # 任务规划器
├── utils/           # 工具函数
│   └── logger.py    # 日志
├── config.py        # 配置
├── main.py          # 入口
└── requirements.txt # 依赖
```

## 安装

```bash
pip install -r requirements.txt
```

## 配置

1. 复制 `.env.example` 为 `.env`
2. 填入 `ANTHROPIC_API_KEY`

```bash
cp .env.example .env
```

## 运行

```bash
python main.py
```

## 内置工具

| 工具 | 功能 | 示例 |
|------|------|------|
| `get_weather` | 获取城市天气 | "北京天气怎么样？" |
| `calculate` | 数学计算 | "计算 sqrt(16)乘以2" |

## 命令

- `reset` - 清空对话记忆
- `exit/quit` - 退出程序
