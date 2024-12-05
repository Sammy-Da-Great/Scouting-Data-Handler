import sys
from config_maker import read_global_config as config
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QMenuBar, QMenu, QAction, QTabWidget, QWidget, QVBoxLayout, QPushButton, QFileDialog, QTableWidget, QHeaderView, QSizePolicy, QGridLayout, QTableWidgetItem, QHBoxLayout, QCheckBox, QLineEdit, QDialogButtonBox, QDialog
import database
import os

class Window(QMainWindow):
    """Main Window."""
    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle("Python Menus & Toolbars")
        self.resize(1000, 500)
        self.showMaximized()

        self.tabs = Tabs(self)
        self.setCentralWidget(self.tabs)

        test_tab = self.tabs.add("test")

        self.menubar = MenuBar(self)

        self.layout = QGridLayout()

class Tabs(QWidget):
    
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.tab_bar = self._createTabBar()
        self.parent = parent
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    tablist = dict() # tablist[tab_name] == (tab, index in tab bar, tab type, database info(database, table))

    def _createTabBar(self):
        # Initialize tab screen
        tabs = QTabWidget()
        tabs.resize(300,200)

        self.layout.addWidget(tabs)
        self.setLayout(self.layout)

        tabs.setTabsClosable(True)
        #tabs.tabCloseRequested.connect(self.deleteByIndex)
        tabs.tabCloseRequested.connect(lambda index: self.deleteByIndex(index))

        return(tabs)

    def add(self, name = "Default Tab Name", content = None, dictionary = tablist, parent = None, layout = QGridLayout(), tab_type = None):
        # Creates or modifies a tab.
        if parent == None: #If parent is not specified, set parent to default tab_bar
            parent = self.tab_bar

        if self.test(name, dictionary, parent): #if tab name already exists in this location, fetch the tab. Else, create a new tab at location.
            buffer = dictionary[name][0]
        else:
            buffer = QWidget()
            parent.addTab(buffer, name)
        buffer.layout = layout #Layout of new tab
        if content != None:
            buffer.layout.addWidget(content)

        if not(self.test(name, dictionary, parent)): #if the tab has not been added to dictionary, add it.
            dictionary[name] = [buffer, parent.indexOf(buffer), tab_type, None]

        buffer.layout.setContentsMargins(0,0,0,0)
        buffer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return(buffer)

    def delete(self, name, dictionary = tablist, parent = None):
        # Deletes a tab from the dictionary and tab bar
        if parent == None: # If no parent is specified, default to tab_bar
            parent = self.tab_bar

        if self.test(name, dictionary, parent):
            tab = dictionary[name][0]

            tab.deleteLater() # Deletes the tab
            parent.removeTab(parent.indexOf(tab)) # Removes the tab from the tab bar

            del dictionary[name] # Removes the tab from the dictionary
        else: # If tab doesn't exist, return exception
            print("Key " + name + "doesn't exist")
        
    def deleteByIndex(self, index, dictionary = tablist, parent = None):
        # Fetches the name of a tab from the index and runs self.delete()
        tab = self.tab_bar.widget(index)
        tab_name = self.tab_bar.tabText(index)

        self.delete(tab_name, parent = None)

    def test(self, name, dictionary = tablist, parent = None): # Boolean
        # Tests if a tab exists in tab_bar
        if parent == None:
            parent = self.tab_bar
        return(name in dictionary) # If name is in dictionary, return true. Else, return false.

    def createDataTab(self, name, database_name, table_name, filepath, dictionary = tablist): #QWidget[]
        tab = self.add(name, tab_type = "DataTab")
        dictionary[name][3] = (database_name, table_name)
        label = QLabel(filepath)

        data = database.read_table(database_name, table_name)

        dimensions = list(database.get_dimensions(database_name, table_name))
        dimensions[0] += 1

        table = QTableWidget(*dimensions, tab)
        table.setHorizontalHeaderLabels(data[0])
        data.pop(0)

        header_v_text = [str(row[0]) for row in data]
        header_v_text[0] = "data type"
        table.setVerticalHeaderLabels(header_v_text)

        layoutGrid = QGridLayout()
        tab.setLayout(layoutGrid)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layoutGrid.addWidget(label)
        layoutGrid.addWidget(table)
        tab.setAutoFillBackground(True)

        for y in range(0,dimensions[0]):
            for x in range(0, dimensions[1]):
                table.setItem(y,x,QTableWidgetItem(str(data[y][x])))

    def createImportTab(self):
        if self.test("Import Data"): #Multiple tabs with the name name cannot exist
            self.delete("Import Data")

        filepath = SaveFile.file_dialog(self)
        if filepath != None:

            tab = self.add("Import Data", tab_type = "ImportTab")
            layoutGrid = QGridLayout()
            tab.setLayout(layoutGrid)
            tab.setAutoFillBackground(True)

            content = ImportWizard(self, filepath)
            layoutGrid.addWidget(content)


    def getCurrentTab(self, parent = None):
        if parent == None: #If parent is not specified, set parent to default tab_bar
            parent = self.tab_bar
        tab = parent.widget(parent.currentIndex())
        return tab

    def saveCurrentTabAsCSV(self, parent = None):
        if parent == None: #If parent is not specified, set parent to default tab_bar
            parent = self.tab_bar
        database.write_csv(SaveFile.data_save(self, name = parent.tabText(parent.currentIndex()) + ".csv"), self.currentTabData(parent=parent)[1])
    
    def saveCurrentTabSQL(self, parent = None):
        tabData = self.currentTabData(parent)
        if tabData != None:
            database.write_to_database(tabData[1], tabData[2], tabData[3], tabData[4])

    def saveCurrentTabAsSQL(self, parent = None):
        tabData = self.currentTabData(parent)
        if tabData != None:
            dialog = SaveSQLAsDialog(parent, tabData[2], tabData[3])
            if dialog.exec() == 1:
                database.write_to_database(tabData[1], dialog.databaseInput.text(), dialog.tableInput.text(), tabData[4])

    def currentTabData(self, parent = None, dictionary = tablist):
        if parent == None: #If parent is not specified, set parent to default tab_bar
            parent = self.tab_bar
        index = parent.currentIndex()
        name = parent.tabText(index)
        tab_type = self.tablist[name][2]
        tab = self.tablist[name][0]

        if (tab_type == "DataTab"):
            table = tab.findChildren(QTableWidget)[0]
            data = []
            columns = []

            for column in range(table.columnCount()):
                columns.append(table.horizontalHeaderItem(column).text())

            for row in range(table.rowCount()):
                row_data = []
                for column in range(table.columnCount()):
                    item = table.item(row, column)
                    if item is not None:
                        row_data.append(str(item.text()))
                    else:
                        row_data.append('')
                data.append(row_data)
            
            filepath = tab.findChildren(QLabel)[0].text()
            return((filepath, data, dictionary[name][3][0], dictionary[name][3][1], columns))


        else:
            print(f"Tab {name} is not a data tab")




