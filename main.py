import os.path
import sqlite3

import ttkbootstrap as ttk
import logging, datetime

from db_access import DatabaseHandler
from gui import CatalystBondScanner

if __name__ == "__main__":

    #logging

    log_file_dir = f'./logs/'
    # log_file_name = f'Catalyst_Bond_Scanner_log_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'
    log_file_name = f'Catalyst_Bond_Scanner.log'

    if not os.path.exists(log_file_dir):
        os.mkdir(log_file_dir)

    logging.basicConfig(filename=f'{log_file_dir}{log_file_name}', filemode='w', encoding='utf-8',
                        level=logging.INFO,
                        format="%(asctime)s %(levelname)s\t%(threadName)s\t%(module)s\t%(funcName)s\t%(message)s")

    #app start

    logging.info("Start")
    window = ttk.Window(title='Skaner Obligacji GPW', themename='darkly')

    database_handler = DatabaseHandler('CBS.db')

    app_instance = CatalystBondScanner(master=window, database_handler=database_handler)

    window.mainloop()