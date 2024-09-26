import mysql.connector
import config_maker

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