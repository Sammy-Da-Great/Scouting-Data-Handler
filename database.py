import mysql.connector
import config_maker

from types import SimpleNamespace
from pathlib import Path
import csv
import os
import json

config = config_maker.read_global_config("global_config.json")

database_name = config.database_name

def query(query_text, input_data = ""): # cursor
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
    rows = read_table(database, table)

    write_csv('tmp/' + file_name, rows)

    return('tmp/' + file_name)

def download_csv_from_database(filepath, database, table):
    rows = read_table(database, table)

    write_csv(filepath, rows)

def column_data(database, table, column_name): # Returns json.loads data
    query_output = query(f'select * from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME=\'{table}\' and table_schema= \'{database}\' and COLUMN_NAME=\'{column_name}\'')
    dict_output = dict()

    columns = [column[0] for column in query_output.description]
    data = [dict(zip(columns, row)) for row in query_output.fetchall()]

    json_data = json.loads(json.dumps(data[0], indent=4))
    return json_data

def columns(database, table): # string[]
    return [tupleData[0] for tupleData in columns_and_datatypes(database, table)]

def datatypes(database, table): # string[]
    return [tupleData[1] for tupleData in columns_and_datatypes(database, table)]

def columns_and_datatypes(database, table): # (name (string), datatype (string))
    data = query(f'select COLUMN_NAME, DATA_TYPE from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME=\'{table}\' and table_schema= \'{database}\'').fetchall()

    return data

def get_dimensions(database, table): # Tuple (entry count (int), key count (int))
    entry_count = query(f'SELECT COUNT(*) FROM {database}.{table}').fetchall()[0][0]
    key_count = len(columns(database, table))

    return((entry_count, key_count))

def read_table(database, table, header=True, types=True):
    rows = query("SELECT * FROM " + database + "." + table + ";").fetchall()
    if types:
        rows.insert(0, datatypes(database, table))
    if header:
        rows.insert(0, columns(database, table))
    return rows

def read_csv(filepath):
    data = []
    with open(filepath, 'r') as stream:
        for rowdata in csv.reader(stream):
            data.append(rowdata)
    return data

def write_csv(filepath, data):
    if filepath != None:
        with open(filepath, 'w', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerows(data)

def test(filepath):
    return(os.path.isfile(filepath))