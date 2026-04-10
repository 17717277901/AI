"""
Conversation Memory - Stores conversation history
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import json


@dataclass
class Message:
    """A single message in the conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    tool_calls: Optional[List[dict]] = None

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "tool_calls": self.tool_calls
        }


class ConversationMemory:
    """Manages conversation history with context window management"""

    def __init__(self, max_length: int = 100):
        self.messages: List[Message] = []
        self.max_length = max_length

    def add_message(self, role: str, content: str, tool_calls: List[dict] = None):
        """Add a message to memory"""
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            tool_calls=tool_calls
        )
        self.messages.append(message)

        # Trim if exceeds max length
        if len(self.messages) > self.max_length:
            self.messages = self.messages[-self.max_length:]

    def get_messages(self, last_n: int = None) -> List[Message]:
        """Get all messages or last N messages"""
        if last_n:
            return self.messages[-last_n:]
        return self.messages

    def get_context_for_llm(self, system_prompt: str = "") -> List[dict]:
        """Format messages for LLM consumption"""
        context = []
        if system_prompt:
            context.append({"role": "system", "content": system_prompt})

        for msg in self.messages:
            context.append({"role": msg.role, "content": msg.content})

        return context

    def clear(self):
        """Clear all messages"""
        self.messages = []

    def save(self, filepath: str):
        """Save memory to file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([msg.to_dict() for msg in self.messages], f, ensure_ascii=False, indent=2)

    def load(self, filepath: str):
        """Load memory from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.messages = [Message(**msg) for msg in data]
        except FileNotFoundError:
            pass
