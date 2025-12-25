import os
import requests

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(city):
    """Отримує погоду для міста. Повертає текстовий опис або None."""
    if not OPENWEATHER_API_KEY:
        return "❌ API ключ погоди не налаштовано."
    
    url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "uk"
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            temp = round(data["main"]["temp"])
            description = data["weather"][0]["description"].capitalize()
            humidity = data["main"]["humidity"]
            return f"🌤 У {city}: {temp}°C, {description}\nВологість: {humidity}%"
        else:
            return "❌ Не вдалося знайти місто. Спробуйте ще раз."
    except Exception as e:
        return "⚠️ Помилка з’єднання з погодним сервісом."