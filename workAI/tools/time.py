"""
Time Tool - Real-time time information
"""
from datetime import datetime
from zoneinfo import ZoneInfo
from tools.base import Tool, ToolResult


class TimeTool(Tool):
    """Get current time for a timezone"""

    # Common timezone mappings
    TIMEZONES = {
        "beijing": "Asia/Shanghai",
        "shanghai": "Asia/Shanghai",
        "tokyo": "Asia/Tokyo",
        "london": "Europe/London",
        "new york": "America/New_York",
        "los angeles": "America/Los_Angeles",
        "paris": "Europe/Paris",
        "sydney": "Australia/Sydney",
        "utc": "UTC",
        "gmt": "UTC",
        "香港": "Asia/Hong_Kong",
        "新加坡": "Asia/Singapore",
        "迪拜": "Asia/Dubai",
        "莫斯科": "Europe/Moscow",
        "东京": "Asia/Tokyo",
        "伦敦": "Europe/London",
        "纽约": "America/New_York",
        "巴黎": "Europe/Paris",
        "北京时间": "Asia/Shanghai",
    }

    @property
    def name(self) -> str:
        return "get_time"

    @property
    def description(self) -> str:
        return "获取时区时间。输入：城市名称或时区（可选）。输出：当前时间、日期、时区信息。"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "城市名称（支持中英文）或时区，如：北京、Tokyo、Asia/Shanghai"
                }
            },
            "required": []
        }

    def execute(self, location: str = None) -> ToolResult:
        try:
            # Determine timezone
            tz = self._get_timezone(location)

            # Get current time
            if tz != "local":
                now = datetime.now(ZoneInfo(tz))
                tz_display = tz
            else:
                now = datetime.now()
                tz_display = "本地时间"

            # Format output as friendly Chinese text
            weekday = now.strftime("%A")
            weekday_cn = self._get_weekday_cn(now.weekday())

            result = f"""🕐 {location or '本地'} 时间

📅 {now.strftime('%Y年%m月%d日')}
📆 {weekday_cn} ({weekday})
⏰ {now.strftime('%H:%M:%S')}
🌍 时区: {tz_display}"""

            return ToolResult(success=True, output=result)

        except Exception as e:
            return ToolResult(success=False, output=None, error=f"获取时间失败: {str(e)}")

    def _get_timezone(self, location: str = None) -> str:
        """Get timezone from location string"""
        if not location:
            return "local"

        location_lower = location.lower().strip()

        # Check known locations
        if location_lower in self.TIMEZONES:
            return self.TIMEZONES[location_lower]

        # Try to use as direct timezone string
        try:
            ZoneInfo(location)
            return location
        except Exception:
            pass

        # Try Chinese location
        for cn_name, tz in self.TIMEZONES.items():
            if cn_name in location_lower or location_lower in cn_name:
                return tz

        return "local"

    def _get_weekday_cn(self, idx: int) -> str:
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        return weekdays[idx]


class CurrentTimeTool(TimeTool):
    """Simpler time tool - always returns local current time"""

    @property
    def name(self) -> str:
        return "current_time"

    @property
    def description(self) -> str:
        return "获取当前本地时间。无需输入。返回：时间、日期、日期时间字符串。"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

    def execute(self) -> ToolResult:
        return super().execute(location=None)
