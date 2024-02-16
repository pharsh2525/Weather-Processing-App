"""
 Name: Harshkumar Patel & Brenan Hermann
 Date: 16 November 2023
 Project: Weather Processing App
"""

from scrape_weather import WeatherScraper
from db_operations import DBOperations


def main():
    # Initialize the weather scraper and scrape the data
    scraper = WeatherScraper()
    weather_data = scraper.run()

    # Initialize the database operations
    db_ops = DBOperations()

    # Save the scraped data to the database
    db_ops.save_data(weather_data)


if __name__ == "__main__":
    main()
