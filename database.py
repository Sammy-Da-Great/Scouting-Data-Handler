'''
Scouting Data Handler, a custom SQL interface
Copyright (C) 2025  Samuel Husmann

You should have received a copy of the GNU General Public License
along with this program. If not, see https://www.gnu.org/licenses/.
'''

import mysql.connector
import config_maker

from types import SimpleNamespace
from pathlib import Path
import csv
import os
import json

config = config_maker.read_global_config("global_config.json")

database_name = config.database_name

def read_config():
    config = config_maker.read_global_config("global_config.json")

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
    mydb.commit()
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

def get_csv_from_database(file_name, db_address):
    database = db_address[0]
    table = db_address[1]
    if not os.path.isdir("tmp"):
        os.makedirs("tmp")
    rows = read_table(db_address)

    write_csv('tmp/' + file_name, rows)

    return('tmp/' + file_name)

def write_to_database(data, db_address, columnHeaders):
    if (db_address[0] != None) or (db_address[1] != None):
        database = db_address[0]
        table = db_address[1]
        dataTypes = [dataType.lstrip() for dataType in data[0]]
        data.pop(0)
        createColumnQuery = ""
        for i in range(len(columnHeaders)):
            if (i < len(columnHeaders) - 1):
                createColumnQuery += f'{columnHeaders[i]} {dataTypes[i]}, '
            else:
                createColumnQuery += f'{columnHeaders[i]} {dataTypes[i]}'
        query(f'DROP TABLE IF EXISTS {database}.{table};')
        query(f'CREATE DATABASE IF NOT EXISTS {database};')
        query(f'CREATE TABLE {database}.{table} ({createColumnQuery});')
        for data_row in data:
            row = [data_item.lstrip() for data_item in data_row]
            row_buffer = []
            for item in row:
                print(f'.{item}.')
                if item == 'None':
                    print("None item")
                    row_buffer.append('NULL')
                else:
                    row_buffer.append(item)
            row = row_buffer
            columnQueryList = []
            valueQueryList = []
            separator = ", "
            for i in range(len(columnHeaders)):
                columnQueryList.append(f'{columnHeaders[i]}')
                if row[i] == 'NULL':
                    valueQueryList.append(f'{row[i]}')
                else:
                    valueQueryList.append(f'\"{row[i]}\"')
            columnQuery = separator.join(columnQueryList)
            valueQuery = separator.join(valueQueryList)
            print(columnQuery)
            print(valueQuery)
            ##query("INSERT INTO " + database + "." + table + " (" + columnQuery + ") VALUES (" + valueQuery + ");")
            query(f'INSERT INTO {database}.{table} ({columnQuery}) VALUES ({valueQuery});')
    else:
        print(f'{db_address} is not a valid db_address')

def download_csv_from_database(filepath, db_address):
    database = db_address[0]
    table = db_address[1]
    rows = read_table(db_address)

    write_csv(filepath, rows)

def column_data(db_address, column_name): # Returns json.loads data
    database = db_address[0]
    table = db_address[1]
    query_output = query(f'select * from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME = \'{table}\' and table_schema = \'{database}\' and COLUMN_NAME = \'{column_name}\' ORDER BY ORDINAL_POSITION')
    dict_output = dict()

    columns = [column[0] for column in query_output.description]
    data = [dict(zip(columns, row)) for row in query_output.fetchall()]

    json_data = json.loads(json.dumps(data[0], indent=4))
    return json_data

def columns(db_address): # string[]
    database = db_address[0]
    table = db_address[1]
    return [tupleData[0] for tupleData in columns_and_datatypes(db_address)]

def datatypes(db_address): # string[]
    database = db_address[0]
    table = db_address[1]
    return [tupleData[1] for tupleData in columns_and_datatypes(db_address)]

def columns_and_datatypes(db_address): # (name (string), datatype (string), size(int))
    database = db_address[0]
    table = db_address[1]
    data = query(f'select COLUMN_NAME, COLUMN_TYPE from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME=\'{table}\' and table_schema= \'{database}\' ORDER BY ORDINAL_POSITION').fetchall()
    return data

def get_dimensions(db_address): # Tuple (entry count (int), key count (int))
    database = db_address[0]
    table = db_address[1]
    entry_count = query(f'SELECT COUNT(*) FROM {database}.{table}').fetchall()[0][0]
    key_count = len(columns(db_address))

    return((entry_count, key_count))

def read_table(db_address, header=True, types=True):
    database = db_address[0]
    table = db_address[1]

    rows = query("SELECT * FROM " + database + "." + table + ";").fetchall()
    if types:
        rows.insert(0, datatypes(db_address))
    if header:
        rows.insert(0, columns(db_address))
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

def get_license():
    text = ""
    with open("LICENSE", 'r') as stream:
        lines = stream.readlines()
        text = "".join(lines)
    return(text)

def get_readme():
    text = ""
    with open("README", 'r') as stream:
        lines = stream.readlines()
        text = "".join(lines)
    return(text)
    