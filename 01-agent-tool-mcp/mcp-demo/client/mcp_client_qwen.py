import asyncio
import os
# 确保你安装了 openai 库：pip install openai
from openai import OpenAI 
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# --- 配置部分 ---
# 1. 从环境变量读取 Key 和 URL
API_KEY = os.getenv("QWEN_API_KEY")
BASE_URL = os.getenv("QWEN_BASE_URL")

# 2. 检查环境变量是否存在
if not API_KEY or not BASE_URL:
    raise ValueError("❌ 错误：未找到环境变量 QWEN_API_KEY 或 QWEN_BASE_URL，请先在终端 export。")

# 3. 初始化 OpenAI 客户端 (通义千问兼容 OpenAI 格式)
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)

# 4. 指定模型 (通义千问 Max)
MODEL_NAME = "qwen-max" 

async def run():
    # 设置要连接的服务端参数 (这里假设服务端是 weather_server.py)
    server_params = StdioServerParameters(
        command="python", # 或者 "fastmcp", 取决于你怎么启动
        args=["../server/weather_server.py"], # 确保这个文件在同级目录
        env=None
    )

    # 启动 MCP 连接
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 1. 初始化
            await session.initialize()
            
            # 2. 获取工具列表 (看看服务端提供了什么能力)
            tools = await session.list_tools()
            print(f"\n🔌 连接成功！发现工具: {[t.name for t in tools.tools]}")

            # --- 模拟 AI 的思考过程 ---
            user_query = "杭州今天天气怎么样？如果是晴天给我个穿衣建议。"
            print(f"\n👤 用户: {user_query}")
            
            # 3. 这里的逻辑通常需要由 LLM 自动判断调用哪个工具
            # 为了演示简单，我们手动模拟 LLM 决定调用 "get_daily_forecast"
            # 在实际 Agent 中，你会把 tools 的描述发给 Qwen，让 Qwen 返回函数调用指令
            
            print("🤖 Agent (Qwen): 正在思考... (决定调用 get_daily_forecast)")
            
            # 4. 调用 MCP 工具
            #result = await session.call_tool("get_daily_forecast", arguments={"city": "Hangzhou"})
            # 1. 改正参数名为 location
            result = await session.call_tool("get_daily_forecast", arguments={"location": "Hangzhou"})

            # 2. (可选) 加上这行打印，看看工具到底返回了什么
            print(f"\n🔍 工具返回的真实数据: {result.content}\n")
            # 5. 把工具的结果给到 Qwen，让它生成最终回答
            messages = [
                {"role": "system", "content": "你是一个助手，利用提供的工具数据回答问题。"},
                {"role": "user", "content": user_query},
                {"role": "tool", "content": str(result.content), "tool_call_id": "mock_id"} # 模拟上下文
            ]
            
            # 这里我们简单一点，直接把工具结果发给 Qwen 做总结
            final_prompt = f"用户问：{user_query}。\n工具返回的天气数据是：{result.content}。\n请根据数据回答用户。"
            
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": final_prompt}]
            )

            print(f"\n🤖 Agent (Qwen-Max): {response.choices[0].message.content}")

if __name__ == "__main__":
    asyncio.run(run())
