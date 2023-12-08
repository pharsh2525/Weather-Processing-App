"""
 Name: Harshkumar Patel & Brenan Hermann
 Date: 16 November 2023
 Project: Weather Processing App
"""

import logging
from dbcm import DBCM
import os
import sys


class DBOperations:
    """
    A class for database creation.
    """

    def __init__(self):
        # Determine if running as a script or frozen executable
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle, sys._MEIPASS is the path to the bundle
            application_path = getattr(
                sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        else:
            # If the application is run as a script, the path is the current working directory
            application_path = os.path.dirname(os.path.abspath(__file__))

        self.db_name = os.path.join(application_path, "WeatherProcessor.db")
        self.initialize_db()

    def initialize_db(self):
        """
        Create table is its not already created.
        """
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sample_date TEXT,
                location TEXT,
                min_temp REAL,
                max_temp REAL,
                avg_temp REAL,
                UNIQUE(sample_date, location)
            );
        '''
        try:
            with DBCM(self.db_name) as cursor:
                cursor.execute(create_table_query)
                logging.info("Database initialized at {}".format(self.db_name))
        except Exception as e:
            logging.error("Failed to initialize database: {}".format(e))

    def save_data(self, weather_data):
        """
        Inserts data into the table or updates it if the existing temperature data is NULL, an empty string,
        or the string 'NULL'.
        """
        with DBCM(self.db_name) as cursor:
            for date, data in weather_data.items():
                location = "Winnipeg"  # Assuming 'location' is a constant
                try:
                    # Prepare the temperature data, replacing 'M' with None for database insertion
                    min_temp = data['Min'] if data['Min'] != 'M' else None
                    max_temp = data['Max'] if data['Max'] != 'M' else None
                    avg_temp = data['Mean'] if data['Mean'] != 'M' else None

                    # Check if the row exists
                    cursor.execute('''
                        SELECT min_temp, max_temp, avg_temp FROM weather_data
                        WHERE sample_date = ? AND location = ?
                    ''', (date, location))
                    row = cursor.fetchone()

                    # If no row exists, insert
                    if not row:
                        cursor.execute('''
                            INSERT INTO weather_data (sample_date, location, min_temp, max_temp, avg_temp)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (date, location, min_temp, max_temp, avg_temp))
                        logging.info(f"Inserted data for {date}.")

                except Exception as e:
                    logging.error(
                        f"Error saving or updating data for {date}: {e}")

    def fetch_data(self, start_date, end_date):
        """
        Gets data from table
        """
        fetch_query = '''
            SELECT * FROM weather_data
            WHERE sample_date BETWEEN ? AND ?
        '''
        with DBCM(self.db_name) as cursor:
            cursor.execute(fetch_query, (start_date, end_date))
            results = cursor.fetchall()
        return tuple(results)  # Convert the list of rows to a tuple

    def purge_data(self):
        """
        Deletes data from table
        """
        purge_query = 'DELETE FROM weather_data'
        reset_ai_query = 'DELETE FROM sqlite_sequence WHERE name="weather_data"'
        with DBCM(self.db_name) as cursor:
            cursor.execute(purge_query)
            cursor.execute(reset_ai_query)  # Reset the autoincrement counter
            logging.info(
                "Data purged from database and autoincrement counter reset.")
