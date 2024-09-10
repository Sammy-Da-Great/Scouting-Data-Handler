from database import *

def create_database(name = database_name):
    query("CREATE DATABASE IF NOT EXISTS " + name)