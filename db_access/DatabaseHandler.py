import datetime
import logging
import sqlite3
from importlib import resources
from . import sql_scripts


def script_into_statements(script: str) -> [str]:
    statements = script.split(';')
    return list(filter(lambda x: x!='', statements))

class DatabaseHandler:

    def __init__(self, db_name):
        logging.info('Connecting to the database')
        self.db_name = db_name
        self.sql_scripts = resources.files(__name__).joinpath('sql_scripts')

        self.create_tables()

    def create_tables(self):
        logging.info('Creating tables')
        db_connection = sqlite3.connect(self.db_name)
        cursor = db_connection.cursor()
        with self.sql_scripts.joinpath('create.sql').open('r') as script_file:
            for statement in script_into_statements(script_file.read()):
                try:
                    cursor.execute(statement)
                except sqlite3.Error as e:
                    logging.exception(f'SQL ERROR {e.sqlite_errorcode} : {e.sqlite_errorname}')

    def get_last_modified_date(self) -> datetime.date | None:
        db_connection = sqlite3.connect(self.db_name)
        cursor = db_connection.cursor()

        with self.sql_scripts.joinpath('select', 'select_last_modified_date.sql').open('r') as script_file:
            try:
                result = cursor.execute(script_file.read()).fetchone()
                return datetime.date.fromisoformat(result[0]) if result is not None else None
            except sqlite3.Error as e:
                logging.exception(f'SQL ERROR {e.sqlite_errorcode} : {e.sqlite_errorname}')

    def update_last_modified_date(self):
        db_connection = sqlite3.connect(self.db_name)
        cursor = db_connection.cursor()
        logging.debug("Updating last_modified date")

        with self.sql_scripts.joinpath('update', 'update_last_modified_date.sql').open('r') as script_file:
            try:
                result = cursor.execute(script_file.read())
                db_connection.commit()
            except sqlite3.Error as e:
                logging.exception(f'SQL ERROR {e.sqlite_errorcode} : {e.sqlite_errorname}')

    def drop_tables(self):
        db_connection = sqlite3.connect(self.db_name)
        cursor = db_connection.cursor()
        logging.warning("Dropping tables")

        with self.sql_scripts.joinpath('drop.sql').open('r') as script_file:
            for statement in script_into_statements(script_file.read()):
                try:
                    cursor.execute(statement)
                except sqlite3.Error as e:
                    logging.exception(f'SQL ERROR {e.sqlite_errorcode} : {e.sqlite_errorname} \n {statement}')

    def upsert_GPW_bond_list(self, bond_list):
        db_connection = sqlite3.connect(self.db_name)
        cursor = db_connection.cursor()
        logging.info("Upserting bond list")

        with self.sql_scripts.joinpath('upsert', 'upsert_GPW_bond_list.sql').open('r') as script_file:
            script = script_file.read()
            sql_returns = [0, 0, 0, 0, 0]
            for bond in bond_list:
                for i, command in enumerate(script_into_statements(script)):
                    try:
                        result = cursor.execute(command.format(issuer_name=bond[0], code=bond[1], market_name=bond[2], price=bond[3], currency_code=bond[4], instrument_type_name=bond[5]))
                        sql_returns[i] += cursor.rowcount
                        db_connection.commit()
                    except sqlite3.Error as e:
                        logging.exception(f'SQL ERROR {e.sqlite_errorcode} : {e.sqlite_errorname}\n{command.strip()}')

            logging.info('Upserted issuers: {}, markets: {}, instrument types: {}, bonds: {}, bond-markets: {}'.format(*sql_returns))

    def select_bonds_table(self):
        db_connection = sqlite3.connect(self.db_name)
        cursor = db_connection.cursor()
        with self.sql_scripts.joinpath('select', 'select_bonds_table.sql').open('r') as script_file:
            try:
                result = cursor.execute(script_file.read()).fetchall()
                return result
            except sqlite3.Error as e:
                logging.exception(f'SQL ERROR {e.sqlite_errorcode} : {e.sqlite_errorname}')

    def upsert_gpw_bond_detail(self, bond_data):
        db_connection = sqlite3.connect(self.db_name)
        cursor = db_connection.cursor()
        logging.debug(f'Upserting bond {bond_data[0]} from GPW')

        bond_data = list(bond_data)
        if bond_data[5] is None:
            bond_data[5] = 'NULL'
        if bond_data[6] is None:
            bond_data[6] = 'NULL'

        with self.sql_scripts.joinpath('upsert', 'upsert_GPW_bond_detail.sql').open('r') as script_file:
            payload = script_file.read()
            for command in script_into_statements(payload):
                try:
                    result = cursor.execute(command.format(code=bond_data[0], maturity_date=bond_data[1], par_value=bond_data[2], issue_value=bond_data[3], interest_type_name=bond_data[4], c_interest_rate=bond_data[5], accrued_interest=bond_data[6]))
                    db_connection.commit()
                except sqlite3.Error as e:
                    logging.exception(f'SQL ERROR {e.sqlite_errorcode} : {e.sqlite_errorname}\n{command.strip()}')

    def delete_bond_list(self):
        db_connection = sqlite3.connect(self.db_name)
        cursor = db_connection.cursor()
        logging.warning("Deleting bond list")
        with self.sql_scripts.joinpath('delete', 'delete_bond_list.sql').open('r') as script_file:
            try:
                result = cursor.execute(script_file.read())
                db_connection.commit()
            except sqlite3.Error as e:
                logging.exception(f'SQL ERROR {e.sqlite_errorcode} : {e.sqlite_errorname}')

    def upsert_obligacje_bond_detail(self, parsed_resource):
        db_connection = sqlite3.connect(self.db_name)
        cursor = db_connection.cursor()
        logging.debug(f'Upserting bond {parsed_resource[0]} from Obligacje')

        bond_data = list(parsed_resource)
        if bond_data[1] == 'TAK':
            bond_data[1] = 'TRUE'
        elif bond_data[1] == 'NIE':
            bond_data[1] = 'FALSE'
        else:
            bond_data[1] = '\'NULL\''

        if bond_data[2] is None:
            bond_data[2] = 'NULL'

        if bond_data[3] is None:
            bond_data[3] = 'NULL'

        if bond_data[5] is None:
            bond_data[5] = 'NULL'

        with self.sql_scripts.joinpath('upsert', 'upsert_obligacje_bond_detail.sql').open('r') as script_file:
            payload = script_file.read()
            for command in script_into_statements(payload):
                try:
                    result = cursor.execute(command.format(bond_code=bond_data[0], is_secured=bond_data[1], index_name=bond_data[2], base_interest_rate=bond_data[3], additional_info=bond_data[5].replace("'", "''")))
                    db_connection.commit()
                except sqlite3.Error as e:
                    logging.exception(f'SQL ERROR {e.sqlite_errorcode} : {e.sqlite_errorname}\n{command.strip()}')

        with self.sql_scripts.joinpath('upsert', 'upsert_obligacje_bond_payment_dates.sql').open('r') as script_file:
            script = script_file.read()
            for payment_date in bond_data[4]:
                try:
                    result = cursor.execute(script.format(bond_code=bond_data[0], payment_date=payment_date))
                    db_connection.commit()
                except sqlite3.Error as e:
                    logging.exception(f'SQL ERROR {e.sqlite_errorcode} : {e.sqlite_errorname}\n{command.strip()}')

    def upsert_sw_issuer_bonds(self, parsed_resource):
        db_connection = sqlite3.connect(self.db_name)
        cursor = db_connection.cursor()
        logging.debug(f'Upserting {parsed_resource[1]} bonds from Stockwatch')

        with self.sql_scripts.joinpath('upsert', 'upsert_sw_issuer_bonds.sql').open('r') as script_file:
            script = script_file.read()
            for bond_code in parsed_resource[0]:
                for command in script_into_statements(script):
                    try:
                        result = cursor.execute(command.format(bond_code=bond_code, sw_code=parsed_resource[1]))
                        db_connection.commit()
                    except sqlite3.Error as e:
                        logging.exception(f'SQL ERROR {e.sqlite_errorcode} : {e.sqlite_errorname}\n{command.strip()}')