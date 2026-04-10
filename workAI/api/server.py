"""
FastAPI WebSocket Server for WorkAI Agent
"""
import asyncio
import json
from typing import Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import Agent, LLMClient
from memory import ConversationMemory
from planning import Planner
from tools import WeatherTool, CalculatorTool, TimeTool, DateTool
from utils import setup_logger

logger = setup_logger("WorkAI-Server")


class ConnectionManager:
    """Manages WebSocket connections"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")

    async def send_json(self, message: dict, client_id: str = None):
        """Send JSON message to client(s)"""
        if client_id:
            websocket = self.active_connections.get(client_id)
            if websocket:
                await websocket.send_json(message)
        else:
            for websocket in self.active_connections.values():
                await websocket.send_json(message)


manager = ConnectionManager()


def create_agent() -> Agent:
    """Create and configure the agent"""
    llm_client = LLMClient()
    tools = [WeatherTool(), CalculatorTool(), TimeTool(), DateTool()]
    memory = ConversationMemory(max_length=100)
    planner = Planner(llm_client)

    return Agent(
        llm_client=llm_client,
        tools=tools,
        memory=memory,
        planner=planner,
        system_prompt="""You are WorkAI, an advanced AI assistant with real-time tool access.

Available Tools (you MUST use these tools when needed):
1. get_weather - 获取城市天气信息 (输入: city 城市名)
2. get_date - 获取今日日期信息 (输入: 无)
3. get_time - 获取时间信息 (输入: location 城市名/时区)
4. calculate - 数学计算 (输入: operation, a, b)

IMPORTANT: When user asks about weather, time, date, or math, you MUST call the appropriate tool FIRST, then respond with the tool results.

Always respond in Chinese (中文). Use the tools to get real-time data."""
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("WorkAI Server starting up...")
    yield
    logger.info("WorkAI Server shutting down...")


app = FastAPI(
    title="WorkAI Agent",
    description="AI Agent with LLM + Tools + Memory + Planning",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
from fastapi.staticfiles import StaticFiles
web_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web")
app.mount("/static", StaticFiles(directory=web_dir), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web interface"""
    with open(os.path.join(web_dir, "index.html"), "r", encoding="utf-8") as f:
        return f.read()


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for chat"""
    client_id = str(id(websocket))
    await manager.connect(websocket, client_id)

    # Create agent instance for this session
    agent = create_agent()

    try:
        # Send welcome message
        await manager.send_json({
            "type": "assistant",
            "content": "WorkAI Agent 已启动。我可以帮你查询天气🌤️、进行计算🔢。有什么可以帮助你的？"
        }, client_id)

        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if message_data.get("type") == "reset":
                agent.reset_memory()
                await manager.send_json({
                    "type": "system",
                    "content": "记忆已清空"
                }, client_id)
                continue

            user_message = message_data.get("content", "")

            # Process message through agent
            try:
                response = await agent.think(user_message)

                # Send response back to client
                await manager.send_json({
                    "type": "assistant",
                    "content": response
                }, client_id)

            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await manager.send_json({
                    "type": "error",
                    "content": f"处理消息时出错: {str(e)}"
                }, client_id)

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(client_id)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "WorkAI Agent"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
