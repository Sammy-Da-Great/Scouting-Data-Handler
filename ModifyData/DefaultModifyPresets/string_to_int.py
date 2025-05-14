from ModifyData.ModifyPresetPreset import *

data_type = "smallint unsigned"
constants = []

def funct(string):
    buffer = ''.join(x for x in string if not(x.isdigit()))
    
    return(buffer)