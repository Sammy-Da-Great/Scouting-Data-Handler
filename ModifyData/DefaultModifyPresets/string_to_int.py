'''
Coalition DataBeam, a custom SQL interface
Copyright (C) 2025  Samuel Husmann

You should have received a copy of the GNU General Public License
along with this program. If not, see https://www.gnu.org/licenses/.
'''

from ModifyData.ModifyPresetPreset import *

data_type = "smallint unsigned"
constants = []

def funct(string):
    buffer = ''.join(x for x in string if not(x.isdigit()))
    
    return(buffer)