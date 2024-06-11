import mysql.connector
import config_maker

config = config_maker.read_global_config("global_config.json")

database_name = config.database_name

mydb = mysql.connector.connect(
  host = config.host,
  user = config.user,
  password = config.password
)

mycursor = mydb.cursor()
mycursor.execute("CREATE DATABASE IF NOT EXISTS " + database_name)

#https://www.w3schools.com/python/python_mysql_create_db.asp

mydb = mysql.connector.connect(
  host = config.host,
  user = config.user,
  password = config.password,
  database = config.database_name
)