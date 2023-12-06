import wx
import threading
from main import main


class App(wx.App):
    def __init__(self):
        super().__init__(clearSigInt=True)

        self.InitFrame()

    def InitFrame(self):  # Renders window
        frame = Frame(parent=None, title="Weather Processing", pos=(100, 100))
        frame.Show()


class Frame(wx.Frame):
    def __init__(self, parent, title, pos):
        super().__init__(parent=parent, title=title, pos=pos)
        self.OnInit()

    def OnInit(self):
        panel = Panel(parent=self)


class Panel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.updateOptions = wx.StaticText(
            self, id=wx.ID_ANY, label="Generate box plot:", pos=(22, 10))

        self.startYear = wx.StaticText(
            self, id=wx.ID_ANY, label="Start year:", pos=(22, 30))
        self.startYearInput = wx.TextCtrl(
            self, id=wx.ID_ANY, size=(60, 16), style=wx.NO_BORDER, pos=(85, 31))  # Input box

        self.endYear = wx.StaticText(
            self, id=wx.ID_ANY, label="End year:", pos=(22, 50))
        self.endYearInput = wx.TextCtrl(
            self, id=wx.ID_ANY, size=(60, 16), style=wx.NO_BORDER, pos=(85, 51))  # Input box

        # Buttons
        self.boxPlotButton = wx.Button(
            parent=self, label="Generate", pos=(20, 70))
        self.updateButton = wx.Button(
            parent=self, label="Update database", pos=(20, 175))
        # Status Text
        self.statusText = wx.StaticText(
            self, id=wx.ID_ANY, label="", pos=(150, 180))

        # Bind the update button to the event handler
        self.updateButton.Bind(wx.EVT_BUTTON, self.onUpdateDatabase)

    def onUpdateDatabase(self, event):
        # Display the loading message
        self.statusText.SetLabel("Updating... may take a few minutes")

        # Run the database update in a separate thread to keep the UI responsive
        threading.Thread(target=self.runDatabaseUpdate).start()

    def runDatabaseUpdate(self):
        # Call the main function from main.py to run the database update
        main()

        # After the main function is complete, update the status text
        # This must be run on the main thread since it updates the GUI
        wx.CallAfter(self.statusText.SetLabel, "Database updated")


if __name__ == "__main__":
    app = App()
    app.MainLoop()
