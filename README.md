# Agentic AI 学习实战笔记 🤖

> 本项目基于 [FlyAIBox/Agent_In_Action](https://github.com/FlyAIBox/Agent_In_Action) 课程，记录了我的实战过程与代码改进。
> **当前状态**：Project 1 (MCP 工具集成) 已通关 ✅

---

## 🌟 核心成果：Project 1 - MCP 工具集成 (Mock版)

我重构了 Project 1 的 MCP 工具集成部分，使其适配 **Qwen-Max** 模型并支持 **本地 Mock 调试**，解决了原课程依赖真实 API Key 导致调试困难的问题。

### 🔧 我的改进点
1.  **Mock 服务端 (`weather_server.py`)**：
    * 移除真实 API 依赖，实现了模拟数据返回。
    * 支持无网环境调试 MCP 协议逻辑。
2.  **Qwen 客户端 (`mcp_client_qwen.py`)**：
    * 重写客户端代码，完美适配阿里云 **Qwen-Max** 模型。
    * 增加了更清晰的控制台日志输出。
3.  **📚 实战笔记**：
    * [👉 点击查看 Project 1 完整实战与避坑指南](docs/Project1-MCP实战笔记.md)

---

## 🚀 快速开始 (Quick Start)

如果你想运行我修改后的 Mock 天气助手：

### 1. 克隆仓库
```bash
git clone [https://github.com/dongzhijie2017/Agent-Learning-Notes.git](https://github.com/dongzhijie2017/Agent-Learning-Notes.git)
cd Agent-Learning-Notes
```
### 2. 环境准备
# 建议使用 conda
```bash
conda create -n agent101 python=3.10 -c conda-forge -y
conda activate agent101
```
# 安装依赖
```bash
pip install mcp fastmcp openai python-dotenv
```
### 3. 配置密钥 (Linux/Mac)
```bash
export QWEN_API_KEY="sk-你的阿里云密钥"
export QWEN_BASE_URL="[https://dashscope.aliyuncs.com/compatible-mode/v1](https://dashscope.aliyuncs.com/compatible-mode/v1)"
```
### 4. 运行代码
```bash
cd 01-agent-tool-mcp/mcp-demo/client
python mcp_client_qwen.py
```
## 📂 仓库结构说明
Agent-Learning-Notes/
├── docs/                     # 📝 核心：我的学习笔记和复盘文档
├── 01-agent-tool-mcp/        # 🛠️ Project 1：MCP 协议实战
│   └── mcp-demo/
│       ├── client/           # 客户端代码 (含 mcp_client_qwen.py)
│       └── server/           # 服务端代码 (含 weather_server.py)
└── ...                       # 其他原课程文件 (待探索)

🙏 致谢
本项目代码及灵感来源于 FlyAIBox/Agent_In_Action。
