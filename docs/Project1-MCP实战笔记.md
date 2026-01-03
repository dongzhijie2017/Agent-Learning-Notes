> 📖 **文档说明**：本指南涵盖了从环境搭建、代码实现（适配 Qwen-Max）到最终调试通关的全过程，包含详细的避坑指南和扩展学习建议。

---

# 📘 Agent_In_Action 项目一：MCP 工具集成实战指南

**核心目标**：实现一个 AI Agent（客户端），通过 MCP 协议调用本地的自定义工具（服务端），模拟查询天气并在不联网的情况下返回结果。

---

## 1. 环境搭建 (Environment Setup)

### 1.1 创建 Conda 环境

为了避免 Anaconda 服务条款 (ToS) 的报错，推荐使用 `conda-forge` 渠道创建环境。

#### ⚠️ 常见问题：ToS 协议未接受

如果遇到以下错误：

```
CondaToSNonInteractiveError: Terms of Service have not been accepted for the following channels. Please accept or remove them before proceeding:
    - https://repo.anaconda.com/pkgs/main
    - https://repo.anaconda.com/pkgs/r
```

**解决方案：** 先签署协议，再创建环境

```bash
# 签署主仓库协议
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main

# 签署 R 语言仓库协议
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

# 创建名为 agent101 的环境，指定 Python 3.10
conda create -n agent101 python=3.10 -c conda-forge -y

# 激活环境 (每次重新登录服务器都需要执行)
conda activate agent101
```

> 💡 **提示**：更多关于 Conda 渠道的信息，请参考官方文档：
> https://www.anaconda.com/docs/tools/working-with-conda/channels

### 1.2 安装依赖库

我们需要安装 MCP 协议库、OpenAI SDK（用于调用通义千问）以及 Jupyter 支持。

```bash
pip install mcp fastmcp python-dotenv httpx openai jupyter

```

---

## 2. 项目目录结构 (Directory Structure)

为了确保代码能正确找到文件，我们将文件分为 `client`（客户端）和 `server`（服务端）两个文件夹。

请确保你的目录结构如下：

```text
Agent_In_Action/
└── 01-agent-tool-mcp/
    └── mcp-demo/
        ├── server/
        │   └── weather_server.py    # (服务端：提供天气工具)
        └── client/
            └── mcp_client_qwen.py   # (客户端：Qwen AI 助手)

```

---

## 3. 代码实现 (Code Implementation)

### 3.1 服务端：天气工具 (`server/weather_server.py`)

这是一个基于 `FastMCP` 的轻量级服务。为了方便调试和学习，我们**去掉了真实 API 调用**，直接返回模拟数据（Mock），确保逻辑闭环。

> 📝 **注意**：实际项目中，你可以将 `return` 语句替换为真实的天气 API 调用（如 OpenWeatherMap、和风天气等）。

**操作：** 在 `server` 目录下创建/覆盖此文件。

```python
from typing import Union
from mcp.server.fastmcp import FastMCP

# 1. 初始化服务
mcp = FastMCP("weather_server")

# 2. 定义工具：查天气 (Mock 模式)
# ⚠️ 重要：参数名为 location，客户端调用时必须一致
@mcp.tool()
async def get_daily_forecast(location: Union[str, int], days: int = 3) -> str:
    """
    获取指定位置的天气预报
    
    Args:
        location: 城市名称或城市ID（支持字符串或整数）
        days: 预报天数，默认3天
    
    Returns:
        天气预报字符串
    """
    # 打印日志以便观察（会输出到服务端控制台）
    print(f"[服务端] 正在查询 {location} 的天气，预报 {days} 天...") 
    
    # 直接返回"通关"数据（实际项目中应调用真实 API）
    return f"【最终通关】{location} 现在晴空万里，气温 28°C，一切系统运行正常！"

# 3. 定义工具：查预警 (占位符)
@mcp.tool()
async def get_weather_warning(location: str) -> str:
    """
    获取指定位置的天气预警
    
    Args:
        location: 城市名称
    
    Returns:
        天气预警信息
    """
    return f"{location} 当前没有任何天气预警。"

# 4. 启动入口
if __name__ == "__main__":
    # 运行 MCP 服务（通过 stdio 通信）
    mcp.run()
```

> 💡 **提示**：
> - 服务端通过标准输入输出（stdio）与客户端通信
> - 服务端日志会输出到服务端进程的控制台，客户端看不到
> - 如果需要调试，可以单独运行服务端脚本测试

