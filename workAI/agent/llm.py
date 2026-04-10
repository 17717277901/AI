"""
LLM Client - Handles communication with LLM providers
Supports: OpenAI-compatible APIs (DashScope/Qwen, Anthropic, etc.)
"""
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Try import openai, fall back to anthropic if not available
try:
    from openai import OpenAI
    USE_OPENAI = True
except ImportError:
    import anthropic
    USE_OPENAI = False


class LLMClient:
    """Client for LLM interactions - OpenAI compatible API"""

    def __init__(self, api_key: str = None, model: str = None, base_url: str = None):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        self.model = model or os.getenv("MODEL_NAME", "qwen-plus")
        self.base_url = base_url or os.getenv("API_BASE_URL")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4096"))

        if USE_OPENAI and self.base_url:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        else:
            # Fallback to Anthropic direct
            self.client = anthropic.Anthropic(api_key=self.api_key)

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        tools: List[dict] = None
    ) -> str:
        """Generate a response from the LLM"""

        messages = [{"role": "user", "content": prompt}]
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})

        if USE_OPENAI:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            if tools:
                kwargs["tools"] = tools

            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        else:
            # Anthropic
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=messages,
                tools=tools
            )
            return response.content[0].text

    async def generate_with_history(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        tools: List[dict] = None
    ) -> Dict[str, Any]:
        """Generate response with conversation history"""

        # Convert messages format for OpenAI
        if USE_OPENAI:
            formatted_messages = []
            if system_prompt:
                formatted_messages.append({"role": "system", "content": system_prompt})
            formatted_messages.extend(messages)

            kwargs = {
                "model": self.model,
                "messages": formatted_messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            if tools:
                kwargs["tools"] = tools

            response = self.client.chat.completions.create(**kwargs)
            message = response.choices[0].message

            tool_calls = []
            if message.tool_calls:
                for call in message.tool_calls:
                    # Safely parse function arguments
                    try:
                        if isinstance(call.function.arguments, str):
                            import json
                            args = json.loads(call.function.arguments)
                        else:
                            args = call.function.arguments
                    except json.JSONDecodeError:
                        args = {"raw": str(call.function.arguments)}

                    tool_calls.append({
                        "name": call.function.name,
                        "input": args,
                        "id": call.id
                    })

            return {
                "text": message.content or "",
                "tool_calls": tool_calls
            }
        else:
            # Anthropic
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=messages,
                tools=tools
            )

            text_content = []
            tool_use_content = []

            for block in response.content:
                if hasattr(block, 'type'):
                    if block.type == 'text':
                        text_content.append(block.text)
                    elif block.type == 'tool_use':
                        tool_use_content.append({
                            'name': block.name,
                            'input': block.input,
                            'id': block.id
                        })

            return {
                "text": "\n".join(text_content),
                "tool_calls": tool_use_content
            }

    def format_tools_for_llm(self, tools: List) -> List[dict]:
        """Format tools for LLM tool use"""
        formatted = []
        for tool in tools:
            formatted.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            })
        return formatted
