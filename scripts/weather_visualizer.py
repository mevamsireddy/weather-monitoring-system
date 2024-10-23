import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os

plots_dir = 'plots'
if not os.path.exists(plots_dir):
    os.makedirs(plots_dir)

# Function to fetch daily summaries from the database
def fetch_daily_summaries():
    conn = sqlite3.connect('data/weather_data.db')
    query = '''
        SELECT city, date, avg_temp, max_temp, min_temp, avg_humidity, avg_wind_speed, dominant_weather
        FROM daily_summary
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Function to visualize daily weather summaries
def visualize_daily_summaries():
    df = fetch_daily_summaries()

    df['date'] = pd.to_datetime(df['date'])

    sns.set(style="whitegrid")

    # Plot average temperature
    plt.figure(figsize=(14, 7))
    sns.barplot(data=df, x='date', y='avg_temp', hue='city', errorbar=None)
    plt.title('Average Temperature by City')
    plt.xlabel('Date')
    plt.ylabel('Average Temperature (°C)')
    plt.xticks(rotation=45)
    plt.legend(title='City')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'average_temperature.png'))
    plt.show()

    # Plot average humidity
    plt.figure(figsize=(14, 7))
    sns.barplot(data=df, x='date', y='avg_humidity', hue='city', errorbar=None)
    plt.title('Average Humidity by City')
    plt.xlabel('Date')
    plt.ylabel('Average Humidity (%)')
    plt.xticks(rotation=45)
    plt.legend(title='City')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'average_humidity.png'))
    plt.show()

    # Plot average wind speed
    plt.figure(figsize=(14, 7))
    sns.barplot(data=df, x='date', y='avg_wind_speed', hue='city', errorbar=None)
    plt.title('Average Wind Speed by City')
    plt.xlabel('Date')
    plt.ylabel('Average Wind Speed (m/s)')
    plt.xticks(rotation=45)
    plt.legend(title='City')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'average_wind_speed.png'))
    plt.show()

    # Plot dominant weather conditions
    plt.figure(figsize=(14, 7))
    weather_counts = df['dominant_weather'].value_counts()
    sns.barplot(x=weather_counts.index, y=weather_counts.values)
    plt.title('Dominant Weather Conditions')
    plt.xlabel('Weather Condition')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'dominant_weather_conditions.png'))
    plt.show()

if __name__ == "__main__":
    visualize_daily_summaries()
