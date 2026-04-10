"""
Agent - Main agent implementation with LLM + Tools + Memory + Planning
"""
import asyncio
from typing import List, Dict, Any
from agent.llm import LLMClient
from memory.conversation import ConversationMemory
from planning.planner import Planner, Plan, StepStatus
from tools.base import Tool, ToolResult
from config import MEMORY_MAX_LENGTH


class Agent:
    """
    Agent with:
    - LLM: Language model for reasoning
    - Tools: Real-time tools (weather, calculator, etc.)
    - Memory: Conversation history
    - Planning: Task decomposition
    """

    def __init__(
        self,
        llm_client: LLMClient,
        tools: List[Tool],
        memory: ConversationMemory = None,
        planner: Planner = None,
        system_prompt: str = ""
    ):
        self.llm = llm_client
        self.tools = {tool.name: tool for tool in tools}
        self.memory = memory or ConversationMemory(max_length=MEMORY_MAX_LENGTH)
        self.planner = planner or Planner(llm_client)
        self.system_prompt = system_prompt or """You are a helpful AI assistant with access to various tools.
When you need real-time information or need to perform calculations, use the available tools.
Always be clear about what you're doing and why."""

    async def think(self, user_input: str) -> str:
        """Main agent loop - think, act, respond"""
        # Add user message to memory
        self.memory.add_message("user", user_input)

        # Get conversation history for context
        messages = self.memory.get_context_for_llm(self.system_prompt)

        # Format tools for LLM
        tools_for_llm = self.llm.format_tools_for_llm(list(self.tools.values()))

        # Get LLM response with tool availability
        response = await self.llm.generate_with_history(
            messages=messages,
            system_prompt=self.system_prompt,
            tools=tools_for_llm
        )

        text = response["text"]
        tool_calls = response.get("tool_calls", [])

        # Execute tool calls if present
        if tool_calls:
            tool_results = await self._execute_tool_calls(tool_calls)
            text += "\n\n" + tool_results

            # Add assistant response to memory
            self.memory.add_message("assistant", text, tool_calls)

            # If more tool calls came back, continue loop
            # (simplified: just return for now)
        else:
            self.memory.add_message("assistant", text)

        return text

    async def _execute_tool_calls(self, tool_calls: List[Dict]) -> str:
        """Execute a list of tool calls"""
        results = []

        for call in tool_calls:
            tool_name = call["name"]
            tool_input = call["input"]
            tool_id = call["id"]

            if tool_name in self.tools:
                tool = self.tools[tool_name]
                result = await asyncio.to_thread(tool.execute, **tool_input)

                if result.success:
                    # 直接返回工具结果，不添加前缀
                    results.append(str(result.output))
                else:
                    results.append(f"⚠️ 错误: {result.error}")
            else:
                results.append(f"⚠️ 错误: 未知工具 {tool_name}")

        return "\n".join(results)

    async def plan_and_execute(self, goal: str) -> str:
        """Use planning to break down and execute a complex task"""
        tools_for_planner = self.llm.format_tools_for_llm(list(self.tools.values()))
        plan = await self.planner.create_plan(goal, tools_for_planner)

        results = [f"Plan created for: {goal}\n"]

        for step in plan.steps:
            self.planner.update_step_status(plan, step.id, StepStatus.IN_PROGRESS)
            results.append(f"\nExecuting Step {step.id}: {step.description}")

            if step.tool_name and step.tool_name in self.tools:
                tool = self.tools[step.tool_name]
                # For planning, we just describe what would happen
                results.append(f"  -> Would use tool: {step.tool_name}")

            self.planner.update_step_status(plan, step.id, StepStatus.COMPLETED)

        results.append("\n" + "=" * 50)
        results.append("Plan execution complete!")

        return "\n".join(results)

    def chat(self, user_input: str) -> str:
        """Synchronous wrapper for think()"""
        return asyncio.run(self.think(user_input))

    def reset_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
