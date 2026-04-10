"""
Planner - Breaks down tasks into executable steps
"""
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class StepStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PlanStep:
    """A single step in a plan"""
    id: int
    description: str
    tool_name: Optional[str] = None
    status: StepStatus = StepStatus.PENDING
    result: Optional[str] = None


@dataclass
class Plan:
    """A plan containing multiple steps"""
    goal: str
    steps: List[PlanStep] = field(default_factory=list)

    def current_step(self) -> Optional[PlanStep]:
        """Get the current step to execute"""
        for step in self.steps:
            if step.status == StepStatus.PENDING:
                return step
        return None

    def is_complete(self) -> bool:
        """Check if all steps are completed"""
        return all(s.status == StepStatus.COMPLETED for s in self.steps)


class Planner:
    """Plans and executes multi-step tasks"""

    def __init__(self, llm_client):
        self.llm = llm_client

    async def create_plan(self, goal: str, available_tools: List[dict]) -> Plan:
        """Create a plan for the given goal using LLM"""
        tools_desc = "\n".join([
            f"- {t['name']}: {t['description']}" for t in available_tools
        ])

        prompt = f"""You are a task planner. Break down the following goal into clear, executable steps.

Goal: {goal}

Available tools:
{tools_desc}

Create a plan with numbered steps. Each step should:
- Be clearly described
- Specify which tool to use (if any)
- Be atomic (can be executed in one action)

Respond in this format:
STEP 1: [description] -> [tool_name or "none"]
STEP 2: [description] -> [tool_name or "none"]
etc.
"""

        response = await self.llm.generate(prompt)

        # Parse response into Plan
        plan = Plan(goal=goal)
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('STEP') and ':' in line:
                parts = line.split('->')
                desc = parts[0].split(':', 1)[1].strip()
                tool = parts[1].strip() if len(parts) > 1 else None

                plan.steps.append(PlanStep(
                    id=len(plan.steps) + 1,
                    description=desc,
                    tool_name=tool if tool and tool != "none" else None
                ))

        return plan

    def update_step_status(self, plan: Plan, step_id: int, status: StepStatus, result: str = None):
        """Update the status of a step"""
        for step in plan.steps:
            if step.id == step_id:
                step.status = status
                step.result = result
                break