### 3.2 客户端：Qwen AI 助手 (`client/mcp_client_qwen.py`)

这是我们自定义的客户端，使用阿里云 Qwen-Max 模型，通过标准输入输出 (Stdio) 连接服务端。

**操作：** 在 `client` 目录下创建/覆盖此文件。

> 📝 **注意**：以下提供的是**简化版本**，适合快速上手。完整版本（包含错误处理、命令行参数等）请参考项目根目录下的 `mcp_client_qwen.py`。

#### 简化版本（适合学习）

```python
import asyncio
import os
from openai import OpenAI 
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# --- 配置部分 ---
# 从环境变量读取 Key，安全且规范
API_KEY = os.getenv("QWEN_API_KEY")
BASE_URL = os.getenv("QWEN_BASE_URL")

if not API_KEY or not BASE_URL:
    raise ValueError("❌ 错误：未找到环境变量 QWEN_API_KEY 或 QWEN_BASE_URL")

# 初始化 OpenAI 客户端 (适配通义千问)
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
MODEL_NAME = "qwen-max" 

async def run():
    # --- 关键点：指定服务端的正确路径 ---
    # 方法1：使用相对路径（如果客户端在 client/ 目录下运行）
    server_params = StdioServerParameters(
        command="python", 
        args=["../server/weather_server.py"], 
        env=None
    )
    
    # 方法2：使用绝对路径（更可靠，推荐）
    # from pathlib import Path
    # script_path = Path(__file__).parent.parent / "server" / "weather_server.py"
    # server_params = StdioServerParameters(
    #     command="python",
    #     args=[str(script_path)],
    #     env=None
    # )

    # 建立 MCP 连接
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 1. 列出可用工具
            tools = await session.list_tools()
            print(f"\n🔌 连接成功！发现工具: {[t.name for t in tools.tools]}")

            user_query = "杭州今天天气怎么样？"
            print(f"\n👤 用户: {user_query}")
            print("🤖 Agent (Qwen): 正在思考... (决定调用 get_daily_forecast)")
            
            # 2. 调用工具 (关键：参数名必须是 location，与服务端一致)
            result = await session.call_tool("get_daily_forecast", arguments={"location": "Hangzhou"})
            
            # 处理工具返回结果（MCP 返回格式可能是多种类型）
            if hasattr(result, 'content'):
                tool_result = result.content
            elif hasattr(result, 'text'):
                tool_result = result.text
            else:
                tool_result = str(result)
            
            print(f"🔍 [调试] 工具返回结果: {tool_result}")
            
            # 3. 让 LLM 生成最终回复
            final_prompt = f"用户问：{user_query}。\n工具返回的数据是：{tool_result}。\n请根据数据回答用户。"
            
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": final_prompt}]
            )

            print(f"\n🤖 Agent (Qwen-Max): {response.choices[0].message.content}")

if __name__ == "__main__":
    asyncio.run(run())
```

#### 完整版本特性

完整版本（`mcp_client_qwen.py`）包含以下增强功能：

- ✅ **完善的错误处理**：处理连接失败、工具调用失败等异常
- ✅ **智能路径查找**：自动查找服务端脚本，支持相对路径和绝对路径
- ✅ **命令行参数支持**：可通过参数自定义查询、工具和参数
- ✅ **类型提示和文档**：更好的代码可读性和维护性
- ✅ **灵活的工具结果处理**：支持多种 MCP 返回格式

使用完整版本：

```bash
# 使用默认查询
python mcp_client_qwen.py

# 自定义查询
python mcp_client_qwen.py --query "北京明天天气如何？"

# 指定工具和参数
python mcp_client_qwen.py --tool get_daily_forecast --tool-args '{"location": "Shanghai"}'
```

---

## 4. 运行步骤 (Execution)

### 4.1 设置环境变量

在终端中配置阿里云 DashScope 的 API Key。

> ⚠️ **注意**：以下方式为临时设置，关闭终端窗口后需重新设置。如需永久设置，请将命令添加到 `~/.bashrc` 或 `~/.zshrc` 文件中。

```bash
# 设置 API Key（替换为你的真实密钥）
export QWEN_API_KEY="sk-你的真实密钥"

# 设置 API 基础 URL（通义千问兼容 OpenAI 格式）
export QWEN_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"

# 可选：设置模型名称（默认 qwen-max）
export QWEN_MODEL_NAME="qwen-max"
```

