"""
 Name: Harshkumar Patel & Brenan Hermann
 Date: 30 November 2023
 Project: Weather Processing App
"""

from dbcm import DBCM
from datetime import datetime
import calendar
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
from db_operations import DBOperations
matplotlib.use('TkAgg')  # Replace 'TkAgg' with your preferred backend


class PlotOperations:

    def __init__(self):
        super().__init__()
        self.db_ops = DBOperations()

    def create_year_boxplot(self, startYear, endYear):
        """
        Creates a boxplot for the mean temperatures of each month from startYear to endYear.
        """
        weatherData = {month: [] for month in range(1, 13)}

        def fetch_and_process_data(startYear, endYear):
            """
            Fetches weather data between startYear and endYear, organizes it by month,
            and calculates the mean temperature for each month.
            """
            with DBCM(self.db_ops.db_name) as cursor:
                for year in range(startYear, endYear + 1):
                    for month in range(1, 13):
                        cursor.execute('''
                            SELECT AVG(avg_temp) FROM weather_data
                            WHERE sample_date BETWEEN ? AND ? AND strftime('%m', sample_date) = ?
                        ''', (f'{year}-{month:02d}-01', f'{year}-{month:02d}-31', f'{month:02d}'))
                        result = cursor.fetchone()
                        if result and result[0] is not None:
                            weatherData[month].append(result[0])

        fetch_and_process_data(startYear, endYear)

        plt.figure()
        plt.title(
            f'Monthly Mean Temperature Distribution from {startYear} to {endYear}')
        plt.xlabel('Month')
        plt.ylabel('Mean Temperature (Celsius)')

        # Prepare the data for boxplot
        data = [weatherData[month] for month in range(1, 13)]

        # Create the boxplot using the processed data
        plt.boxplot(data, showfliers=True)

        # Define the x-axis labels as months
        plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr',
                   'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

        plt.show()

    def create_month_line_plot(self, year, month):
        """
        Creates a line plot for the daily temperatures of a specific month and year.
        """
        def fetch_daily_data(year, month):
            """
            Fetches daily weather data for a specific month and year.
            """
            with DBCM(self.db_ops.db_name) as cursor:
                start_date = f"{year}-{month:02d}-01"
                end_date = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]}"

                cursor.execute('''
                    SELECT sample_date, avg_temp FROM weather_data
                    WHERE sample_date BETWEEN ? AND ?
                    ORDER BY sample_date
                ''', (start_date, end_date))
                return cursor.fetchall()

        daily_data = fetch_daily_data(year, month)

        # Make sure there's data to plot
        if not daily_data:
            print(f"No data found for {year}-{month}.")
            return

        # Separate the data into dates and temperatures
        dates = [mdates.date2num(datetime.strptime(
            row[0], '%Y-%m-%d').date()) for row in daily_data]

        temperatures = [row[1] for row in daily_data]

        # Create the plot
        plt.figure(figsize=(10, 5))
        # 'o' to mark the data points
        plt.plot(dates, temperatures, marker='.')

        # Format the x-axis to show dates nicely
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())

        # Rotate date labels for better readability
        plt.gcf().autofmt_xdate()

        # Add labels and title
        plt.title(f'Daily Temperature for {calendar.month_name[month]} {year}')
        plt.xlabel('Day of the Month')
        plt.ylabel('Temperature (Celsius)')

        plt.grid(True)  # Add a grid for easier reading
        plt.tight_layout()  # Adjust layout to fit everything nicely
        plt.show()
