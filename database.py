import mysql.connector
import config_maker

config = config_maker.read_global_config("global_config.json")

database_name = config.database_name

def query(query_text):
    mydb = mysql.connector.connect(
        host = config.host,
        user = config.user,
        password = config.password
    )
    mycursor = mydb.cursor()
    mycursor.execute(query_text)