**验证环境变量是否设置成功：**

```bash
echo $QWEN_API_KEY
echo $QWEN_BASE_URL
```

### 4.2 启动程序

#### 方式一：使用简化版本（在 client 目录下运行）

```bash
# 进入客户端目录
cd ~/Agent_In_Action/01-agent-tool-mcp/mcp-demo/client

# 运行客户端
python mcp_client_qwen.py
```

#### 方式二：使用完整版本（支持命令行参数）

```bash
# 在项目根目录或任意位置运行
python mcp_client_qwen.py

# 或使用自定义参数
python mcp_client_qwen.py --query "北京明天天气如何？" --tool get_daily_forecast
```

> 💡 **提示**：如果遇到 `ModuleNotFoundError`，请确保已激活 conda 环境：
> ```bash
> conda activate agent101
> ```

### 4.3 预期输出

看到如下内容即代表成功：

```
📡 正在连接 MCP 服务端: /path/to/weather_server.py
✅ MCP 连接初始化成功
🔌 连接成功！发现工具: ['get_daily_forecast', 'get_weather_warning']

👤 用户: 杭州今天天气怎么样？
🤖 Agent (Qwen): 正在思考... (决定调用 get_daily_forecast)
🔧 调用工具: get_daily_forecast，参数: {'location': 'Hangzhou'}
✅ 工具调用成功
📊 工具返回数据: 【最终通关】Hangzhou 现在晴空万里，气温 28°C，一切系统运行正常！

🤖 正在请求 Qwen-Max 生成回答...
🤖 Agent (Qwen-Max): 根据最新数据，杭州现在晴空万里，气温 28°C，一切系统运行正常！
```

### 4.4 常见错误排查

| 错误信息 | 可能原因 | 解决方案 |
|---------|---------|---------|
| `❌ 错误：未找到环境变量` | 环境变量未设置 | 检查 `QWEN_API_KEY` 和 `QWEN_BASE_URL` 是否已设置 |
| `[Errno 2] No such file or directory` | 找不到服务端脚本 | 检查路径是否正确，使用绝对路径更可靠 |
| `ModuleNotFoundError: No module named 'mcp'` | 依赖未安装 | 运行 `pip install mcp fastmcp` |
| `工具调用失败` | 参数名不匹配 | 检查服务端工具定义的参数名，确保客户端调用时一致 |

---

## 5. 💡 避坑指南 (Key Learnings)

在本次实战中，我们解决了初学者最容易遇到的几个问题：

### 5.1 路径地狱 (Path Issues)

**现象：**
```
[Errno 2] No such file or directory: '../server/weather_server.py'
```

**原因：**
- 客户端和服务端在不同目录，相对路径可能失效
- 工作目录（`pwd`）与脚本所在目录不一致

**解决方案：**

1. **使用绝对路径（推荐）**
   ```python
   from pathlib import Path
   script_path = Path(__file__).parent.parent / "server" / "weather_server.py"
   server_params = StdioServerParameters(
       command="python",
       args=[str(script_path)],
       env=None
   )
   ```

2. **使用相对路径（需确保工作目录正确）**
   ```python
   # 在 client/ 目录下运行时使用
   args=["../server/weather_server.py"]
   ```

3. **验证路径**
   ```python
   import os
   print(f"当前工作目录: {os.getcwd()}")
   print(f"脚本所在目录: {Path(__file__).parent}")
   ```

### 5.2 参数不对齐 (Parameter Mismatch)

**现象：**
- Agent 返回"遇到技术问题"或"工具调用失败"
- 控制台没有明显错误，但工具返回空结果

**原因：**
- 服务端定义参数名为 `location`，客户端却传了 `city`
- 参数类型不匹配（如传了字符串，但期望整数）

**解决方案：**

1. **检查工具定义**
   ```python
   tools = await session.list_tools()
   for tool in tools.tools:
       print(f"工具名: {tool.name}")
       print(f"参数: {tool.inputSchema}")
   ```

2. **严格对应参数名**
   ```python
   # ✅ 正确：参数名与服务端一致
   result = await session.call_tool("get_daily_forecast", 
                                     arguments={"location": "Hangzhou"})
   
   # ❌ 错误：参数名不匹配
   result = await session.call_tool("get_daily_forecast", 
                                     arguments={"city": "Hangzhou"})
   ```

