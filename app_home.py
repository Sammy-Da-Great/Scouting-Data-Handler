import sys
from config_maker import read_global_config as config
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QMenuBar, QMenu, QAction, QTabWidget, QWidget, QVBoxLayout, QPushButton, QFileDialog
import database
import os

class Window(QMainWindow):
    """Main Window."""
    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle("Python Menus & Toolbars")
        self.resize(1000, 500)

        self.tabs = Tabs(self)
        self.setCentralWidget(self.tabs)
        self.tabs.add("test")

        self.menubar = MenuBar(self)

class Tabs(QWidget):
    
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.tab_bar = self._createTabBar()

    tablist = dict()

    def _createTabBar(self):
        # Initialize tab screen
        tabs = QTabWidget()
        tabs.resize(300,200)

        self.layout.addWidget(tabs)
        self.setLayout(self.layout)
        return(tabs)

    def add(self, name = "Default Tab Name", content = None, dictionary = tablist, parent = None):
        if parent == None:
            parent = self.tab_bar
        if self.test(name, dictionary, parent):
            buffer = parent[name]
        else:
            buffer = QWidget()
            parent.addTab(buffer, name)
        
        buffer.layout = QVBoxLayout()
        if content != None:
            buffer.layout.addWidget(content)

        dictionary[name] = (buffer, parent.indexOf(buffer))

        return(buffer)

    def delete(self, name, dictionary = tablist, parent = None):
        if parent == None:
            parent = self.tab_bar
        if self.test(name, dictionary, parent):
            parent.removeTab(dictionary[name][1])
            del dictionary[name]
        else:
            print("Key " + name + "doesn't exist")

    def test(self, name, dictionary = tablist, parent = None):
        if parent == None:
            parent = self.tab_bar
        return(name in dictionary.keys())
    
    def get(self, name, dictionary = tablist):
        return(dictionary[name][0])

class MenuBar(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self._createMenuBar()
        self.tabs = parent.tabs

    def set_open_table(self, button, target_database):
        button.triggered.connect(lambda: self.open_table(button.text() + ".csv", target_database, button.text(), button.parent().parent().title() + "/" + button.parent().title() + "/", button.parent().parent().title() == "Data Export"))

    def open_table(self, file_name, database_name, table_name, category, export):
        if not os.path.isdir("tmp/" + category):
            os.makedirs("tmp/" + category)
        if export:
            SaveFile.file_save(self, file_name, database_name, table_name)
        else:
            database.get_csv_from_database(category + file_name, database_name, table_name)

    def create_toolbar_dropdown(self, name, parent):
        buffer = QMenu(name, self)
        parent.addMenu(buffer)
        return buffer

    def create_toolbar_button(self, name, parent, action = None):
        buffer = QAction(name, parent)
        parent.addAction(buffer)
        if action != None:
            buffer.triggered.connect(action)
        return buffer
    
    def database_buttons(self, names, parent, action = None):
        list_buffer = []
        for name in names:
            buffer = QAction(name, self)
            parent.addAction(buffer)
            if not(action == None):
                buffer.triggered.connect(action)
            list_buffer.append(buffer)
        return list_buffer

    def table_buttons(self, target_database, parent, action = None):
        list_buffer = []
        names = []
        
        names = database.get_all_tables(target_database)
        if not names:
            return(list())
    
        for name in names:
            buffer = self.create_toolbar_button(name, parent)
            list_buffer.append(buffer)

        list_buffer = list(map(lambda mylambda: self.set_open_table(mylambda, target_database), list_buffer))

        return list_buffer

    def database_dropdowns(self, names, parent, action = None):
        self.list_buffer = []
        for name in names:
            buffer = QMenu(name, parent)
            parent.addMenu(buffer)
            self.list_buffer.append(buffer)
            self.table_buttons(name, buffer, action)
        return self.list_buffer

    def _createMenuBar(self):
        menuBar = self.parent.menuBar()

        #File
        file_dropdown = self.create_toolbar_dropdown("File", menuBar)

        file_dropdown.addSeparator()
        self.exitAction = self.create_toolbar_button("Exit", file_dropdown, self.close)
        #
        homeAction = self.create_toolbar_button("Home", menuBar)
        #Database
        database_names = database.get_all_databases()

        database_dropdown = self.create_toolbar_dropdown("Database", menuBar)

        view_dropdown = self.create_toolbar_dropdown("View", database_dropdown)
        self.database_dropdowns(database_names, view_dropdown)
        #
        export_dropdown = self.create_toolbar_dropdown("Data Export", database_dropdown)
        self.database_dropdowns(database_names, export_dropdown)

        import_dropdown = self.create_toolbar_dropdown("Data Import", database_dropdown)
        self.database_buttons(database_names, import_dropdown)
        
        self.create_toolbar_button("Settings", database_dropdown)
        #

class SaveFile(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__()
        self.setGeometry(50, 50, 500, 300)
        self.setWindowTitle("Export File")

    def file_save(self, name, database_name, table_name):
        filename = QFileDialog.getSaveFileName(self, "Save File", table_name + ".csv", "Comma Separated (*.csv)")[0]
        database.download_csv_from_database(filename, database_name, table_name)



def start_app():
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    app.exec_()
    #APP CLOSED
    import cleanup
    cleanup.remove_temp_dir()
if __name__ == "__main__":
    import initialization
    start_app()