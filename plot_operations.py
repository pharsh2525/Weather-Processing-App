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
matplotlib.use('WXAgg')  # Replace 'TkAgg' with your preferred backend


class PlotOperations:

    def __init__(self):
        super().__init__()
        self.db_ops = DBOperations()

    def create_year_boxplot(self, startYear, endYear):
        """
        Creates a boxplot for the mean temperatures of each month from startYear to endYear.
        """
        weatherData = {month: [] for month in range(1, 13)}

        for year in range(startYear, endYear + 1):
            for month in range(1, 13):
                start_date = f"{year}-{month:02d}-01"
                end_date = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]}"
                monthly_data = self.db_ops.fetch_data(start_date, end_date)

                # Extract the avg_temp values
                monthly_avg_temps = [temp[3]
                                     for temp in monthly_data if temp[3] is not None]
                if monthly_avg_temps:
                    month_avg = sum(monthly_avg_temps) / len(monthly_avg_temps)
                    weatherData[month].append(month_avg)

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
        plt.xticks(range(1, 13), calendar.month_abbr[1:13])
        plt.show()

    def create_month_line_plot(self, year, month):
        """
        Creates a line plot for the daily temperatures of a specific month and year.
        """
        # Prepare start and end dates for the query
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]}"

        # Fetch data from the database
        monthly_data = self.db_ops.fetch_data(start_date, end_date)

        # Check if data is available
        if not monthly_data:
            print(f"No data found for {year}-{month}.")
            return

        # Separate the data into dates and temperatures
        dates = [datetime.strptime(row[1], '%Y-%m-%d')
                 for row in monthly_data if row[3] is not None]
        temperatures = [row[3] for row in monthly_data if row[3] is not None]

        # Convert dates for matplotlib
        dates = mdates.date2num(dates)

        # Create the plot
        plt.figure(figsize=(10, 5))

        # '.' to mark the data points
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