### 5.3 环境变量未设置

**现象：**
```
ValueError: ❌ 错误：未找到环境变量 QWEN_API_KEY 或 QWEN_BASE_URL
```

**解决方案：**

1. **临时设置（当前终端会话）**
   ```bash
   export QWEN_API_KEY="sk-your-key"
   export QWEN_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
   ```

2. **永久设置（推荐）**
   ```bash
   # 添加到 ~/.bashrc 或 ~/.zshrc
   echo 'export QWEN_API_KEY="sk-your-key"' >> ~/.bashrc
   echo 'export QWEN_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **使用 .env 文件（开发环境）**
   ```bash
   # 安装 python-dotenv
   pip install python-dotenv
   
   # 创建 .env 文件
   echo "QWEN_API_KEY=sk-your-key" > .env
   echo "QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1" >> .env
   
   # 在代码中加载
   from dotenv import load_dotenv
   load_dotenv()
   ```

### 5.4 MCP 连接失败

**现象：**
```
❌ MCP 连接失败: ...
```

**可能原因和解决方案：**

1. **服务端脚本路径错误**
   - 检查路径是否正确
   - 使用绝对路径

2. **Python 解释器路径问题**
   ```python
   # 使用完整路径
   server_params = StdioServerParameters(
       command="/usr/bin/python3",  # 或使用 which python3 查找
       args=[str(script_path)],
       env=None
   )
   ```

3. **服务端脚本有语法错误**
   - 先单独运行服务端脚本测试
   ```bash
   python server/weather_server.py
   ```

4. **依赖未安装**
   ```bash
   pip install mcp fastmcp
   ```

### 5.5 工具返回结果处理

**现象：**
```
AttributeError: '...' object has no attribute 'content'
```

**原因：**
MCP 返回结果格式可能不同，直接访问 `result.content` 可能失败。

**解决方案：**
```python
# 兼容多种返回格式
if hasattr(result, 'content'):
    tool_result = result.content
elif hasattr(result, 'text'):
    tool_result = result.text
elif isinstance(result, (list, dict)):
    tool_result = result
else:
    tool_result = str(result)
```

---

## 6. 📚 扩展学习

### 6.1 下一步可以做什么？

- ✅ 添加更多工具（如查询股票、翻译等）
- ✅ 实现 LLM 自动选择工具（而非手动指定）
- ✅ 添加工具调用链（一个工具的结果作为另一个工具的输入）
- ✅ 集成到 Web 应用或聊天机器人

### 6.2 相关资源

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [FastMCP 文档](https://github.com/jlowin/fastmcp)
- [通义千问 API 文档](https://help.aliyun.com/zh/dashscope/)

---

## 7. 📝 总结

### 7.1 核心要点回顾

通过本项目的学习，你应该掌握：

1. ✅ **MCP 协议基础**：理解客户端-服务端架构，通过 stdio 通信
2. ✅ **工具定义与调用**：如何在服务端定义工具，如何在客户端调用
3. ✅ **LLM 集成**：如何将工具返回结果传递给 LLM 生成自然语言回答
4. ✅ **错误处理**：路径问题、参数对齐、环境变量等常见问题的解决方案

### 7.2 项目结构总结

```
Agent_In_Action/
└── 01-agent-tool-mcp/
    └── mcp-demo/
        ├── server/
        │   └── weather_server.py    # MCP 服务端：提供工具
        └── client/
            └── mcp_client_qwen.py   # MCP 客户端：调用工具 + LLM
```

### 7.3 关键代码流程

```
1. 客户端启动 → 连接服务端（通过 stdio）
2. 客户端列出可用工具 → 服务端返回工具列表
3. 客户端调用工具 → 服务端执行并返回结果
4. 客户端将结果传给 LLM → LLM 生成自然语言回答
5. 客户端输出最终答案
```

### 7.4 常见问题速查

| 问题 | 检查项 |
|-----|--------|
| 连接失败 | 路径是否正确、服务端脚本是否有语法错误 |
| 工具调用失败 | 参数名是否匹配、参数类型是否正确 |
| 环境变量错误 | 是否已设置、是否在正确的终端会话中 |
| 导入错误 | 是否已安装依赖、是否激活了 conda 环境 |

---

**🎉 恭喜！** 你已经完成了 MCP 工具集成的实战项目。接下来可以尝试添加更多工具，或实现更复杂的 Agent 逻辑。

---