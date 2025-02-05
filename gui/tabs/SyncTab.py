import datetime
import logging
import random
import threading
import time
import tkinter
from threading import Thread, Event

import ttkbootstrap as ttk
from PIL.ImageTk import PhotoImage
from pytablericons import TablerIcons, OutlineIcon

from db_access import DatabaseHandler
from gui import CatalystBondScanner
from scraper.CombinedScraper import CombinedScraper


class SyncTab(ttk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.master: ttk.Notebook = kwargs['master']
        self.app: CatalystBondScanner = self.master.master
        self.tab_icon_img = PhotoImage(TablerIcons.load(OutlineIcon.SEARCH))
        self.pack(fill='both', expand=True)

        self.master.add(self, compound=ttk.TOP, image=self.tab_icon_img, text='Synchronizacja')

        self.top_frame = ttk.Frame(self)
        self.top_frame.pack(fill='x', pady=10, padx=10)
        self.middle_frame = ttk.Frame(self)
        self.middle_frame.pack(fill='both', expand=True, pady=10, padx=10)
        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.pack(fill='x', pady=10, padx=10)

        #top frame

        self.title_label = ttk.Label(self.top_frame, text="Synchronizacja", font=(tkinter.font.nametofont('TkDefaultFont'), 32, 'bold'))
        self.title_label.pack(side='left')

        self.button_frame = ttk.Frame(self.top_frame)
        self.button_frame.pack(side='right', fill='y')

        self.sync_button = ttk.Button(self.button_frame, text="Synchronizuj", command=lambda:self.sync_button_action(), bootstyle=ttk.PRIMARY)
        self.sync_button.pack(side='top', fill='both', expand=True)

        self.update_date_frame = ttk.Frame(self.button_frame)
        self.update_date_frame.pack(side='top')

        self.last_update_text_label = ttk.Label(self.update_date_frame, text="Ostatnio aktualizowane: ")
        self.last_update_text_label.pack(side='left')

        self.last_update_date_label = ttk.Label(self.update_date_frame)
        self.last_update_date_label.pack(side='left')

        #middle frame

        self.bond_list_progress_var = ttk.DoubleVar()
        self.bond_list_frame = ttk.LabelFrame(self.middle_frame, text='Lista obligacje i emitentów')
        self.bond_list_frame.pack(fill='x', padx=10, pady=10)
        self.bond_list_progress = ttk.Progressbar(self.bond_list_frame, variable=self.bond_list_progress_var, maximum=1, bootstyle='success')
        self.bond_list_progress.pack(fill='x', padx=10, pady=10)

        self.bonds_progress_var = ttk.DoubleVar()
        self.bonds_frame = ttk.LabelFrame(self.middle_frame, text='Detale obligacji')
        self.bonds_frame.pack(fill='x', padx=10, pady=10)
        self.bonds_progress = ttk.Progressbar(self.bonds_frame, variable=self.bonds_progress_var, maximum=1, bootstyle='success')
        self.bonds_progress.pack(fill='x', padx=10, pady=10)

        self.issuers_progress_var = ttk.DoubleVar()
        self.issuers_frame = ttk.LabelFrame(self.middle_frame, text='Detale emitentów')
        self.issuers_frame.pack(fill='x', padx=10, pady=10)
        self.issuers_progress = ttk.Progressbar(self.issuers_frame, variable=self.issuers_progress_var, maximum=1, bootstyle='success')
        self.issuers_progress.pack(fill='x', padx=10, pady=10)

        #bottom frame

        self.purge_button = ttk.Button(self.bottom_frame, text='Wyczyść pamięć', command=lambda:self.purge_database(), bootstyle=ttk.DANGER)
        self.purge_button.pack(side='left')

        #scraper
        self.scraper_thread: Thread = None
        self.scraper = CombinedScraper()
        self.scraper.set_database_handler(self.app.get_database_handler())
        self.scraper.set_progress_vars([self.bond_list_progress_var, self.bonds_progress_var, self.issuers_progress_var])

    def on_tab_show(self):
        # last modify date update
        last_modified_date: datetime.date = self.app.get_database_handler().get_last_modified_date()

        if last_modified_date is None:
            self.last_update_date_label.configure(bootstyle='inverse-danger')
            self.last_update_date_label['text'] = 'NIGDY'
        else:
            self.last_update_date_label['text'] = last_modified_date
            days_diff = abs((last_modified_date - datetime.date.today()).days)

            if days_diff < 7:
                self.last_update_date_label.config(bootstyle='inverse-success')
            elif days_diff < 30:
                self.last_update_date_label.config(bootstyle='inverse-warning')
            else:
                self.last_update_date_label.config(bootstyle='inverse-danger')

    def sync_button_action(self):
        if self.sync_button['text'] == 'Synchronizuj':
            self.sync_start()
        elif self.sync_button['text'] == 'Zatrzymaj':
            logging.debug('Synch stop button pressed')
            self.sync_stop()

    def thread_finished_check(self):
        if self.scraper_thread is None:
            return
        elif self.scraper_thread.is_alive():
            self.after(1000, self.thread_finished_check)
        else:
            logging.debug('Synch thread not alive')
            self.sync_stop()

    def sync_start(self):
        self.processing_block()
        self.bond_list_progress_var.set(0)
        self.bonds_progress_var.set(0)
        self.issuers_progress_var.set(0)
        self.scraper_thread = threading.Thread(target=self.sync_run, name="ScraperThread")
        self.scraper_thread.start()
        logging.debug('Synch started')
        self.after(1000, self.thread_finished_check)

    def sync_stop(self):
        self.processing_block()
        logging.debug('Synch stopping')
        self.scraper_thread.join()
        logging.debug('Synch stopped')
        self.scraper_thread = None
        self.processing_unblock()
        self.on_tab_show()

    def sync_run(self):
        #TODO: SYNC & ABORT
        self.scraper.start()

    def purge_database(self):
        #TODO: Okno dialogowe "czy na pewno?"

        logging.warning("Purging database")
        self.processing_block()
        database_handler: DatabaseHandler = self.app.get_database_handler()
        database_handler.drop_tables()
        database_handler.create_tables()
        self.processing_unblock()

        self.bond_list_progress_var.set(0)
        self.bonds_progress_var.set(0)
        self.issuers_progress_var.set(0)

        self.on_tab_show()

    def processing_block(self):
        self.purge_button['state'] = ttk.DISABLED
        self.sync_button['state'] = ttk.DISABLED
        self.bond_list_progress.config(bootstyle='success-striped')
        self.bonds_progress.config(bootstyle='success-striped')
        self.issuers_progress.config(bootstyle='success-striped')

    def processing_unblock(self):
        self.purge_button['state'] = ttk.NORMAL
        self.sync_button['state'] = ttk.NORMAL
        self.bond_list_progress.config(bootstyle='success')
        self.bonds_progress.config(bootstyle='success')
        self.issuers_progress.config(bootstyle='success')
    
    def destroy(self):
        if self.scraper_thread is not None and self.scraper_thread.is_alive():
            self.sync_stop()
        super().destroy()