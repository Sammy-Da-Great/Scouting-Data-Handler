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