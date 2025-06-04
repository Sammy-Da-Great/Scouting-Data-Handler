'''
Coalition DataBeam, a custom SQL interface
Copyright (C) 2025  Samuel Husmann

You should have received a copy of the GNU General Public License
along with this program. If not, see https://www.gnu.org/licenses/.
'''

from ModifyData.ModifyPresetPreset import *

data_type = "smallint unsigned"
constants = []

def funct(a, b):
    if a is None and b is None:
        return(None)
    else:
        if a is None:
            a = 0
        if b is None:
            b = 0
        return (int(a) + int(b))