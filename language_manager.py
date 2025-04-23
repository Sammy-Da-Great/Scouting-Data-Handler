'''
Scouting Data Handler, a custom SQL interface
Copyright (C) 2025  Samuel Husmann

You should have received a copy of the GNU General Public License
along with this program. If not, see https://www.gnu.org/licenses/.
'''

import config_maker
import os
from pathlib import Path
import json

language = config_maker.read_global_config().language

no_language = False

try:
    current_language = json.loads(open(f'languages/{language}.json', "r", encoding="utf-8").read())
except Exception as e:
    print(f'Could not read languages/{language}.json\nException: {e}')
    no_language = True

def tr(key):
    buffer = key
    if no_language == False:
        try:
            buffer = current_language[key]
        except:
            print(f'Translation key \"{key}\" in language \"{language}\" does not exist. Returning key name.')
    else:
        print(f'Language \"{language}\" does not exist. Returning key name \"{key}\"')
    return(buffer)