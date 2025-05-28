from ModifyData.ModifyPresetPreset import *

data_type = "varchar(45)"
constants = ["splitter", "index"]

def funct(string, splitter, index):
    buffer = string.split(splitter)[int(index)]
    return(buffer)