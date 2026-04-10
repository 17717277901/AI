"""
WorkAI Agent - Main Entry Point
"""
import asyncio
import os
from dotenv import load_dotenv

from agent import Agent, LLMClient
from memory import ConversationMemory
from planning import Planner
from tools import WeatherTool, CalculatorTool
from utils import setup_logger

# Load environment variables
load_dotenv()

logger = setup_logger("WorkAI")


def create_agent() -> Agent:
    """Create and configure the agent"""
    # Initialize LLM client
    llm_client = LLMClient()

    # Initialize tools
    tools = [
        WeatherTool(),
        CalculatorTool(),
    ]

    # Initialize memory
    memory = ConversationMemory(max_length=100)

    # Initialize planner
    planner = Planner(llm_client)

    # Create agent
    agent = Agent(
        llm_client=llm_client,
        tools=tools,
        memory=memory,
        planner=planner,
        system_prompt="""You are WorkAI, a helpful AI assistant with access to real-time tools.
You can:
- Get current weather information for any city using the weather tool
- Perform mathematical calculations using the calculator tool
- Remember context from our conversation

Be concise, helpful, and proactive in suggesting actions."""
    )

    return agent


async def main():
    """Main interactive loop"""
    logger.info("=" * 50)
    logger.info("WorkAI Agent initialized")
    logger.info("=" * 50)

    agent = create_agent()

    print("\n" + "=" * 50)
    print("WorkAI Agent - Type 'exit' or 'quit' to end")
    print("=" * 50 + "\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nGoodbye!")
                break

            if not user_input:
                continue

            if user_input.lower() == "reset":
                agent.reset_memory()
                print("Memory cleared.\n")
                continue

            # Get agent response
            response = await agent.think(user_input)
            print(f"\nWorkAI: {response}\n")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"Error: {e}\n")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Warning: ANTHROPIC_API_KEY not set in environment or .env file")
        print("Please set it before running the agent.\n")

    asyncio.run(main())
