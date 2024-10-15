import mysql.connector
import config_maker

from types import SimpleNamespace
from pathlib import Path
import csv
import os

config = config_maker.read_global_config("global_config.json")

database_name = config.database_name

def query(query_text, input_data = ""):
    mydb = mysql.connector.connect(
        host = config.host,
        user = config.user,
        password = config.password,
        buffered=True
    )
    cursor = mydb.cursor()
    if input_data == "":
        cursor.execute(query_text)
    else:
        cursor.execute(query_text, input_data)
    return cursor

def get_all_databases():
    current_query = query("SHOW DATABASES;")
    buffer = []
    for x in current_query:
        buffer.append(x[0])
    return(buffer)

def get_all_tables(database):
    current_query = query("SELECT table_name FROM information_schema.tables WHERE table_schema = \'" + database + "\'")
    buffer = []
    for table in [tables[0] for tables in current_query.fetchall()]:
        buffer.append(table)
    return(buffer)

def get_csv_from_database(file_name, database, table):
    if not os.path.isdir("tmp"):
        os.makedirs("tmp")
    rows = query("SELECT * FROM " + database + "." + table + ";").fetchall()
    fp = open('tmp/' + file_name, 'w')
    buffer = csv.writer(fp)
    buffer.writerows(rows)
    fp.close()
    return('tmp/' + file_name)

def download_csv_from_database(file_destination, database, table):
    rows = query("SELECT * FROM " + database + "." + table + ";").fetchall()
    fp = open(file_destination, 'w')
    buffer = csv.writer(fp)
    buffer.writerows(rows)
    fp.close()