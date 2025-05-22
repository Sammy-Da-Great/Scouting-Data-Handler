'''
Scouting Data Handler, a custom SQL interface
Copyright (C) 2025  Samuel Husmann

You should have received a copy of the GNU General Public License
along with this program. If not, see https://www.gnu.org/licenses/.
'''

import os
abspath = os.path.abspath(__file__) # If the file is run from another directory, it will set the working directory to its own.
dname = os.path.dirname(abspath)
os.chdir(dname)
if not os.path.isdir("tmp"):
        os.makedirs("tmp")
        
if not os.path.isdir("Queries"):
        os.makedirs("Queries")


import config_maker
config_maker.initialize_configs()

import create_sql_database

create_sql_database.create_database()

import app_home

if __name__ == "__main__":
        app_home.start_app()