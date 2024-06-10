import json

class global_config:
    def __init__(self, host, user, password): 
        self.host = host
        self.user = user
        self.password = password

def make_config(config, file_name):
    f = open("config/" + file_name,"w")
    f.write(json.dumps(config.__dict__))
    f.close

make_config(global_config("testHost", "testuser", "testPassword"), "global_config.json")