import datetime
import logging
import sqlite3
from importlib import resources
from . import sql_scripts

class DatabaseHandler:

    def __init__(self, db_name):
        logging.info('Connecting to the database')
        self.db_connection = sqlite3.connect(db_name, check_same_thread=False)
        self.sql_scripts = resources.files(__name__).joinpath('sql_scripts')

        self.create_tables()

    def create_tables(self):
        logging.info('Creating tables')
        cursor = self.db_connection.cursor()
        with self.sql_scripts.joinpath('create.sql').open('r') as script_file:
            for statement in script_file.read().split(";"):
                try:
                    cursor.execute(statement)
                except sqlite3.Error as e:
                    logging.exception(f'SQL ERROR {e.sqlite_errorcode} : {e.sqlite_errorname}')

    def get_last_modified_date(self) -> datetime.date | None:
        cursor = self.db_connection.cursor()
        with self.sql_scripts.joinpath('select', 'select_last_modified_date.sql').open('r') as script_file:
            try:
                result = cursor.execute(script_file.read()).fetchone()
                return datetime.date.fromisoformat(result[0]) if result is not None else None
            except sqlite3.Error as e:
                logging.exception(f'SQL ERROR {e.sqlite_errorcode} : {e.sqlite_errorname}')

    def update_last_modified_date(self):
        logging.debug("Updating last_modified date")
        cursor = self.db_connection.cursor()
        with self.sql_scripts.joinpath('update', 'update_last_modified_date.sql').open('r') as script_file:
            try:
                result = cursor.execute(script_file.read())
                self.db_connection.commit()
            except sqlite3.Error as e:
                logging.exception(f'SQL ERROR {e.sqlite_errorcode} : {e.sqlite_errorname}')

    def drop_tables(self):
        logging.warning("Dropping tables")
        cursor = self.db_connection.cursor()
        with self.sql_scripts.joinpath('drop.sql').open('r') as script_file:
            for statement in script_file.read().split(";"):
                try:
                    cursor.execute(statement)
                except sqlite3.Error as e:
                    logging.exception(f'SQL ERROR {e.sqlite_errorcode} : {e.sqlite_errorname} \n {statement}')

    def upsert_bond_list(self, bond_list):
        logging.info("Upserting bond list")
        cursor = self.db_connection.cursor()

        with self.sql_scripts.joinpath('upsert', 'upsert_bond_list.sql').open('r') as script_file:
            script = script_file.read()
            for bond in bond_list:
                payload = script.format(issuer_name=bond[0], code=bond[1], market_name=bond[2], price=bond[3].replace(',', '.'), currency_code=bond[4])
                for command in payload.split(';'):
                    try:
                        result = cursor.execute(command)
                        self.db_connection.commit()
                    except sqlite3.Error as e:
                        logging.exception(f'SQL ERROR {e.sqlite_errorcode} : {e.sqlite_errorname}\n{command.strip()}')