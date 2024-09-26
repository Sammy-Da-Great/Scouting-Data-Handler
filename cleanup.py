from pathlib import Path
import os
import glob
def remove_temp_dir():
    print("Exited Application")
    files = glob.glob('tmp/*')
    for f in files:
        os.remove(f)
    Path.rmdir('tmp/')