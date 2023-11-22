"""
 Name: Harshkumar Patel & Brenan Harman
 Date: 16 November 2023
 Project: Weather Processing App
"""

import logging
from dbcm import DBCM

class DBOperations:
    """
    A class for database creation.
    """
    def __init__(self):
        self.db_name = "WeatherProcessor.db"
        self.initialize_db()

    def initialize_db(self):
        """
        create table is its not already created.
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
        with DBCM(self.db_name) as cursor:
            cursor.execute(create_table_query)
            logging.info("Database initialized.")

    def save_data(self, weather_data):
        """
        Inserts data into the table
        """
        insert_query = '''
            INSERT OR IGNORE INTO weather_data (sample_date, location, min_temp, max_temp, avg_temp)
            VALUES (?, ?, ?, ?, ?)
        '''
        with DBCM(self.db_name) as cursor:
            for date, data in weather_data.items():
                # Assuming 'location' is a constant or obtained from somewhere
                location = "Winnipeg"  
                cursor.execute(insert_query, (date, location, data['Min'], data['Max'], data['Mean']))
            logging.info("Data saved to database.")

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
        Deletes table from table
        """
        purge_query = 'DELETE FROM weather_data'
        with DBCM(self.db_name) as cursor:
            cursor.execute(purge_query)
            logging.info("Data purged from database.")
