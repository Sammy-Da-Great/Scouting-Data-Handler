import json
from types import SimpleNamespace

class Global_Config:
    def __init__(self, host, user, password): 
        self.host = host
        self.user = user
        self.password = password
    def __str__(self):
        return "{0}, {1}, {2}".format(self.host, self.user, self.password)

def make_config(config, file_name):
    f = open("config/" + file_name,"w")
    f.write(json.dumps(config.__dict__))
    f.close()

make_config(Global_Config("defaultHost", "defaultUser", "defaultPassword"), "global_config.json")

def read_global_config(file_name):
    f = open("config/" + file_name,"r")
    return(Global_Config(**json.loads(f.read())))
    f.close()