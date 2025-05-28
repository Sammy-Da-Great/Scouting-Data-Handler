'''
Scouting Data Handler, a custom SQL interface
Copyright (C) 2025  Samuel Husmann

You should have received a copy of the GNU General Public License
along with this program. If not, see https://www.gnu.org/licenses/.
'''

from ModifyData.ModifyPresetPreset import *

data_type = "varchar(45)"
constants = ["prefix", "suffix"]

def funct(prefix, column, suffix):
    if prefix is None:
        prefix = ""
    if suffix is None:
        suffix = ""
    if column is None:
        column = ""
    return (prefix + column + suffix)