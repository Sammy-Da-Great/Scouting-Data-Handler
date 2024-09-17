import sys
import ctypes
import clr 


# https://stackoverflow.com/questions/49796024/python-tkinter-filedialog-askfolder-interfering-with-clr/50446803#50446803
# https://stackoverflow.com/questions/9319317/quick-and-easy-file-dialog-in-python

# https://github.com/pythonnet/pythonnet/blob/ea059ca0aeec4cdad490c1a68c783908dd879607/demo/wordpad.py#L6

# https://learn.microsoft.com/en-us/dotnet/api/system.windows.forms.filedialog?view=windowsdesktop-8.0

co_initialize = ctypes.windll.ole32.CoInitialize
#   Force STA mode
co_initialize(None)

clr.AddReference('System.Windows.Forms')

from System.Windows.Forms import OpenFileDialog

def open_file(title, extensions, folder = "c:\\"):
    file_dialog = OpenFileDialog()

    filter = []
    for i, v in enumerate(extensions):
        filter.append(extensions[i][0] + "|*" + extensions[i][1])
    filter = "|".join(filter)

    file_dialog.Filter = filter
    file_dialog.Title = title
    file_dialog.InitialDirectory = folder

    ret = file_dialog.ShowDialog()
    if ret != 1:
        if file_dialog.FileName:
            print(file_dialog.FileName)
        else:
            print("Cancelled")
    return(file_dialog.FileName)
    sys.exit()

# open_file("Open Doc", [("Text File", ".txt"), ("Rich Text File", ".rtf")])