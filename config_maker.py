import json
from types import SimpleNamespace
from pathlib import Path
import os

class Global_Config:
    def __init__(self, host, user, password, database_name): 
        self.host = host
        self.user = user
        self.password = password
        self.database_name = database_name
    def __str__(self):
        return "{0}, {1}, {2}, {3}".format(self.host, self.user, self.password, self.database_name)

def make_config(config, file_name):
    f = open("config/" + file_name,"w")
    f.write(json.dumps(config.__dict__))
    f.close()

def initialize_configs():
    if not os.path.isdir("config"):
        os.makedirs("config")

    if not(Path("config/global_config.json").is_file()):
        make_config(Global_Config("localHost", "defaultUser", "defaultPassword", "defaultDatabaseName"), "global_config.json")

def read_global_config(file_name = "global_config.json"):
    f = open("config/" + file_name,"r")
    return(Global_Config(**json.loads(f.read())))
    f.close()