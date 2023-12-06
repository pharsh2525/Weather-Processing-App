"""
 Name: Harshkumar Patel & Brenan Hermann
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
        Inserts data into the table or updates it if the existing temperature data is NULL or an empty string.
        """
        with DBCM(self.db_name) as cursor:
            for date, data in weather_data.items():
                # Skip insertion/update if any of the values are None
                if None in data.values():
                    logging.warning(
                        f"Skipped insertion/update for {date} due to None values in data: {data}")
                    continue

                location = "Winnipeg"  # Assuming 'location' is a constant
                try:
                    # Check if the row exists and if the temperatures are NULL or empty strings
                    cursor.execute('''
                        SELECT min_temp, max_temp, avg_temp FROM weather_data
                        WHERE sample_date = ? AND location = ?
                    ''', (date, location))
                    row = cursor.fetchone()

                    # If row exists and any temperature is NULL or an empty string, update it
                    if row and (row[0] is None or row[0] == '' or row[1] is None or row[1] == '' or row[2] is None or row[2] == ''):
                        cursor.execute('''
                            UPDATE weather_data
                            SET min_temp = ?,
                                max_temp = ?,
                                avg_temp = ?
                            WHERE sample_date = ? AND location = ? AND
                                (min_temp IS NULL OR min_temp = '' OR
                                max_temp IS NULL OR max_temp = '' OR
                                avg_temp IS NULL OR avg_temp = '')
                        ''', (data['Min'], data['Max'], data['Mean'], date, location))
                        logging.info(f"Updated data for {date}.")
                    # If row does not exist, insert it
                    elif not row:
                        cursor.execute('''
                            INSERT INTO weather_data (sample_date, location, min_temp, max_temp, avg_temp)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (date, location, data['Min'], data['Max'], data['Mean']))
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
        Deletes table from table
        """
        purge_query = 'DELETE FROM weather_data'
        with DBCM(self.db_name) as cursor:
            cursor.execute(purge_query)
            logging.info("Data purged from database.")
