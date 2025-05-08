import requests
import json
import time

API_KEY = "0267276dcdc78ea5568eb0db1d52d5cd"
CITY = "London"
OUTPUT_FILE = "weather.json"

def fetch_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    
    try:
        data = response.json()
    except json.JSONDecodeError:
        print("Failed to decode JSON.")
        return

    # Check for API error response
    if response.status_code != 200 or "weather" not in data:
        print("API Error:", data.get("message", "Unknown error"))
        return

    # Save the JSON file
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f)

    # Print weather info
    print("Weather updated:", data["weather"][0]["description"], data["main"]["temp"],"°C")
    print("Wind speed:", data["wind"]["speed"], "m/s", "from", data["wind"]["deg"],"°")

if __name__ == "__main__":
    while True:
        fetch_weather()
        time.sleep(120)  # update every 2 minutes
