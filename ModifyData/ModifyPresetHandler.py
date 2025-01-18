import os
import subprocess
import inspect
import database as db #Needs to be run from main folder

preset_path = "ModifyData\\ModifyPresets"
presetpreset = "ModifyData\\ModifyPresetPreset.py"
conversion_path = "ModifyData\\ConversionPresets\\"

def openFolder(): 
    os.startfile(preset_path)

def createFile(name):
    filepath = f"{preset_path}\\{name}"

    with open(presetpreset,'r') as firstfile, open(filepath,'a') as secondfile:
        for line in firstfile:
            secondfile.write(line)

def delFile(name):
    filepath = f"{preset_path}\\{name}"
    os.remove(filepath)

def getParams(file, custom = False): #list of strings
    funct = getFunct(file, custom)
    return [tupleData[0] for tupleData in inspect.signature(funct).parameters]

def saveConversion(convert_data, name):
    db.write_csv(f"{name}", convert_data)

def readConversion(name):
    return db.read_csv(f"{name}")

def runFunct(parameters, file, custom = False):
    funct = getFunct(file, custom)
    return(funct(*parameters))
    
def getFunct(file, custom = False):
    import importlib
    if custom == True:
        presetFolder = "ModifyPresets"
    else:
        presetFolder = "DefaultModifyPresets"
    
    function_string = f'ModifyData.{presetFolder}.{os.path.splitext(file)[0]}.funct'
    mod_name, func_name = function_string.rsplit('.',1)
    mod = importlib.import_module(mod_name)
    funct = getattr(mod, func_name)
    return(funct)

def runConversion(convert_data, data):
    if convert_data[0] == data[0]:
        lookup = dict()
        for key in data[0]:
            lookup[key] = len(lookup)

        convert_keys = []
        for row in convert_data[1:]:
            convert_keys.append(row[0])
            
        rows = []
        rows.append(convert_keys)

        for data_row in data[2:]:
            row = []
            for convert_row in convert_data[1:]:
                parameters = []
                for parameter in convert_row[3:]:
                    parameters.append(data_row[lookup[parameter]])
                row.append(runFunct(parameters, convert_row[2], convert_row[1] == "Custom"))
            rows.append(row)
        
        return(rows)
                
            




    else:
        print("error, keys of original do not match the keys of the table")