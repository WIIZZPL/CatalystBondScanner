import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from db_access import DatabaseHandler
from gui.tabs.HomeTab import HomeTab
from gui.tabs.ScannerTab import ScannerTab
from gui.tabs.IssuerTab import IssuerTab
from gui.tabs.SyncTab import SyncTab

class CatalystBondScanner(ttk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{i:kwargs[i] for i in kwargs if i!='database_handler'})
        self.database_handler = kwargs['database_handler']
        self.pack(fill=BOTH, expand=YES)

        self.tabs = ttk.Notebook(self, width=1000, height=480)
        self.tabs.pack(pady=10, padx=10, expand=True, fill=BOTH)

        self.home_tab = HomeTab(master=self.tabs)
        self.scanner_tab = ScannerTab(master=self.tabs)
        self.issuer_tab = IssuerTab(master=self.tabs)
        self.sync_tab = SyncTab(master=self.tabs)

        self.tabs.select(3)

        self.tabs.bind("<<NotebookTabChanged>>", self.on_tab_change_event)

    def on_tab_change_event(self, event):
        if self.tabs.select() == '.!catalystbondscanner.!notebook.!hometab':
            self.home_tab.on_tab_show()
        elif self.tabs.select() == '.!catalystbondscanner.!notebook.!synctab':
            self.sync_tab.on_tab_show()

    def switch_and_sync(self):
        self.tabs.select('.!catalystbondscanner.!notebook.!synctab')
        self.sync_tab.sync_button_action()

    def get_database_handler(self) -> DatabaseHandler:
        return self.database_handler