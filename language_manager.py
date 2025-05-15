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

current_language_code = config_maker.read_global_config().language

no_language = False



def get_language(language_name_short):
    try:
        return(json.loads(open(f'languages/{language_name_short}.json', "r", encoding="utf-8").read()))
    except Exception as e:
        print(f'Could not read languages/{language_name_short}.json\nException: {e}')
        return(None)

current_language = get_language(current_language_code)
if current_language is None:
    no_language = True

def tr(key, language_code = None):
    buffer = key
    if no_language == False:
        try:
            if language_code is None:
                buffer = current_language[key]
            else:
                buffer = get_language(language_name_short = language_code)[key]
        except:
            print(f'Translation key \"{key}\" in language \"{language_code}\" does not exist. Returning key name.')
    else:
        print(f'Language \"{language_code}\" does not exist. Returning key name \"{key}\"')
    return(buffer)


language_list = {}

for language_code in [os.path.splitext(file)[0] for file in os.listdir("languages/") if os.path.splitext(file)[1] == '.json']:
    language_list[language_code] = tr("language_name_long", language_code = language_code)