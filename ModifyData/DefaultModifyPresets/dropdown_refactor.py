from ModifyData.ModifyPresetPreset import *

data_type = "varchar(45)"
constants = ["original", "modified"]

def funct(dropdown, original, modified):
    conversion = dict(zip(original.split(","), modified.split(",")))
    if (dropdown is None) or (dropdown == 'None'):
        return ""
    else:
        return(conversion[dropdown])