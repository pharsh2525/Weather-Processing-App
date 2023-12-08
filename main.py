"""
 Name: Harshkumar Patel & Brenan Hermann
 Date: 16 November 2023
 Project: Weather Processing App
"""

from scrape_weather import WeatherScraper  # Import your WeatherProcessor class
from db_operations import DBOperations  # Import your DBOperations class


def main():
    # Initialize the weather scraper and scrape the data
    scraper = WeatherScraper()
    weather_data = scraper.run()

    # Initialize the database operations
    db_ops = DBOperations()

    # Save the scraped data to the database
    db_ops.save_data(weather_data)

    # start_date = '2000-01-01'
    # end_date = '2000-12-31'

    # Fetch data from the database
    # fetched_data = db_ops.fetch_data(start_date, end_date)
    # print("Fetched Data:")
    # for row in fetched_data:
    #     print(row)


if __name__ == "__main__":
    main()
