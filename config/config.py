# config/config.py

API_KEY = ''  # Replace with your OpenWeatherMap API key

# List of Indian cities to monitor
CITIES = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']

# Interval for scheduling (in minutes)
FETCH_INTERVAL_MINUTES = 1

# User-configurable thresholds for alerts
ALERT_THRESHOLDS = {
    'temperature': 35,
    'consecutive_updates': 2
}

# Email configuration for sending alerts (optional)
EMAIL_ALERTS = {
    'enable_email': False,
    'smtp_server': 'smtp.example.com',
    'smtp_port': 587,
    'sender_email': 'your_email@example.com',
    'receiver_email': 'receiver_email@example.com',
    'email_password': 'your_email_password'
}