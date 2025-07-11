'''
Coalition DataBeam, a custom SQL interface
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

def readConversion(filepath):
    raw_conversion = db.read_csv(filepath)
    conversion = {}
    conversion['format'] = db.read_csv(filepath)[0]

    rows = []
    for row_data in raw_conversion[1:]:
        row = {}
        row['name'] = row_data[0]
        row['category'] = row_data[1]
        row['preset'] = row_data[2]

        row['keys'] = row_data[3:]
        row['constants'] = getModule(row['preset'], custom= (row['category'] == "Custom"))[2]
        row['constants'] = [key in row['constants'] for key in getParams(row['preset'], custom= (row['category'] == "Custom"))]
        rows.append(row)
    
    conversion['rows'] = rows

    return conversion

def runFunct(parameters, file, custom = False):
    funct = getFunct(file, custom)
    parameters_buffer = []
    for parameter in parameters:
        if parameter == "None" or parameter == '':
            parameters_buffer.append(None)
        else:
            parameters_buffer.append(parameter)
    return(funct(*parameters_buffer))
    
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
    return((mod, funct, getattr(mod, "constants"), getattr(mod, "get_data_type")))

def runConversion(convert_data, data, constants):
    if all(key in convert_data[0] for key in data[0]):
        lookup = dict()
        for key in data[0]:
            lookup[str(key)] = len(lookup)

        lookup_datatype = dict()
        for key_datatype_pair in list(zip(data[0], data[1])):
            lookup_datatype[str(key_datatype_pair[0])] = str(key_datatype_pair[1])

        conversion_names = [conversion[0] for conversion in convert_data[1:]]
        
        conversions = dict()

        for conversion_data_pair in list(zip(convert_data[1:], range(len(convert_data[1:])))):
            conversion_data = conversion_data_pair[0]
            conversion = {}
            conversion['category'] = conversion_data[1]
            conversion['preset'] = conversion_data[2]
            conversion['parameters'] = conversion_data[3:]


            module = getModule(conversion['preset'], custom = (conversion['category'] == "Custom"))

            data_types = []
            parameters = list(zip([not(param in module[2]) for param in inspect.signature(module[1]).parameters], conversion['parameters']))
            for parameter in parameters:
                if parameter[0]:
                    data_types.append(lookup_datatype[parameter[1]])

            #conversion['data_type'] = getModule(conversion['preset'], custom = (conversion['category'] == "Custom"))[0].data_type
            conversion['data_type'] = module[3](getattr(module[0], "data_type"), data_types)

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

                try:
                    row.append(runFunct(parameters, conversion['preset'], conversion['category'] == "Custom"))
                except Exception as e:
                    row.append("ERROR")
                    print(f"preset {conversion['preset']} experienced an error with parameters: {parameters} Error: {e}")


            row = [str(row_item) for row_item in row]
            data_rows.append(row)

        data_format = [conversion_names]
        data_format.append([conversions[key]['data_type'] for key in conversion_names])


        return [*data_format, *data_rows]

    else:
        print("error, keys of original do not match the keys of the table")

def runConversionFromCSV(data, conversion_filepath):
    conversion = readConversion(conversion_filepath)

    convert_data = db.read_csv(conversion_filepath)

    constants = [convert_data[0]]

    for row in conversion['rows']:
        constants.append(row['constants'])
    
    return(runConversion(convert_data, data, constants))
