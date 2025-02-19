'''
Scouting Data Handler, a custom SQL interface
Copyright (C) 2025  Samuel Husmann

You should have received a copy of the GNU General Public License
along with this program. If not, see https://www.gnu.org/licenses/.
'''

data_type = "tinyint(1)"
constants = []

def funct(boolean):
    boolean_buffer = str(boolean)
    
    true_list = ["True", "true", "1"]
    false_list = ["False", "false", "0"]
    
    if boolean_buffer in true_list:
        boolean_buffer = "1"
    elif boolean_buffer in false_list:
        boolean_buffer = "0"
    return (boolean_buffer)