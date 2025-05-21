from ModifyData.ModifyPresetPreset import *

data_type = "varchar(45)"
constants = ["remove", "replace"]

def funct(string, remove, replace):
    if replace is None:
        replace = ""
    return(string.replace(remove, replace))