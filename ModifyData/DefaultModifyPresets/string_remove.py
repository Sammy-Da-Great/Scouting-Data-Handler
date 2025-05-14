from ModifyData.ModifyPresetPreset import *

data_type = "varchar(45)"
constants = ["remove", "replace"]

def funct(string, remove, replace):
    return (string.replace(remove, replace))