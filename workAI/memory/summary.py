"""
Summary Memory - Condenses old memories for long-term retention
"""
from dataclasses import dataclass
from typing import List


@dataclass
class Summary:
    """A condensed summary of past interactions"""
    topic: str
    key_points: List[str]
    timestamp: str


class SummaryMemory:
    """Manages summarized memories for long-term context"""

    def __init__(self):
        self.summaries: List[Summary] = []

    def add_summary(self, topic: str, key_points: List[str], timestamp: str):
        """Add a new summary"""
        self.summaries.append(Summary(topic=topic, key_points=key_points, timestamp=timestamp))

    def get_recent_summaries(self, limit: int = 5) -> List[Summary]:
        """Get recent summaries"""
        return self.summaries[-limit:]

    def search_summaries(self, keyword: str) -> List[Summary]:
        """Search summaries by keyword"""
        return [
            s for s in self.summaries
            if keyword.lower() in s.topic.lower() or any(keyword.lower() in point.lower() for point in s.key_points)
        ]
