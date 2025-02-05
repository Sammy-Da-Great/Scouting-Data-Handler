'''
Scouting Data Handler, a custom SQL interface
Copyright (C) 2025  Samuel Husmann

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see https://www.gnu.org/licenses/.
'''




import sys
from config_maker import read_global_config as config
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
import database
import os
import ModifyData.ModifyPresetHandler as mph

class Window(QMainWindow):
    """Main Window."""
    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle("Scouting Data Handler")
        self.resize(1000, 500)
        self.showMaximized()

        self.tabs = Tabs(self)
        self.setCentralWidget(self.tabs)


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

    def createDataTab(self, name, db_address, filepath, dictionary = tablist): #QWidget[]
        database_name = db_address[0]
        table_name = db_address[1]
        data = database.read_table(db_address)
        self.createDataTabFromList(name, data, filepath, db_address, dictionary)

        '''tab = self.add(name, tab_type = "DataTab")
        dictionary[name][3] = [db_address]
        label = QLabel(filepath)

        data = database.read_table(db_address)

        dimensions = list(database.get_dimensions(db_address))
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
                table.setItem(y,x,QTableWidgetItem(str(data[y][x])))'''

    def createDataTabFromList(self, name, data, filepath, db_address, dictionary=tablist): #QWidget[]
        database_name = db_address[0]
        table_name = db_address[1]
        tab = self.add(name, tab_type = "DataTab")
        dictionary[name][3] = [db_address]
        layoutGrid = QGridLayout()

        tab.setAutoFillBackground(True)
        content = DataTab(self, data, filepath, tab)
        layoutGrid.addWidget(content)

        '''label = QLabel(filepath)

        dimensions = (len(data) - 1, len(data[0]))

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

        for y in range(0, dimensions[0]):
            for x in range(0, dimensions[1]):
                table.setItem(y,x,QTableWidgetItem(str(data[y][x])))'''

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

    def createConcatTab(self):
        if self.test("Merge Data"): #Multiple tabs with the name name cannot exist
            self.delete("Merge Data")

        name = self.tab_bar.tabText(self.tab_bar.currentIndex())
        tab_type = self.tablist[name][2]
        if tab_type == "DataTab":

            tab = self.add("Merge Data", tab_type = "ConcatTab")
            layoutGrid = QGridLayout()
            tab.setLayout(layoutGrid)
            tab.setAutoFillBackground(True)

            content = ConcatWizard(self)
            layoutGrid.addWidget(content)

    def modifyTab(self):
        if self.test("Modify Data"): #Multiple tabs with the name name cannot exist
            self.delete("Modify Data")
        name = self.tab_bar.tabText(self.tab_bar.currentIndex())
        tab_type = self.tablist[name][2]

        if tab_type == "DataTab":
            data = self.currentTabData(keys=True)

            content = ModifyWizard(self, data[1], data[2], self.getCurrentTab(), name)

            tab = self.add("Modify Data", tab_type = "ModifyTab")
            layoutGrid = QGridLayout()
            tab.setLayout(layoutGrid)
            tab.setAutoFillBackground(True)

            layoutGrid.addWidget(content)

    def createLicenseTab(self):
        if self.test("License"): #Multiple tabs with the name name cannot exist
            self.delete("License")
        

        content = ScrollLabel()
        text = database.get_license()
        content.setText(text)

        tab = self.add("License", tab_type = "License")
        layoutGrid = QGridLayout()
        tab.setLayout(layoutGrid)
        tab.setAutoFillBackground(True)

        layoutGrid.addWidget(content)

    def getCurrentTab(self, parent = None):
        if parent == None: #If parent is not specified, set parent to default tab_bar
            parent = self.tab_bar
        tab = parent.widget(parent.currentIndex())
        return tab

    def saveCurrentTabAsCSV(self, parent = None):
        if parent == None: #If parent is not specified, set parent to default tab_bar
            parent = self.tab_bar
        file = SaveFile.data_save(self, name = parent.tabText(parent.currentIndex()) + ".csv")
        if file != "":
            database.write_csv(file, self.currentTabData(parent=parent, keys=True)[1])
    
    def saveCurrentTabSQL(self, parent = None):
        if parent == None: #If parent is not specified, set parent to default tab_bar
            parent = self.tab_bar

        tabData = self.currentTabData(parent, keys=False)
        keys = self.currentTabData(parent, keys=True)[1][0]
        data = tabData[1]
        db_address = tabData[2]

        if tabData[2] == (None, None):
            self.saveCurrentTabAsSQL(parent=parent)
        else:
            self.saveTabDataSQL(data, db_address, keys)

    def saveCurrentTabAsSQL(self, parent = None):
        tabData = self.currentTabData(parent)
        
        if tabData != None:
            dialog = SaveSQLAsDialog(parent, tabData[2])
            if dialog.exec() == 1:
                keys = self.currentTabData(parent, keys=True)[1][0]
                data = tabData[1]
                db_address = (dialog.databaseInput.text(), dialog.tableInput.text())

                self.saveTabDataSQL(data, db_address, keys)

    def saveTabDataSQL(self, data, db_address, keys):
        if (db_address != (None, None)) and (data != None) and (keys != None):
            database.write_to_database(data, db_address, keys)

            self.parent.menubar.updateMenuBar()


    def currentTabData(self, parent = None, keys = False, dictionary=tablist): #[filepath, data, db_address, columns]
        if parent == None: #If parent is not specified, set parent to default tab_bar
            parent = self.tab_bar
        index = parent.currentIndex()
        name = parent.tabText(index)
        return(self.tabData(name, parent, keys, dictionary))

    def tabData(self, name, parent = None, keys = False, dictionary=tablist):
        if parent == None: #If parent is not specified, set parent to default tab_bar
            parent = self.tab_bar
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

            if keys:
                key_list = []
                for c in range(table.columnCount()):
                    header_item = table.horizontalHeaderItem(c).text()
                    if header_item == None:
                        header_item = str(c+1)
                    
                    key_list.append(header_item)
                #print(data)
                #print(key_list)
                data.insert(0, key_list)
            
            filepath = tab.findChildren(QLabel)[0].text()
            return((filepath, data, dictionary[name][3][0], columns))
        else:
            print(f"Tab {name} is not a data tab, it is a {tab_type}")

