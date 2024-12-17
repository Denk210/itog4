import requests
from bs4 import BeautifulSoup

def get_location_by_ip():
    url = "https://ipinfo.io/json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        city = data.get("city")
        return city
    return None

def get_yandex_weather(city):
    url = f"https://yandex.ru/pogoda/{city}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Не удалось получить данные для города {city}.")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        # Температура
        temperature = soup.find("div", class_="temp fact__temp fact__temp_size_s").text.strip()
        # Описание погоды
        weather_description = soup.find("div", class_="link__condition day-anchor i-bem").text.strip()
        # Влажность
        humidity = soup.find("div", class_="term term_orient_v fact__humidity").find("div", class_="term__value").text.strip()
        # Скорость ветра
        wind = soup.find("span", class_="wind-speed").text.strip()
        wind_unit = soup.find("span", class_="fact__unit").text.strip()
        wind_info = f"{wind} {wind_unit}"

        # Формируем результат
        weather_data = {
            "city": city,
            "temperature": temperature,
            "description": weather_description,
            "humidity": humidity,
            "wind": wind_info,
        }
        return weather_data
    except AttributeError as e:
        print(f"Не удалось найти данные о погоде: {e}")
        return None