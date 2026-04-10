"""
Date Tool - Real-time date information
"""
from datetime import datetime, date
from tools.base import Tool, ToolResult


class DateTool(Tool):
    """Get current date information"""

    WEEKDAYS_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

    @property
    def name(self) -> str:
        return "get_date"

    @property
    def description(self) -> str:
        return "获取今日日期信息。返回：日期、星期、周数、距离周末天数等。"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

    def execute(self) -> ToolResult:
        try:
            today = date.today()
            now = datetime.now()
            weekday_idx = today.weekday()
            is_weekend = weekday_idx >= 5
            is_friday = weekday_idx == 4
            is_monday = weekday_idx == 0

            # Days until weekend (if not already weekend)
            if is_weekend:
                days_to_weekend_text = "现在是周末！🎉"
            elif is_friday:
                days_to_weekend_text = "今天是周五！明天就是周末啦！🎉"
            else:
                days_to_weekend = 5 - weekday_idx
                days_to_weekend_text = f"距离周末还有 {days_to_weekend} 天"

            # Week of year
            week_number = today.isocalendar()[1]

            # Lunar calendar hint (simplified)
            month = today.month
            day = today.day

            # Get Chinese zodiac animal (simplified, based on year)
            zodiac_animals = ["猴", "鸡", "狗", "猪", "鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊"]
            year = today.year
            zodiac_idx = (year - 2016) % 12
            zodiac = zodiac_animals[zodiac_idx]

            # Season
            if month in [3, 4, 5]:
                season = "🌸 春季"
            elif month in [6, 7, 8]:
                season = "☀️ 夏季"
            elif month in [9, 10, 11]:
                season = "🍂 秋季"
            else:
                season = "❄️ 冬季"

            result = f"""📅 今日日期

🗓️ {today.strftime('%Y年%m月%d日')}
📆 {self.WEEKDAYS_CN[weekday_idx]}
📅 今年的第 {week_number} 周
{season}
🐭 生肖: {zodiac}年
{ days_to_weekend_text }
⏰ 当前时间: {now.strftime('%H:%M:%S')}"""

            return ToolResult(success=True, output=result)

        except Exception as e:
            return ToolResult(success=False, output=None, error=f"获取日期失败: {str(e)}")