class MenuBar(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self._createMenuBar()
        self.tabs = parent.tabs

    def set_open_table(self, button, target_database):
        button.triggered.connect(lambda: self.open_table(button.text(), (target_database, button.text()), button.parent().parent().title() + "/" + button.parent().title() + "/", button.parent().parent().title()))

    def open_table(self, file_name, db_address, category, action):
        database_name = db_address[0]
        table_name = db_address[1]
        if not os.path.isdir("tmp/" + category):
            os.makedirs("tmp/" + category)
        if action == "Data Export":
            file = SaveFile.file_save(self, file_name + ".csv")
            if file != "":
                database.download_csv_from_database(file, db_address)
        elif action == "View":
            filepath = database.get_csv_from_database(category + file_name + ".csv", db_address)
            self.tabs.createDataTab(file_name, db_address, filepath)
        
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
        menuBar.clear()

        #File
        file_dropdown = self.create_toolbar_dropdown("File", menuBar)

        self.saveActionSQL = self.create_toolbar_button("Save Current Tab to SQL", file_dropdown, lambda: self.tabs.saveCurrentTabSQL())
        self.saveActionSQLAs = self.create_toolbar_button("Save Current Tab as...", file_dropdown, lambda: self.tabs.saveCurrentTabAsSQL())
        self.saveActionCSV = self.create_toolbar_button("Save Current Tab as .csv as...", file_dropdown, lambda: self.tabs.saveCurrentTabAsCSV())
        self.exitAction = self.create_toolbar_button("Exit", file_dropdown, self.close)
        
        #
        editDropdown = self.create_toolbar_dropdown("Edit", menuBar)
        self.create_toolbar_button("Merge Tabs", editDropdown, lambda: self.tabs.createConcatTab())
        self.create_toolbar_button("Modify Keys", editDropdown, lambda: self.tabs.modifyTab())
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

        helpDropdown = self.create_toolbar_dropdown("Help", menuBar)
        self.create_toolbar_button("License", helpDropdown, lambda: self.tabs.createLicenseTab())
        #

    def updateMenuBar(self):
        self._createMenuBar()

class SaveFile(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__()
        self.setGeometry(50, 50, 500, 300)
        self.setWindowTitle("Export File")

    def file_save(self, name):
        filename = QFileDialog.getSaveFileName(self, "Save File", name, "Comma Separated (*.csv)")[0]
        return filename

    def file_dialog(self, name = "", extension = "Comma Separated (*.csv)"): # Returns a filepath
        return QFileDialog.getOpenFileName(self, "Open File", name, extension)[0]

    def data_save(self, name = "", extension = "Comma Separated (*.csv)"): # Saves to a chosen .csv
        return QFileDialog.getSaveFileName(self, "Save File", name, extension)[0]

class DataTab(QWidget):
    def __init__(self, parent, data, filepath, tab):
        super(QWidget, self).__init__(parent)
        label = QLabel(filepath)

        dimensions = (len(data) - 1, len(data[0]))

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

        for y in range(0, dimensions[0]):
            for x in range(0, dimensions[1]):
                table.setItem(y,x,QTableWidgetItem(str(data[y][x])))
    
class SaveSQLAsDialog(QDialog):
    def __init__(self, parent=None, db_address=(None, None)):
        super().__init__(parent)
        currentDatabase = db_address[0]
        currentTable = db_address[1]
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

        self.parent = parent

        label = QLabel(filepath)
        self.filepath = filepath
        self.layoutGrid.addWidget(label, 0, 0, alignment=Qt.AlignCenter)

        #####
        if (filepath == '' or not(database.test(filepath))):
            self.deleteSelf()
        else:
            self.data = database.read_csv(filepath)
            key_number = len(self.data[0])

            #table
            self.table = QTableWidget(4, key_number)
            self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.table.setVerticalHeaderLabels(["Key", "Type", "Datapoint 3", "Datapoint 4"])
            self.layoutGrid.addWidget(self.table, 1, 1)

            #Checkboxes
            self.sidebar = QVBoxLayout()
            self.tab_name = QLineEdit("test")
            self.format_label = QLabel("Format:")
            self.key_check = QCheckBox('Keys')
            self.type_check = QCheckBox('Types')
            self.key_check.setChecked(True)
            self.type_check.setChecked(True)
            self.key_check.stateChanged.connect(self.updateTable)
            self.type_check.stateChanged.connect(self.updateTable)
            self.sidebar.addWidget(self.tab_name)
            self.sidebar.addWidget(self.format_label)
            self.sidebar.addWidget(self.key_check)
            self.sidebar.addWidget(self.type_check)

            self.tab_name.textChanged[str].connect(self.updateConfirm)
            self.confirm_step_1 = QPushButton("Confirm")
            self.confirm_step_1.clicked.connect(self.confirm)
            self.sidebar.addWidget(self.confirm_step_1)

            self.layoutGrid.addLayout(self.sidebar, 1, 0)

            self.setTable()
            self.updateConfirm()
    
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
        
    def confirm(self):
        print("Step 1 complete, loading step 2")
        keys = []
        types = []
        for x in range(0, len(self.data[0])):
            keys.append(self.table.item(0, x).text())
            types.append(self.table.item(1, x).text())
        
        data_buffer = self.data
        if self.key_check.isChecked():
            data_buffer.pop(0)
        if self.type_check.isChecked():
            data_buffer.pop(0)
        
        print(self.data)
        print("Short Data:")
        print(data_buffer)

        self.parent.createDataTabFromList(self.tab_name.text(), [keys, types, *data_buffer], self.filepath, (None, None))
        self.deleteSelf()

    def deleteSelf(self):
        self.parent.delete("Import Data")

    def updateConfirm(self):
        banned_names = [""]

        if (self.parent.test(self.tab_name.text()) or self.tab_name.text() in banned_names):
            self.confirm_step_1.setEnabled(False)
        else:
            self.confirm_step_1.setEnabled(True)

    def clearSidebar(self):
        layout = self.sidebar
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def setItemToggle(self, item, toggle):
        defaultFlags = QTableWidgetItem().flags()
        if toggle:
            item.setFlags(defaultFlags & Qt.ItemIsSelectable)
        else:
            item.setFlags(defaultFlags)

class ModifyWizard(QWidget):
    def __init__(self, parent, data, db_address, tab, name):
        super(QWidget, self).__init__(parent)

        self.layoutGrid = QGridLayout(self)
        self.setLayout(self.layoutGrid)
        self.setAutoFillBackground(True)

        self.parent = parent

        self.data = data
        
        self.sidebar = QWidget()
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        
        self.addItemButton = QPushButton("+")
        self.removeItemButton = QPushButton("-")
        self.addItemButton.clicked.connect(lambda: self.addItem())
        self.removeItemButton.clicked.connect(lambda: self.removeItem())

        self.nameInput = QLineEdit()

        self.openPresetsButton = QPushButton("Open Presets Folder")
        self.openPresetsButton.clicked.connect(lambda: mph.openFolder())
        self.confirmButton = QPushButton("Confirm")
        self.confirmButton.clicked.connect(lambda: self.saveData(self.nameInput.text(), mph.runConversion(self.getConversion(), self.data)))

        self.saveConversionButton = QPushButton("Save Conversion")
        self.saveConversionButton.clicked.connect(lambda: self.saveConversion())

        self.loadConversionButton = QPushButton("Load Conversion")
        self.loadConversionButton.clicked.connect(lambda: self.loadConversion())
        

        self.layoutGrid.addWidget(self.pairItems([self.addItemButton, self.removeItemButton]), 0, 0)
        self.layoutGrid.addWidget(self.pairItems([QLabel("Name:"), self.nameInput]), 1, 0)

        self.layoutGrid.addWidget(self.sidebar, 2, 0)

        self.layoutGrid.addWidget(self.pairItems([self.openPresetsButton, self.saveConversionButton, self.loadConversionButton, self.confirmButton]), 3, 0)

    def saveData(self, name, data):
        self.parent.createDataTabFromList(name, data, None, (None, None))
        self.parent.delete("Modify Data")


    def loadConversion(self):
        name = SaveFile.file_dialog(self, "ModifyData\\ConversionPresets\\")
        if name != "":
            data = mph.readConversion(name)
            if self.data[0] == data[0]:
                #Load Conversion
                widgets = (self.sidebar_layout.itemAt(i).widget() for i in range(self.sidebar_layout.count())) 
                for widget in widgets:
                    self.deleteWidget(widget)

                rows = [data[i + 1] for i in range(len(data) - 1)]
                for row in rows:
                    keys = [row[i + 3] for i in range(len(row) - 3)]
                    print(type(keys))
                    self.addItem(key = row[0], custom = row[1], preset = row[2], keylist = keys)
            else:
                #Return exception
                print("Exception")

    def saveConversion(self):
        name = SaveFile.file_save(self, "ModifyData\\ConversionPresets\\")
        if name != "":
            presets = self.getConversion()
            mph.saveConversion(presets, name)

    def getConversion(self):
        key_list = self.data[0]
        presets = [key_list]
        widgets = (self.sidebar_layout.itemAt(i).widget().layout() for i in range(self.sidebar_layout.count())) 
        for widget in widgets:
            key = widget.itemAt(0).widget().text()
            preset_group = widget.itemAt(1).widget().custom_dropdown.currentText()
            preset_name = widget.itemAt(1).widget().selector_dropdown.currentText()
            parameters = widget.itemAt(1).widget().getKeys()
            presets.append([key, preset_group, preset_name, *parameters])
        
        return(presets)


    def addItem(self, key = "", custom = None, preset = None, keylist = None):
        buffer = self.pairItems([QLineEdit(key), PresetSelector(self, custom = custom, preset = preset, keylist = keylist)])
        self.sidebar_layout.addWidget(buffer)
    
    def removeItem(self):
        widget = self.sidebar_layout.itemAt(self.sidebar_layout.count() - 1).widget()
        if widget != None:
            self.deleteWidget(widget)

    def deleteWidget(self, widget):
        import sip
        widget.layout().parent().layout().removeWidget(widget)
        sip.delete(widget)
        self.widget = None

    def pairItems(self, items):
        pair = QWidget()
        pair_layout = QHBoxLayout(pair)
        for item in items:
            pair_layout.addWidget(item)
        return(pair)

    def fetchPresets(self, custom = False):
        if custom:
            filenames = next(os.walk("ModifyData/ModifyPresets/"), (None, None, []))[2]
        else:
            filenames = next(os.walk("ModifyData/DefaultModifyPresets/"), (None, None, []))[2]
        return filenames

    def dropdownMenu(self, data):
        dropdown = QComboBox()
        dropdown.addItems(data)
        return(dropdown)

    def preset(self, keys):
        presets = QWidget()
        presets_layout = QHBoxLayout()
        presets.setLayout()

class PresetSelector(QWidget):
    def __init__(self, parent, custom = None, preset = None, keylist = None):
        super(QWidget, self).__init__()
        self.parent = parent
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)




        self.custom_dropdown = self.parent.dropdownMenu(["Default", "Custom"])
        if custom != None:
            self.custom_dropdown.setCurrentText(custom)
        self.custom_dropdown.currentTextChanged.connect(lambda: self.updateSelector())

        self.selector_dropdown = self.parent.dropdownMenu(["None"])
        if preset != None:
            self.selector_dropdown.setCurrentText(preset)
        self.selector_dropdown.currentTextChanged.connect(lambda: self.updateKeys())

        self.keys = QWidget()
        self.keys_layout = QHBoxLayout()
        self.keys.setLayout(self.keys_layout)


        self.layout.addWidget(self.custom_dropdown)
        self.layout.addWidget(self.selector_dropdown)
        self.layout.addWidget(self.keys)

        self.updateSelector(values=keylist)

    def getKeys(self):
        keys = []
        dropdowns = (self.keys_layout.itemAt(i).widget().layout().itemAt(1).widget() for i in range(self.keys_layout.count()))
        for drop in dropdowns:
            keys.append(drop.currentText())
        return(keys)


    def manualUpdateSelector(self):
        self.selector_dropdown.clear()
        self.selector_dropdown.addItems(self.parent.fetchPresets(custom = (self.custom_dropdown.currentText() == "Custom")))

    def updateSelector(self, values = None):
        self.manualUpdateSelector()
        self.updateKeys(values = values)

    def updateKeys(self, delete = True, values = None):
        if self.selector_dropdown.currentText() != "":
            #print(f"filename: {self.selector_dropdown.currentText()}")
            keys_list = mph.getParams(self.selector_dropdown.currentText(), custom = (self.custom_dropdown.currentText() == "Custom"))

            if delete == True:
                for i in reversed(range(self.keys_layout.count())): 
                    self.keys_layout.itemAt(i).widget().deleteLater()


            
            if values == None:
                values = []
                for key in keys_list:
                    values.append(None)

            for key, value in zip(keys_list, values):
                label = QLabel(f"{key}:")
                dropdown = self.parent.dropdownMenu(self.parent.data[0])
                if value != None:
                    dropdown.setCurrentText(value)
                group = self.parent.pairItems([label, dropdown])
                self.keys_layout.addWidget(group)

class ConcatWizard(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        self.layoutGrid = QGridLayout(self)
        self.setLayout(self.layoutGrid)
        self.setAutoFillBackground(True)

        self.parent = parent


        #
        self.sidebar = QVBoxLayout()
        self.tab_name = QLineEdit("test")
        self.format_selector = QWidget()
        self.format_selector_layout = QHBoxLayout()
        self.format_selector.setLayout(self.format_selector_layout)
        self.format_label = QLabel("Format:")

        self.format = self.dropdownMenu(self.dataTabs())
        self.sidebar.addWidget(self.tab_name)
        self.sidebar.addWidget(self.format_selector)
        self.format_selector_layout.addWidget(self.format_label)
        self.format_selector_layout.addWidget(self.format)

        self.possible_items = QListDragAndDrop()
        self.possible_items.setFlow(QListView.TopToBottom)
        self.possible_items.setWrapping(False)
        self.possible_items.setResizeMode(QListView.Adjust)
        self.layoutGrid.addWidget(self.possible_items, 1, 1)

        self.chosen_items = QListDragAndDrop()
        self.chosen_items.setFlow(QListView.TopToBottom)
        self.chosen_items.setWrapping(False)
        self.chosen_items.setResizeMode(QListView.Adjust)
        self.layoutGrid.addWidget(self.chosen_items, 1, 2)

        self.format.currentTextChanged.connect(lambda: self.updateList())
        

        #self.tab_name.textChanged[str].connect(self.updateConfirm)
        self.confirm_step_1 = QPushButton("Confirm")
        self.confirm_step_1.clicked.connect(lambda: self.confirm())
        #self.confirm_step_1.clicked.connect(self.confirm)
        self.sidebar.addWidget(self.confirm_step_1)

        self.layoutGrid.addLayout(self.sidebar, 1, 0)

    def confirm(self):
        formatList = self.parent.tabData(self.format.currentText(), keys=True)[1][0:1]

        data = formatList
        for tab_index in range(self.chosen_items.count()):
            tab_name = self.chosen_items.item(tab_index).text()
            tab_data = self.parent.tabData(tab_name, keys=False)[1][1:]
            data.extend(tab_data)

        self.parent.createDataTabFromList(self.tab_name.text(), data, "", (None, None))



    def updateList(self):
        self.possible_items.clear()
        self.chosen_items.clear()
        self.possible_items.addItems(self.dataTabs(self.format.currentText()))

    def dropdownMenu(self, data):
        dropdown = QComboBox()
        dropdown.addItems(data)
        return(dropdown)

    def dataTabs(self, formatTab = None):
        tabs = [*self.parent.tablist]
        tabs = list(filter((lambda tabname: self.parent.tablist[tabname][2] == "DataTab"), tabs))
        print(tabs)
        if formatTab != None:
            tabs = list(map(lambda tabname: (tabname, self.data(tabname)[0]), tabs))
            print(tabs)
            tabs = list(filter((lambda tab: tab[1] == self.data(formatTab)[0]), tabs))
            tabs = [tab[0] for tab in tabs]
        return(tabs)

    def data(self, name):
        return(self.parent.tabData(name, keys=True)[1])

class ScrollLabel(QScrollArea):

    # constructor
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)

        # making widget resizable
        self.setWidgetResizable(True)

        # making qwidget object
        content = QWidget(self)
        self.setWidget(content)

        # vertical box layout
        lay = QVBoxLayout(content)

        # creating label
        self.label = QLabel(content)

        # setting alignment to the text
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # making label multi-line
        self.label.setWordWrap(True)

        # adding label to the layout
        lay.addWidget(self.label)

    # the setText method
    def setText(self, text):
        # setting text to the label
        self.label.setText(text)

class QListDragAndDrop(QListWidget):
   def __init__(self):
       super(QListDragAndDrop, self).__init__()
       self.setFrameShape(QFrame.WinPanel)
       self.setFrameShadow(QFrame.Raised)
       self.setDragEnabled(True)
       self.setDragDropMode(QAbstractItemView.DragDrop)
       self.setDefaultDropAction(Qt.MoveAction)
       self.setSelectionMode(QAbstractItemView.MultiSelection)
       self.setMovement(QListView.Snap)
       self.setProperty("isWrapping", True)
       self.setWordWrap(True)
       self.setSortingEnabled(True)
       self.setAcceptDrops(True)

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