"""
 Name: Harshkumar Patel & Brennan Hermann
 Date: 16 November 2023
 Project: Weather Processing App
"""

import threading
import wx
from main import main
from dbcm import DBCM
import logging
from db_operations import DBOperations
from plot_operations import PlotOperations


class App(wx.App):
    """
    Main application class for the Weather Processing App.
    Manages the initialization and rendering of the main application frame.
    """

    def __init__(self):
        """
        Initialize the application.
        """

        super().__init__(clearSigInt=True)
        self.init_frame()

    def init_frame(self):  # Renders window
        """Create and display the main frame of the application."""

        frame = Frame(parent=None, title="Weather Processing",
                      pos=(100, 100))
        frame.Show()


class Frame(wx.Frame):
    """Initialize the frame."""

    def __init__(self, parent, title, pos):
        """Initialize the frame's title and position."""

        super().__init__(parent=parent, title=title, pos=pos, size=(410, 285))
        self.on_init()

    def on_init(self):
        """Initialize the panel within the frame."""

        panel = Panel(parent=self)


class Panel(wx.Panel):
    """Panel to hold all user interface elements for the Weather Processing App."""

    def __init__(self, parent):
        """Initialize the panel and its widgets."""

        super().__init__(parent=parent)
        self.init_ui()

    def init_ui(self):
        """Initialize user interface components and layout."""

        # Year boxplot
        self.boxplot_options = wx.StaticText(
            self, label="Generate box plot of years:", pos=(22, 10))

        self.start_year_label = wx.StaticText(
            self, label="Start year:", pos=(22, 30))
        self.start_year_input = wx.TextCtrl(
            self, size=(34, 16), style=wx.NO_BORDER, pos=(85, 31))

        self.end_year_label = wx.StaticText(
            self,  label="End year:", pos=(22, 50))
        self.end_year_input = wx.TextCtrl(
            self, size=(34, 16), style=wx.NO_BORDER, pos=(85, 51))

        self.start_year_input.SetHint("####")
        self.end_year_input.SetHint("####")

        self.start_year_input.SetMaxLength(4)
        self.end_year_input.SetMaxLength(4)

        self.start_year_input.Bind(wx.EVT_CHAR, self.on_char_input)
        self.end_year_input.Bind(wx.EVT_CHAR, self.on_char_input)

        self.year_boxplot_button = wx.Button(
            parent=self, label="Generate ", pos=(20, 70))
        self.year_boxplot_button.Bind(wx.EVT_BUTTON, self.on_year_box_plot)

        # Month boxplot
        self.boxplot_options2 = wx.StaticText(
            self, label="Generate box plot of a month in year:", pos=(180, 10))

        self.year_label = wx.StaticText(
            self, label="Year:", pos=(180, 30))
        self.year_input = wx.TextCtrl(
            self, size=(34, 16), style=wx.NO_BORDER, pos=(245, 31))

        self.month_label = wx.StaticText(
            self, label="Month:", pos=(180, 50))
        self.month_input = wx.TextCtrl(
            self, size=(17, 16), style=wx.NO_BORDER, pos=(245, 51))

        self.year_input.SetHint("####")
        self.month_input.SetHint("##")

        self.year_input.SetMaxLength(4)
        self.month_input.SetMaxLength(2)

        self.year_input.Bind(wx.EVT_CHAR, self.on_char_input)
        self.month_input.Bind(wx.EVT_CHAR, self.on_char_input)

        self.month_boxplot_button = wx.Button(
            parent=self, label="Generate", pos=(180, 70))
        self.month_boxplot_button.Bind(
            wx.EVT_BUTTON, self.on_month_box_plot)

        self.download_button = wx.Button(
            parent=self, label="Download weather data", pos=(20, 175))
        self.update_button = wx.Button(
            parent=self, label="Update weather data", pos=(20, 175))
        self.purge_button = wx.Button(
            parent=self, label="Purge weather data", pos=(20, 205))

        self.years_label = wx.StaticText(
            self, label="", pos=(25, 150))
        self.update_years_label()

        self.status_text = wx.StaticText(
            self, label="", pos=(175, 179))
        self.purge_text = wx.StaticText(
            self, label="", pos=(175, 210))

        self.update_ui_based_on_data()
        self.update_button.Bind(wx.EVT_BUTTON, self.on_update_database)
        self.download_button.Bind(wx.EVT_BUTTON, self.on_download_database)
        self.purge_button.Bind(wx.EVT_BUTTON, self.on_purge_data)

    def on_download_database(self, event):
        """Handle the event to download data from the database."""

        self.reset_status_text()
        self.status_text.SetLabel("Downloading... May take a few minutes")
        threading.Thread(target=self.run_database_download).start()

    def run_database_download(self):
        """Perform the data download from the database in a separate thread."""

        main()
        self.update_ui_based_on_data()
        self.update_years_label()
        wx.CallAfter(self.status_text.SetLabel, "Weather data downloaded.")

    def on_update_database(self, event):
        """Handle the event to update data in the database."""

        self.reset_status_text()
        self.status_text.SetLabel("Updating...")
        threading.Thread(target=self.run_database_update).start()

    def run_database_update(self):
        """Perform the database update in a separate thread."""

        main()
        self.update_ui_based_on_data()
        self.update_years_label()
        wx.CallAfter(self.status_text.SetLabel, "Weather data updated.")

    def on_char_input(self, event):
        """Restrict text control input to only accept numeric characters."""

        key = event.GetUnicodeKey()
        if key not in range(256):
            event.Skip()
        if chr(key).isdigit() or key < 32:
            event.Skip()

    def check_database_for_data(self):
        """Check if there is any data in the database."""

        db_name = 'WeatherProcessor.db'
        with DBCM(db_name) as cursor:
            cursor.execute("SELECT COUNT(*) FROM weather_data")
            return cursor.fetchone()[0] > 0

    def update_ui_based_on_data(self):
        """Update UI elements based on the presence of data in the database."""

        if self.check_database_for_data():
            self.download_button.Hide()
            self.update_button.Show()
            self.purge_button.Enable(True)
        else:
            self.update_button.Hide()
            self.download_button.Show()
            self.purge_button.Enable(False)

    def on_purge_data(self, event):
        """Handle the event to purge data from the database."""

        self.reset_status_text()
        db_ops = DBOperations()
        db_ops.purge_data()
        self.update_ui_based_on_data()
        self.update_years_label()
        wx.CallAfter(self.purge_text.SetLabel, "Weather data purged.")

    def reset_status_text(self):
        """Reset the status text of all status labels."""

        self.status_text.SetLabel("")
        self.purge_text.SetLabel("")

    def on_year_box_plot(self, event):
        """Generate a box plot for the specified range of years."""

        plot_ops = PlotOperations()
        start_year = self.start_year_input.GetValue()
        end_year = self.end_year_input.GetValue()
        plot_ops.create_boxplot(int(start_year), int(end_year))

    def on_month_box_plot(self, event):
        """Generate a line plot for daily temperatures of a specific month and year."""

        plot_ops = PlotOperations()
        year = self.year_input.GetValue()
        month = self.month_input.GetValue()
        plot_ops.create_monthly_line_plot(int(year), int(month))

    def update_years_label(self):
        """Update the label with available years in the database."""

        years = self.fetch_years()
        years_str = ' - '.join(str(year) for year in years)
        self.years_label.SetLabel(f'Available database years: {years_str}')

    def fetch_years(self):
        """Fetches the earliest and latest years from the database."""

        db_name = 'WeatherProcessor.db'
        with DBCM(db_name) as cursor:
            cursor.execute(
                "SELECT MIN(strftime('%Y', sample_date)) FROM weather_data")
            earliest_year = cursor.fetchone()[0]
            cursor.execute(
                "SELECT MAX(strftime('%Y', sample_date)) FROM weather_data")
            latest_year = cursor.fetchone()[0]

        return [earliest_year, latest_year] if earliest_year is not None else ["Null"]


if __name__ == "__main__":
    app = App()
    app.MainLoop()
