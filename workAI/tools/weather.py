"""
Weather Tool - Real-time weather information
"""
import requests
from urllib.parse import quote
from tools.base import Tool, ToolResult


class WeatherTool(Tool):
    """Get real-time weather for a location"""

    # 英文天气状况转中文映射
    WEATHER_CN = {
        "sunny": "晴天",
        "clear": "晴",
        "partly cloudy": "多云",
        "partly sunny": "多云",
        "cloudy": "阴天",
        "overcast": "阴",
        "mist": "薄雾",
        "fog": "大雾",
        "rain": "雨",
        "light rain": "小雨",
        "moderate rain": "中雨",
        "heavy rain": "大雨",
        "showers": "阵雨",
        "thunderstorm": "雷暴",
        "snow": "雪",
        "light snow": "小雪",
        "heavy snow": "大雪",
        "sleet": "雨夹雪",
        "hail": "冰雹",
        "wind": "大风",
        "hot": "炎热",
        "cold": "寒冷",
        "humid": "潮湿",
        "haze": "雾霾",
        "smoke": "烟雾",
    }

    # 中文城市名到英文的映射
    CITY_MAP = {
        "北京": "Beijing",
        "上海": "Shanghai",
        "广州": "Guangzhou",
        "深圳": "Shenzhen",
        "杭州": "Hangzhou",
        "成都": "Chengdu",
        "重庆": "Chongqing",
        "武汉": "Wuhan",
        "西安": "Xian",
        "南京": "Nanjing",
        "天津": "Tianjin",
        "苏州": "Suzhou",
        "长沙": "Changsha",
        "青岛": "Qingdao",
        "沈阳": "Shenyang",
        "大连": "Dalian",
        "厦门": "Xiamen",
        "郑州": "Zhengzhou",
        "济南": "Jinan",
        "福州": "Fuzhou",
        "东京": "Tokyo",
        "伦敦": "London",
        "纽约": "New+York",
        "巴黎": "Paris",
        "悉尼": "Sydney",
        "新加坡": "Singapore",
        "香港": "Hong+Kong",
        "台北": "Taipei",
    }

    @property
    def name(self) -> str:
        return "get_weather"

    @property
    def description(self) -> str:
        return "获取城市天气信息。输入：城市名称。输出：温度、天气状况、湿度、风速、体感温度等。"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称（中文或英文），如：北京、Tokyo、Shanghai"
                }
            },
            "required": ["city"]
        }

    def _translate_weather(self, weather_en: str) -> str:
        """将英文天气翻译为中文"""
        weather_lower = weather_en.lower().strip()
        return self.WEATHER_CN.get(weather_lower, weather_en)

    def _convert_city(self, city: str) -> str:
        """将中文城市名转换为英文"""
        city_stripped = city.strip()
        # 先检查映射表
        if city_stripped in self.CITY_MAP:
            return self.CITY_MAP[city_stripped]
        # 如果已经是英文，直接返回
        return city_stripped

    def execute(self, city: str) -> ToolResult:
        try:
            # 转换城市名为英文
            city_en = self._convert_city(city)

            # 使用 wttr.in API
            url = f"https://wttr.in/{city_en}?format=j1"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=10, headers=headers)

            if response.status_code == 200:
                data = response.json()
                current = data.get("current_condition", [{}])[0]

                # 获取温度数据
                temp = current.get("temp_C", "N/A")
                feels_like = current.get("FeelsLikeC", "N/A")

                # 获取天气预报获取最高最低温度 (wttr.in提供3天预报)
                weather_data = data.get("weather", [{}])
                if weather_data and len(weather_data) > 1:
                    max_temp = weather_data[1].get("maxtempC", "N/A")
                    min_temp = weather_data[1].get("mintempC", "N/A")
                    temp_range = f"{min_temp}°C ~ {max_temp}°C"
                else:
                    temp_range = "暂无数据"

                # 获取天气状况
                weather_desc_en = current.get("weatherDesc", [{}])[0].get("value", "N/A")
                weather_desc_cn = self._translate_weather(weather_desc_en)

                # 获取湿度和风速
                humidity = current.get("humidity", "N/A")
                wind = current.get("windspeedKmph", "N/A")
                wind_dir = current.get("winddir16Point", "N/A")

                # 紫外线指数
                uv_index = current.get("uvIndex", "N/A")

                # 格式化输出为漂亮的中文格式
                result = f"""🌤️ {city} 天气实况

🌡️ 当前温度: {temp}°C
🔆 体感温度: {feels_like}°C
📈 今日气温: {temp_range}
☁️ 天气状况: {weather_desc_cn}
💧 空气湿度: {humidity}%
🌬️ 风速: {wind} km/h
🧭 风向: {wind_dir}
☀️ 紫外线指数: {uv_index}"""

                return ToolResult(success=True, output=result)
            else:
                return ToolResult(success=False, output=None, error=f"API 返回状态 {response.status_code}")

        except requests.RequestException as e:
            return ToolResult(success=False, output=None, error=f"网络错误: {str(e)}")