class MenuBar(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self._createMenuBar()
        self.tabs = parent.tabs

    def set_open_table(self, button, target_database):
        button.triggered.connect(lambda: self.open_table(button.text(), target_database, button.text(), button.parent().parent().title() + "/" + button.parent().title() + "/", button.parent().parent().title()))

    def open_table(self, file_name, database_name, table_name, category, action):
        if not os.path.isdir("tmp/" + category):
            os.makedirs("tmp/" + category)
        if action == "Data Export":
            database.download_csv_from_database(SaveFile.file_save(self, file_name + ".csv"), database_name, table_name)
        elif action == "View":
            filepath = database.get_csv_from_database(category + file_name + ".csv", database_name, table_name)
            self.tabs.createDataTab(file_name, database_name, table_name, filepath)
        
        print(category + file_name + ".csv")

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

        self.saveActionSQL = self.create_toolbar_button("Save Current Tab to SQL", file_dropdown, lambda: self.tabs.saveCurrentTabSQL())
        self.saveActionSQLAs = self.create_toolbar_button("Save Current Tab as...", file_dropdown, lambda: self.tabs.saveCurrentTabAsSQL())
        self.saveActionCSV = self.create_toolbar_button("Save Current Tab as .csv as...", file_dropdown, lambda: self.tabs.saveCurrentTabAsCSV())
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

        import_button = self.create_toolbar_button("Data Import", database_dropdown, lambda: self.tabs.createImportTab())
        
        self.create_toolbar_button("Settings", database_dropdown)
        #

class SaveFile(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__()
        self.setGeometry(50, 50, 500, 300)
        self.setWindowTitle("Export File")

    def file_save(self, name): # Should save to SQL
        filename = QFileDialog.getSaveFileName(self, "Save File", name, "Comma Separated (*.csv)")[0]
        return filename

    def file_dialog(self, name = "", extension = "Comma Separated (*.csv)"): # Returns a filepath
        return QFileDialog.getOpenFileName(self, "Open File", name, extension)[0]

    def data_save(self, name = "", extension = "Comma Separated (*.csv)"): # Saves to a chosen .csv
        return QFileDialog.getSaveFileName(self, "Save File", name, extension)[0]
    
class SaveSQLAsDialog(QDialog):
    def __init__(self, parent=None, currentDatabase="", currentTable=""):
        super().__init__(parent)
        self.setWindowTitle("Save Current Tab as...")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.databaseLabel = QLabel("Database")
        self.layout.addWidget(self.databaseLabel)
        self.databaseInput = QLineEdit()
        self.databaseInput.setText(currentDatabase)
        self.layout.addWidget(self.databaseInput)
        self.tableLabel = QLabel("Table")
        self.layout.addWidget(self.tableLabel)
        self.tableInput = QLineEdit()
        self.tableInput.setText(currentTable)
        self.layout.addWidget(self.tableInput)
        self.dialogButtons = QDialogButtonBox()
        self.dialogButtons.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.dialogButtons.accepted.connect(self.accept)
        self.dialogButtons.rejected.connect(self.reject)
        self.layout.addWidget(self.dialogButtons)
        self.show()

class ImportWizard(QWidget):
    def __init__(self, parent, filepath):
        super(QWidget, self).__init__(parent)

        self.layoutGrid = QGridLayout(self)
        self.setLayout(self.layoutGrid)
        self.setAutoFillBackground(True)

        label = QLabel(filepath)
        self.layoutGrid.addWidget(label, 0, 0, alignment=Qt.AlignCenter)

        #####
        self.data = database.read_csv(filepath)
        key_number = len(self.data[0])

        #table
        self.table = QTableWidget(4, key_number)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setVerticalHeaderLabels(["Key", "Type", "Datapoint 3", "Datapoint 4"])
        self.layoutGrid.addWidget(self.table, 1, 1)

        #Checkboxes
        self.sidebar = QVBoxLayout()
        self.format_label = QLabel("Format:")
        self.key_check = QCheckBox('Keys')
        self.type_check = QCheckBox('Types')
        self.key_check.setChecked(True)
        self.type_check.setChecked(True)
        self.key_check.stateChanged.connect(self.updateTable)
        self.type_check.stateChanged.connect(self.updateTable)
        self.sidebar.addWidget(self.format_label)
        self.sidebar.addWidget(self.key_check)
        self.sidebar.addWidget(self.type_check)

        self.confirm_step_1 = QPushButton("Confirm")
        self.confirm_step_1.clicked.connect(self.updateTable)
        self.sidebar.addWidget(self.confirm_step_1)

        self.layoutGrid.addLayout(self.sidebar, 1, 0)

        self.setTable()
    
    def setTable(self):
        for y in [0, 1]:
            for x in range(0, len(self.data[0])):
                item = QTableWidgetItem(f'{x}, {y}')
                self.setItemToggle(item, False)
                self.table.setItem(y, x, item)
        for y in [2, 3]:
            for x in range(0, len(self.data[0])):
                item = QTableWidgetItem(f'{x}, {y}')
                self.setItemToggle(item, True)
                self.table.setItem(y, x, item)
        self.updateTable()
                
    def updateTable(self):
        rowIndex = 0
        print("update")
        if self.key_check.isChecked() == True:
            for x in range(0, len(self.data[0])):
                self.table.item(0, x).setText(str(self.data[rowIndex][x]))
                self.setItemToggle(self.table.item(0, x), True)
            rowIndex = rowIndex + 1
        else:
            for x in range(0, len(self.data[0])):
                self.table.item(0, x).setText("")
                self.setItemToggle(self.table.item(0, x), False)

        if self.type_check.isChecked() == True:
            for x in range(0, len(self.data[0])):
                self.table.item(1, x).setText(str(self.data[rowIndex][x]))
                self.setItemToggle(self.table.item(1, x), True)
            rowIndex = rowIndex + 1
        else:
            for x in range(0, len(self.data[0])):
                self.table.item(1, x).setText("")
                self.setItemToggle(self.table.item(1, x), False)
        
        for x in range(0, len(self.data[0])):
            self.table.item(2, x).setText(str(self.data[rowIndex][x]))
            self.table.item(3, x).setText(str(self.data[rowIndex + 1][x]))
        
    def confirmStep1(self):
        print("Step 1 complete, loading step 2")
        self.clearSidebar()

        #for y in [0, 3]:
        #    for x in range(0, len(self.data[0])):
        #        self.table.item(y, x).setFlags(Qt.ItemIsEnabled)

    def clearSidebar(self):
        layout = self.sidebar
        while self.layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def setItemToggle(self, item, toggle):
        defaultFlags = QTableWidgetItem().flags()
        if toggle:
            item.setFlags(defaultFlags & Qt.ItemIsSelectable)
        else:
            item.setFlags(defaultFlags)

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