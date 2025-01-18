'''
Scouting Data Handler, a custom SQL interface
Copyright (C) 2025  Samuel Husmann

You should have received a copy of the GNU General Public License
along with this program. If not, see https://www.gnu.org/licenses/.
'''

from pathlib import Path
import shutil
import os
import glob

def remove_dir(path):
    files = glob.glob(path + '*')
    for f in files:
        os.remove(f)
    Path.rmdir(path)

def remove_temp_dir():
    print("Exited Application")
    shutil.rmtree("tmp/")