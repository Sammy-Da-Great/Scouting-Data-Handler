'''
Coalition DataBeam, a custom SQL interface
Copyright (C) 2025  Samuel Husmann

You should have received a copy of the GNU General Public License
along with this program. If not, see https://www.gnu.org/licenses/.
'''

from ModifyData.ModifyPresetPreset import *

data_type = "varchar(45)"
constants = ["remove", "replace"]

def funct(string, remove, replace):
    if replace is None:
        replace = ""
    return(string.replace(remove, replace))