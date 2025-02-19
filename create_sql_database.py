'''
Scouting Data Handler, a custom SQL interface
Copyright (C) 2025  Samuel Husmann

You should have received a copy of the GNU General Public License
along with this program. If not, see https://www.gnu.org/licenses/.
'''

from database import *

def create_database(name = database_name):
    query("CREATE DATABASE IF NOT EXISTS " + name)