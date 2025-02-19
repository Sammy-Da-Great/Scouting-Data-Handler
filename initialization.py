'''
Scouting Data Handler, a custom SQL interface
Copyright (C) 2025  Samuel Husmann

You should have received a copy of the GNU General Public License
along with this program. If not, see https://www.gnu.org/licenses/.
'''

import config_maker
import create_sql_database
import app_home
import os
# First Script run in the program.

if not os.path.isdir("tmp"):
        os.makedirs("tmp")


config_maker.initialize_configs()
create_sql_database.create_database()

if __name__ == "__main__":
        app_home.start_app()