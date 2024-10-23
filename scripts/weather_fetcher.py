# scripts/weather_fetcher.py
import requests
import schedule
import time
import logging
import os
import sys
import sqlite3
from datetime import datetime
from smtplib import SMTP

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import API_KEY, CITIES, FETCH_INTERVAL_MINUTES, ALERT_THRESHOLDS, EMAIL_ALERTS

log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Set up logging
log_file_path = os.path.join(log_dir, 'app.log')
logging.basicConfig(filename=log_file_path, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

weather_data = {city: [] for city in CITIES}
alert_counter = {city: 0 for city in CITIES}

# Function to initialize the SQLite database
def init_db():
    conn = sqlite3.connect('data/weather_data.db')
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS daily_summary')

    cursor.execute('''
        CREATE TABLE daily_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            date TEXT,
            avg_temp REAL,
            max_temp REAL,
            min_temp REAL,
            avg_humidity REAL,
            avg_wind_speed REAL,
            dominant_weather TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Utility to convert Kelvin to Celsius
def kelvin_to_celsius(kelvin_temp):
    return kelvin_temp - 273.15

# Function to send email alerts (if enabled)
def send_email_alert(city, temperature):
    if not EMAIL_ALERTS['enable_email']:
        return
    
    try:
        with SMTP(EMAIL_ALERTS['smtp_server'], EMAIL_ALERTS['smtp_port']) as smtp:
            smtp.starttls()  # Secure the connection
            smtp.login(EMAIL_ALERTS['sender_email'], EMAIL_ALERTS['email_password'])
            subject = f"Weather Alert: {city} Temperature Exceeds {ALERT_THRESHOLDS['temperature']}°C"
            body = f"The temperature in {city} has exceeded the threshold. Current temperature: {temperature:.2f}°C."
            msg = f"Subject: {subject}\n\n{body}"
            smtp.sendmail(EMAIL_ALERTS['sender_email'], EMAIL_ALERTS['receiver_email'], msg)
            logging.info(f"Email alert sent for {city} (Temperature: {temperature:.2f}°C)")
    
    except Exception as e:
        logging.error(f"Failed to send email alert: {e}")

# Function to trigger alert based on the threshold
def check_alert(city, temp):
    if temp > ALERT_THRESHOLDS['temperature']:
        alert_counter[city] += 1
        if alert_counter[city] >= ALERT_THRESHOLDS['consecutive_updates']:
            logging.warning(f"ALERT: {city} temperature exceeded {ALERT_THRESHOLDS['temperature']}°C for {ALERT_THRESHOLDS['consecutive_updates']} consecutive updates.")
            print(f"ALERT: {city} temperature exceeded {ALERT_THRESHOLDS['temperature']}°C for {ALERT_THRESHOLDS['consecutive_updates']} consecutive updates.")
            send_email_alert(city, temp)
    else:
        alert_counter[city] = 0

# Fetch weather data from OpenWeatherMap API for a given city
def fetch_weather_data(city):  
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
    
    try:
        response = requests.get(base_url)
        data = response.json()
        
        if response.status_code == 200:
            main_weather = data['weather'][0]['main']
            temp = kelvin_to_celsius(data['main']['temp'])
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            feels_like = kelvin_to_celsius(data['main']['feels_like'])
            timestamp = data['dt']
            
            logging.info(f"City: {city}, Main: {main_weather}, Temp: {temp:.2f}°C, Humidity: {humidity}%, Wind Speed: {wind_speed} m/s, Feels Like: {feels_like:.2f}°C, Timestamp: {timestamp}")
            print(f"City: {city}, Temp: {temp:.2f}°C, Humidity: {humidity}%, Wind Speed: {wind_speed} m/s, Feels Like: {feels_like:.2f}°C")

            weather_data[city].append({
                'temp': temp,
                'humidity': humidity,
                'wind_speed': wind_speed,
                'weather': main_weather,
                'timestamp': timestamp
            })

            check_alert(city, temp)
            return data  

        else:
            logging.error(f"Failed to get data for {city}. Status code: {response.status_code}")
            return {'cod': response.status_code}  
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {'cod': 500}  

# Save daily summaries to the database
def save_daily_summary(city, date, avg_temp, max_temp, min_temp, avg_humidity, avg_wind_speed, dominant_weather):
    conn = sqlite3.connect('data/weather_data.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        INSERT INTO daily_summary (city, date, avg_temp, max_temp, min_temp, avg_humidity, avg_wind_speed, dominant_weather)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (city, date, avg_temp, max_temp, min_temp, avg_humidity, avg_wind_speed, dominant_weather))
    conn.commit()
    conn.close()

# Fetch weather data for all cities and store daily summaries
def fetch_weather_for_all_cities():
    for city in CITIES:
        fetch_weather_data(city)

    for city in CITIES:
        if weather_data[city]:
            temps = [entry['temp'] for entry in weather_data[city]]
            humidities = [entry['humidity'] for entry in weather_data[city]]
            wind_speeds = [entry['wind_speed'] for entry in weather_data[city]]
            main_weathers = [entry['weather'] for entry in weather_data[city]]

            avg_temp = sum(temps) / len(temps)
            max_temp = max(temps)
            min_temp = min(temps)
            avg_humidity = sum(humidities) / len(humidities)
            avg_wind_speed = sum(wind_speeds) / len(wind_speeds)
            dominant_weather = max(set(main_weathers), key=main_weathers.count)

            today = datetime.now().strftime('%Y-%m-%d')
            save_daily_summary(city, today, avg_temp, max_temp, min_temp, avg_humidity, avg_wind_speed, dominant_weather)
            weather_data[city] = []

# Initialize database
init_db()

# Schedule tasks
schedule.every(FETCH_INTERVAL_MINUTES).minutes.do(fetch_weather_for_all_cities)

# Keep the script running to execute the scheduled tasks
if __name__ == "__main__":
    print(f"Starting weather data fetcher... (interval: {FETCH_INTERVAL_MINUTES} minutes)")
    while True:
        schedule.run_pending()
        time.sleep(1)
