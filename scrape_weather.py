"""
 Name: Harshkumar Patel & Brennan Hermann
 Date: 16 November 2023
 Project: Weather Processing App
"""

from html.parser import HTMLParser
import urllib.request
from datetime import datetime
from threading import Thread, Lock
from db_operations import DBOperations
from pyparsing import null_debug_action
from dbcm import DBCM


class WeatherScraper(HTMLParser):
    """
    A class for scraping weather data from a specified website.
    """

    def __init__(self):
        super().__init__()
        self.in_table_body = False
        self.current_date = None
        self.weather_data = {}
        self.td_count = 0
        self.temp_data = []
        self.stop_scraping = False
        self.final_end = False
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.db_ops = DBOperations()

    def handle_starttag(self, tag, attrs):
        if self.stop_scraping:  # Stop processing if flag is set
            return

        if tag == "tbody":
            self.in_table_body = True

        elif tag == "tr" and self.in_table_body:
            # Reset data for each table row
            self.td_count = 0
            self.temp_data = []
            self.current_date = None

        elif tag == "abbr" and self.in_table_body:
            for attr in attrs:
                if attr[0] == 'title':
                    # Convert the title to the desired date format before setting it as current date
                    date_str = self.convert_date_format(attr[1])
                    if date_str in self.weather_data:
                        self.final_end = True  # Set the flag to stop scraping
                    else:
                        self.current_date = date_str

                    if self.current_date == "Invalid date format":
                        self.stop_scraping = True  # Set the flag to stop scraping
                        return

        elif tag == "td" and self.in_table_body:
            if self.td_count < 3:  # Only consider the first 3 td tags
                self.td_count += 1
                # Initialize to capture the text content
                self.temp_data.append('')

    def handle_data(self, data):
        if self.in_table_body and self.td_count > 0 and self.td_count <= 3:
            # Strip leading/trailing whitespace and check if the data is non-empty
            data = data.strip()
            if data and self.temp_data[self.td_count - 1] == '':
                # Handle special notations or non-numeric parts
                if "LegendM" in data:
                    # Set as None for 'LegendM'
                    self.temp_data[self.td_count - 1] = None
                else:
                    # Extract numeric part from the data (e.g., "-1.8E" -> "-1.8")
                    numeric_data = ''.join(
                        filter(lambda x: x.isdigit() or x == '.' or x == '-', data))
                    # Check if the extracted data starts with a negative sign
                    if data.startswith('-') and not numeric_data.startswith('-'):
                        numeric_data = '-' + numeric_data
                    self.temp_data[self.td_count -
                                   1] = numeric_data if numeric_data else None

    def handle_endtag(self, tag):
        if tag == "tbody":
            self.in_table_body = False

        elif tag == "tr" and self.in_table_body and not self.final_end:
            # Check if the date and temperature data are valid
            if self.current_date is not None and len(self.temp_data) == 3 and all(data is not None for data in self.temp_data):
                # Create a dictionary for the day's temperatures
                daily_temps = {
                    "Max": self.temp_data[0], "Min": self.temp_data[1], "Mean": self.temp_data[2]}
                # Store it in the weather_data dictionary
                self.weather_data[self.current_date] = daily_temps

    @staticmethod
    def convert_date_format(date_str):
        """
        tries to convert scraped date to YYYY-MM-DD format
        """
        try:
            # Convert the string to a datetime object
            date_obj = datetime.strptime(date_str, '%B %d, %Y')
            # Format the datetime object to the desired format
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            return "Invalid date format"

    def generate_url(self, year, month):
        """
        Dynamically generates URL
        """
        return f"https://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&StartYear=1840&EndYear=2018&Day=1&Year={year}&Month={month}"

    def scrape_weather_data(self, year, month):
        """
        Scrapes data from a given month and year.
        """
        try:
            self.weather_data = {}  # Reset the data for each call
            url = self.generate_url(year, month)
            print(f"{month} - {year}")
            with urllib.request.urlopen(url) as response:
                html = response.read().decode('utf-8')
            self.feed(html)
        except Exception as e:
            print(f"Error scraping weather data for {year}-{month}: {e}")

        return self.weather_data

    def does_data_exist(self, date):
        """
        Check if data for a specific date already exists in the database.
        """

        with DBCM(self.db_ops.db_name) as cursor:
            cursor.execute(
                'SELECT * FROM weather_data WHERE sample_date = ?', (date,))
            return cursor.fetchone() is not None

    def scrape_weather_data_thread(self, year, month, shared_data, lock, shared_flag, last_scraped_date):
        """
        Scrape weather data in a separate thread.
        """
        try:
            if self.does_data_exist(f"{year}-{str(month).zfill(2)}-01"):
                shared_flag['complete'] = True
                return

            monthly_data = self.scrape_weather_data(year, month)

            with lock:
                # Find the earliest date in the current scraping session
                current_earliest_date = min(monthly_data.keys(), default=None)

                # Compare with the last scraped date
                if last_scraped_date['date'] == current_earliest_date:
                    shared_flag['complete'] = True
                else:
                    shared_data.update(monthly_data)
                    # Update the last scraped date
                    last_scraped_date['date'] = current_earliest_date
        except Exception as e:
            print(f"Error scraping weather data for {year}-{month}: {e}")

    def run(self):
        """
        Creates threads and adds data to dictonary
        """
        shared_weather_data = {}
        lock = Lock()
        threads = []
        scraping_complete = {'complete': False}
        # Variable to track the earliest date of the last scraped data
        last_scraped_date = {'date': None}

        current_year, current_month = datetime.now().year, datetime.now().month

        while not scraping_complete['complete']:
            scraper = WeatherScraper()
            thread = Thread(target=scraper.scrape_weather_data_thread, args=(
                current_year, current_month, shared_weather_data, lock, scraping_complete, last_scraped_date))
            threads.append(thread)
            thread.start()

            # Decrement the month and year if needed
            if current_month == 1:
                current_month = 12
                current_year -= 1
            else:
                current_month -= 1

        for thread in threads:
            thread.join()

        sorted_weather_data = dict(
            sorted(shared_weather_data.items(), key=lambda item: item[0]))
        return sorted_weather_data
