'''
Scouting Data Handler, a custom SQL interface
Copyright (C) 2025  Samuel Husmann

You should have received a copy of the GNU General Public License
along with this program. If not, see https://www.gnu.org/licenses/.
'''

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

    return (inspect.signature(funct).parameters, getModule(file, custom)[2])

def saveConversion(convert_data, name):
    db.write_csv(f"{name}", convert_data)

def readConversion(name):
    raw_conversion = db.read_csv(f"{name}")
    conversion = {}
    conversion['format'] = db.read_csv(f"{name}")[0]

    rows = []
    for row_data in raw_conversion[1:]:
        row = {}
        row['name'] = row_data[0]
        row['category'] = row_data[1]
        row['preset'] = row_data[2]

        row['keys'] = row_data[3:]
        rows.append(row)
    
    conversion['rows'] = rows

    return conversion

def runFunct(parameters, file, custom = False):
    funct = getFunct(file, custom)
    return(funct(*parameters))
    
def getFunct(file, custom = False):
    return(getModule(file, custom)[1])

def getModule(file, custom = False):
    import importlib
    if custom == True:
        presetFolder = "ModifyPresets"
    else:
        presetFolder = "DefaultModifyPresets"
    
    function_string = f'ModifyData.{presetFolder}.{os.path.splitext(file)[0]}.funct'
    mod_name, func_name = function_string.rsplit('.',1)
    mod = importlib.import_module(mod_name)
    funct = getattr(mod, func_name)
    return((mod, funct, getattr(mod, "constants")))

def runConversion(convert_data, data, constants):
    if convert_data[0] == data[0]:
        lookup = dict()
        for key in data[0]:
            lookup[str(key)] = len(lookup)

        conversion_names = [conversion[0] for conversion in convert_data[1:]]
        
        conversions = dict()

        for conversion_data in convert_data[1:]:
            conversion = {}
            conversion['category'] = conversion_data[1]
            conversion['preset'] = conversion_data[2]
            conversion['parameters'] = conversion_data[3:]
            conversion['data_type'] = getModule(conversion['preset'], custom = (conversion['category'] == "Custom"))[0].data_type
            conversions[conversion_data[0]] = conversion

        for conversion_data in list(zip(conversion_names, constants[1:])):
            conversions[conversion_data[0]]['parameters'] = list(zip(conversions[conversion_data[0]]['parameters'], conversion_data[1]))

        
        data_rows = []

        for data_row in data[2:]:

            row = []
            for key in conversion_names:
                conversion = conversions[key]

                parameters = []
                for parameter in conversion['parameters']:
                    parameter_buffer = None

                    if not(parameter[1]): # If dropdown
                        parameter_buffer = data_row[lookup[parameter[0]]]
                    elif parameter[1]:
                        parameter_buffer = parameter[0]
                    parameters.append(parameter_buffer) 

                row.append(runFunct(parameters, conversion['preset'], conversion['category'] == "Custom"))

            row = [str(row_item) for row_item in row]
            data_rows.append(row)

        data_format = [conversion_names]
        data_format.append([conversions[key]['data_type'] for key in conversion_names])


        return [*data_format, *data_rows]
                                   


                









        '''
        print(convert_data)
        print(constants)

        convert_keys = []
        convert_data_types = []
        for row in convert_data[1:]:
            convert_keys.append(row[0])
            convert_data_types.append(getModule(row[2], row[1] == "Custom")[0].data_type)
            
        rows = []
        rows.append(convert_keys)
        rows.append(convert_data_types)

        for data_row in data[2:]:
            row = []
            print(list(zip(convert_data[1][3:], constants)))
            for convert_item in list(zip(convert_data[1][3:], constants)):
                print(convert_item)
                parameters = []
                for parameter in convert_item:
                    if parameter[1] == True:
                        parameters.append(parameter[0])
                    elif parameter[1] == False:
                        parameters.append(data_row[lookup[str(parameter[0])]])
                row.append(runFunct(parameters, convert_row[2], convert_row[1] == "Custom"))
            rows.append(row)
        
        return(rows)'''
    else:
        print("error, keys of original do not match the keys of the table")