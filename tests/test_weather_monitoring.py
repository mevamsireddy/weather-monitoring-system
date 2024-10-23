# tests/test_weather_monitoring.py
import unittest
from unittest.mock import patch, MagicMock
import sqlite3
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from scripts.weather_fetcher import (
    fetch_weather_data,
    kelvin_to_celsius,
    save_daily_summary,
    check_alert,
    init_db,
)

class TestWeatherMonitoring(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Setup method to initialize the database for testing."""
        cls.db_path = 'data/test_weather_data.db'
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
        init_db()

    def test_kelvin_to_celsius(self):
        """Test the conversion of Kelvin to Celsius."""
        self.assertAlmostEqual(kelvin_to_celsius(273.15), 0.0)
        self.assertAlmostEqual(kelvin_to_celsius(300), 26.85)

    @patch('scripts.weather_fetcher.requests.get')
    def test_fetch_weather_data_success(self, mock_get):
        """Test successful weather data fetching."""
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {
            'weather': [{'main': 'Clear'}],
            'main': {'temp': 300, 'humidity': 50, 'feels_like': 299.15},
            'wind': {'speed': 5},
            'dt': 1609459200
        })
        result = fetch_weather_data("London")

    @patch('scripts.weather_fetcher.requests.get')
    def test_fetch_weather_data_failure(self, mock_get):
        """Test weather data fetching failure."""
        mock_get.return_value = MagicMock(status_code=404, json=lambda: {})
        result = fetch_weather_data("InvalidCity")
        self.assertEqual(result.get('cod'), 404)

    def test_save_daily_summary(self):
        """Test saving daily summary to the database."""
        save_daily_summary("London", "2022-10-23", 15.0, 20.0, 10.0, 60.0, 5.0, "Clear")
        conn = sqlite3.connect('data/weather_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM daily_summary WHERE city = 'London'")
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], "London")
        conn.close()

    @patch('scripts.weather_fetcher.alert_counter', new_callable=dict)
    def test_check_alert(self, mock_alert_counter):
        """Test the alerting system based on temperature."""
        mock_alert_counter["London"] = 0
        check_alert("London", 25)
        self.assertEqual(mock_alert_counter["London"], 0)

if __name__ == "__main__":
    unittest.main()