"""
 Name: Harshkumar Patel & Brenan Hermann
 Date: 30 November 2023
 Project: Weather Processing App
"""

import matplotlib.pyplot as plt
import numpy as np
from dbcm import DBCM


class PlotOperations:

    def __init__(self):
        super().__init__()
        self.db_name = "WeatherProcessor.db"
        self.weatherData = {month: [] for month in range(1, 13)}

    def create_boxplot(self, startYear, endYear):
        """
        Creates a boxplot for the mean temperatures of each month from startYear to endYear.
        """
        def fetch_and_process_data(startYear, endYear):
            """
            Fetches weather data between startYear and endYear, organizes it by month,
            and calculates the mean temperature for each month.
            """
            with DBCM(self.db_name) as cursor:
                for year in range(startYear, endYear + 1):
                    for month in range(1, 13):
                        cursor.execute('''
                            SELECT AVG(avg_temp) FROM weather_data
                            WHERE sample_date BETWEEN ? AND ? AND strftime('%m', sample_date) = ?
                        ''', (f'{year}-{month:02d}-01', f'{year}-{month:02d}-31', f'{month:02d}'))
                        result = cursor.fetchone()
                        if result and result[0] is not None:
                            self.weatherData[month].append(result[0])

        fetch_and_process_data(startYear, endYear)

        plt.figure()
        plt.title(
            f'Monthly Mean Temperature Distribution from {startYear} to {endYear}')
        plt.xlabel('Month')
        plt.ylabel('Mean Temperature (Celsius)')

        # Prepare the data for boxplot
        data = [self.weatherData[month] for month in range(1, 13)]

        # Create the boxplot using the processed data
        plt.boxplot(data, showfliers=True)

        # Define the x-axis labels as months
        plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr',
                   'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

        plt.show()


plot_ops = PlotOperations()
plot_ops.create_boxplot(2000, 2023)  # test
