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
import config_maker
from PyQt5.QtCore import Qt, QMimeData, QPoint, QEvent
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtGui import QDrag
import database
import os
import ModifyData.ModifyPresetHandler as mph
import tba_api
from datetime import datetime
import sip

from language_manager import tr

version = "2025.4.23"

class Window(QMainWindow):
    """Main Window."""
    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle(f'{tr("title")} {tr("version_short")}{version}')
        self.setWindowIcon(QtGui.QIcon('Images/logo.png'))
        self.resize(1000, 500)

        self.menus = MenuManager(self)
        self.tabs = self.menus.tabs #Tabs(self)
        self.settings = self.menus.settings #Settings(self)

        self.menubar = MenuBar(self)

        self.setCentralWidget(self.menus)

        self.layout = QGridLayout()

        self.showMaximized()

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

    def test(self, name, dictionary = tablist, parent = None, data_type = None): # Boolean
        # Tests if a tab exists in tab_bar
        if parent == None:
            parent = self.tab_bar

        if name in dictionary:
            if data_type != None:
                return(dictionary[name][2] == data_type)
            else:
                return(name in dictionary) # If name is in dictionary, return true. Else, return false.
        else:
            return(False)

    def createDataTab(self, name, db_address, filepath, dictionary = tablist): #QWidget[]
        database_name = db_address[0]
        table_name = db_address[1]
        data = database.read_table(db_address)
        self.createDataTabFromList(name, data, filepath, db_address, dictionary)

    def createDataTabFromList(self, name, data, filepath, db_address, dictionary=tablist): #QWidget[]
        database_name = db_address[0]
        table_name = db_address[1]
        tab = self.add(name, tab_type = "DataTab")
        dictionary[name][3] = [db_address]
        layoutGrid = QGridLayout()

        tab.setAutoFillBackground(True)
        content = DataTab(self, data, filepath, tab)
        layoutGrid.addWidget(content)

    def createConcatTab(self):
        if self.test("Merge Data"): #Multiple tabs with the name name cannot exist
            self.delete("Merge Data")

        name = self.tab_bar.tabText(self.tab_bar.currentIndex())
        if name != '':
            tab_type = self.tablist[name][2]
            if tab_type == "DataTab":

                tab = self.add("Merge Data", tab_type = "ConcatTab")
                layoutGrid = QGridLayout()
                tab.setLayout(layoutGrid)
                tab.setAutoFillBackground(True)

                content = ConcatWizard(self)
                layoutGrid.addWidget(content)

    def modifyTab(self):
        if self.test(tr("modify_keys")): #Multiple tabs with the name name cannot exist
            self.delete(tr("modify_keys"))
        name = self.tab_bar.tabText(self.tab_bar.currentIndex())
        if name != '':
            tab_type = self.tablist[name][2]

            if tab_type == "DataTab":
                data = self.currentTabData(keys=True)

                content = ModifyWizard(self, data[1], data[2], self.getCurrentTab(), name)

                tab = self.add(tr("modify_keys"), tab_type = "ModifyTab")
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

        index = parent.currentIndex()
        name = parent.tabText(index)

        if self.test(name, data_type = "DataTab"):
        

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

            self.parent.parent.menubar.updateMenuBar()

    def currentTabData(self, parent = None, keys = False, dictionary=tablist): #[filepath, data, db_address, columns]
        if parent == None: #If parent is not specified, set parent to default tab_bar
            parent = self.tab_bar
        index = parent.currentIndex()
        name = parent.tabText(index)
        if self.test(name, data_type = "DataTab"):
            return(self.tabData(name, parent, keys, dictionary))
        else:
            return(None)

    def currentTabType(self, parent = None, dictionary = tablist, data_type=None):
        if parent == None: #If parent is not specified, set parent to default tab_bar
            parent = self.tab_bar
        index = parent.currentIndex()
        name = parent.tabText(index)
        if self.test(name):
            if data_type != None:
                return(self.test(name, data_type = data_type))
            else:
                return(dictionary[name][2])
        else:
            return(False)

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
        if action == tr("export_data"):
            file = SaveFile.file_save(self, file_name + ".csv")
            if file != "":
                database.download_csv_from_database(file, db_address)
        elif action == tr("view"):
            filepath = database.get_csv_from_database(category + file_name + ".csv", db_address)
            self.tabs.createDataTab(file_name, db_address, filepath)
        
        #print(category + file_name + ".csv")

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
        file_dropdown = self.create_toolbar_dropdown(tr("file_dropdown"), menuBar)

        self.saveActionSQL = self.create_toolbar_button(tr("save_current_SQL"), file_dropdown, lambda: self.tabs.saveCurrentTabSQL())
        self.saveActionSQLAs = self.create_toolbar_button(tr("save_current_SQL_as"), file_dropdown, lambda: self.tabs.saveCurrentTabAsSQL())
        self.saveActionCSV = self.create_toolbar_button(tr("save_current_csv_as"), file_dropdown, lambda: self.tabs.saveCurrentTabAsCSV())
        self.exitAction = self.create_toolbar_button(tr("exit"), file_dropdown, self.parent.close)

        file_dropdown.aboutToShow.connect(lambda: self.parent.menus.hideItemsOnCondition([], [self.saveActionSQL, self.saveActionSQLAs, self.saveActionCSV], self.parent.menus.tabs.currentTabType(data_type = "DataTab")))
        
        #
        editDropdown = self.create_toolbar_dropdown(tr("edit_dropdown"), menuBar)
        merge_tabs = self.create_toolbar_button(tr("concat_menu"), editDropdown, lambda: self.parent.menus.concatWizard.createMenu())
        modify_keys = self.create_toolbar_button(tr("modify_menu"), editDropdown, lambda: self.tabs.modifyTab())
        data_button = self.create_toolbar_button(tr("data_menu"), editDropdown, lambda: self.parent.menus.setCurrentWidget(self.parent.tabs))
        settings_button = self.create_toolbar_button(tr("settings_menu"), editDropdown, lambda: self.parent.menus.setCurrentWidget(self.parent.settings))

        editDropdown.aboutToShow.connect(lambda: self.parent.menus.hideItemsOnMenu([], [merge_tabs, modify_keys], self.parent.menus.tabs))
        editDropdown.aboutToShow.connect(lambda: self.parent.menus.disableItemsOnMenu([data_button], [], self.parent.menus.tabs))
        editDropdown.aboutToShow.connect(lambda: self.parent.menus.disableItemsOnMenu([settings_button], [], self.parent.menus.settings))

        #Database
        database_names = database.get_all_databases()

        database_dropdown = self.create_toolbar_dropdown(tr("database_dropdown"), menuBar)

        self.parent.menus.currentChanged.connect(lambda: self.parent.menus.disableItemsOnMenu([], [database_dropdown], self.parent.menus.tabs))

        view_dropdown = self.create_toolbar_dropdown(tr("view"), database_dropdown)
        self.database_dropdowns(database_names, view_dropdown)

        export_dropdown = self.create_toolbar_dropdown(tr("export_data"), database_dropdown)
        self.database_dropdowns(database_names, export_dropdown)

        import_button = self.create_toolbar_button(tr("import_data"), database_dropdown, lambda: self.parent.menus.importwizard.importData())
        # Validation
        validation_drop = self.create_toolbar_dropdown(tr("query"), menuBar)
        saved_queries_drop = self.create_toolbar_dropdown(tr("SQL_query"), menuBar)
        tba_drop = self.create_toolbar_dropdown(tr("TBA_query"), validation_drop)
        tba_import_drop = self.create_toolbar_dropdown(tr("import_data"), tba_drop)

        self.create_toolbar_button('Request Teams', tba_import_drop, lambda: self.tabs.createDataTabFromList('TBA Request', tba_api.generate_team_data(config_maker.read_global_config().current_competition_key), '', (None, None)))
        self.create_toolbar_button('Request Matches', tba_import_drop, lambda: self.tabs.createDataTabFromList('TBA Request', tba_api.generate_match_data(config_maker.read_global_config().current_competition_key), '', (None, None)))
        self.create_toolbar_button('Request Matches (Teams)', tba_import_drop, lambda: self.tabs.createDataTabFromList('TBA Request', tba_api.generate_match_teams(config_maker.read_global_config().current_competition_key), '', (None, None)))
        self.create_toolbar_button('Request Coral From Matches', tba_import_drop, lambda: self.tabs.createDataTabFromList('TBA Request', tba_api.get_coral_from_each_match(config_maker.read_global_config().current_competition_key), '', (None, None)))

        for sql_script in database.get_sql_scripts():
            filename = sql_script[0]
            filepath = sql_script[1]
            self.sqlScriptButton(filename, filepath, saved_queries_drop)


        #
        helpDropdown = self.create_toolbar_dropdown(tr("help_menu"), menuBar)
        self.create_toolbar_button(tr("about_menu"), helpDropdown, lambda: self.parent.menus.setCurrentWidget(self.parent.menus.readme))
        self.create_toolbar_button(tr("license_menu"), helpDropdown, lambda: self.parent.menus.setCurrentWidget(self.parent.menus.license))
        #

    def manyDataCreateTab(self, filename, filepath):
        data = database.run_sql_script(filepath)
        for data_item in zip(data, range(len(data))):
            self.tabs.createDataTabFromList(f'{filename}-{data_item[1]}', data_item[0], '', (None, None))

    def sqlScriptButton(self, filename, filepath, drop):
        self.create_toolbar_button(filename, drop, lambda: self.manyDataCreateTab(filename, filepath))


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

    def file_dialog(self, name = "", extension = "Comma Separated (*.csv)", many = False): # Returns a filepath
        if many == False:
            return QFileDialog.getOpenFileName(self, "Open File", name, extension)[0]
        else:
            return QFileDialog.getOpenFileNames(self, "Open File", name, extension)[0]

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
        if currentDatabase == None:
            currentDatabase = config_maker.read_global_config().database_name
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

class ImportMenu(QWidget):
    def __init__(self, parent, filepath):
        super(QWidget, self).__init__(parent)

        self.layoutGrid = QGridLayout(self)
        self.setLayout(self.layoutGrid)
        self.setAutoFillBackground(True)

        self.parent = parent

        self.filepath = filepath
        label = QLabel(self.filepath)

        self.layoutGrid.addWidget(label, 0, 0, alignment=Qt.AlignCenter)

        #####
        if (self.filepath == '' or not(database.test(self.filepath))):
            self.deleteSelf()
        else:
            self.data = database.read_csv(self.filepath)
            key_number = len(self.data[0])

            #table
            self.table = QTableWidget(4, key_number)
            self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.table.setVerticalHeaderLabels([tr("key_header"), tr("datatype_header"), "Datapoint 1", "Datapoint 2"])
            self.layoutGrid.addWidget(self.table, 1, 1)

            #Checkboxes
            self.sidebar = QVBoxLayout()
            self.tab_name = QLineEdit(os.path.splitext(os.path.basename(self.filepath))[0])
            self.format_label = QLabel(tr("format_selector"))
            self.key_check = QCheckBox(tr("keys"))
            self.type_check = QCheckBox(tr("datatypes"))
            self.key_check.setChecked(True)
            self.type_check.setChecked(True)
            self.key_check.stateChanged.connect(self.updateTable)
            self.type_check.stateChanged.connect(self.updateTable)
            self.sidebar.addWidget(self.tab_name)
            self.sidebar.addWidget(self.format_label)
            self.sidebar.addWidget(self.key_check)
            self.sidebar.addWidget(self.type_check)

            self.tab_name.textChanged[str].connect(self.updateConfirm)
            self.confirm_button = QPushButton(tr("button_confirm"))
            self.confirm_button.clicked.connect(self.confirm)
            self.sidebar.addWidget(self.confirm_button)

            self.cancel_button = QPushButton(tr("button_cancel"))
            self.cancel_button.clicked.connect(self.deleteSelf)
            self.sidebar.addWidget(self.cancel_button)

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
        keys = []
        types = []
        for x in range(0, len(self.data[0])):
            keys.append(self.table.item(0, x).text().lstrip())
            types.append(self.table.item(1, x).text().lstrip())
        
        data_buffer = []
        for row in self.data:
            row_buffer = []
            for item in row:
                row_buffer.append(item.lstrip())
            data_buffer.append(row_buffer)

        if self.key_check.isChecked():
            data_buffer.pop(0)
        if self.type_check.isChecked():
            data_buffer.pop(0)
        
        #print(self.data)
        #print("Short Data:")
        #print(data_buffer)

        data_confirmed = [keys, types, *data_buffer]

        self.parent.parent.tabs.createDataTabFromList(self.tab_name.text(), data_confirmed, self.filepath, (None, None))
        self.deleteSelf()

    def deleteSelf(self):
        self.deleteLater()

    def updateConfirm(self):
        banned_names = [""]

        if (self.parent.parent.tabs.test(self.tab_name.text()) or self.tab_name.text() in banned_names):
            self.confirm_button.setEnabled(False)
        else:
            self.confirm_button.setEnabled(True)

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

class ImportWizard(QStackedWidget):
    def __init__(self, parent):
        super(QStackedWidget, self).__init__(parent)
        self.parent = parent
        self.currentChanged.connect(lambda: self.menuCompleted())

    def menuCompleted(self):
        if self.count() > 0:
            self.setCurrentIndex(0)
        else:
            self.parent.setCurrentWidget(self.parent.tabs)

    def importData(self, filepaths = None):

        if self.count() <= 0:
            for index in range(self.count()):
                self.widget(index).deleteLater()

            if filepaths == None:
                filepaths = SaveFile.file_dialog(self, many = True)
            if filepaths != None:
                if len(filepaths) > 0:
                    for filepath in filepaths:
                        self.addWidget(ImportMenu(self, filepath))
            self.setCurrentIndex(0)
        
        if filepaths != None:
            self.parent.setCurrentWidget(self)

class ModifyWizard(QWidget):
    def __init__(self, parent, data, db_address, tab, name):
        super(QWidget, self).__init__(parent)

        self.layoutGrid = QGridLayout(self)
        self.setLayout(self.layoutGrid)
        self.setAutoFillBackground(True)

        self.parent = parent

        self.data = data
        
        self.heightVar = 200
        

        self.scroll_area = QScrollArea()
        self.sidebar = DraggableGroupBox(self, self.heightVar)
        self.scroll_area.setWidgetResizable(True)
        self.sidebar_layout = self.sidebar.layout
        self.scroll_area.setWidget(self.sidebar)
        
        self.addItemButton = QPushButton("+")
        self.removeItemButton = QPushButton("-")
        self.addItemButton.clicked.connect(lambda: self.addItem())
        self.removeItemButton.clicked.connect(lambda: self.removeItem())

        self.nameInput = QLineEdit()

        self.directButton = QPushButton("Direct")
        self.directButton.clicked.connect(lambda: self.directConversion())

        self.openPresetsButton = QPushButton("Open Presets Folder")
        self.openPresetsButton.clicked.connect(lambda: mph.openFolder())
        self.confirmButton = QPushButton("Confirm")
        self.confirmButton.clicked.connect(lambda: self.saveData(self.nameInput.text(), mph.runConversion(self.getConversion(), self.data, self.getConstants())))

        self.nameInput.textChanged.connect(lambda: self.confirmButton.setEnabled(not(self.parent.test(self.nameInput.text()))))

        self.saveConversionButton = QPushButton("Save Conversion")
        self.saveConversionButton.clicked.connect(lambda: self.saveConversion())

        self.loadConversionButton = QPushButton("Load Conversion")
        self.loadConversionButton.clicked.connect(lambda: self.loadConversion())
        

        self.layoutGrid.addWidget(self.pairItems([self.addItemButton, self.removeItemButton]), 0, 0)
        self.layoutGrid.addWidget(self.pairItems([QLabel("Name:"), self.nameInput]), 1, 0)

        self.layoutGrid.addWidget(self.scroll_area, 2, 0)

        self.layoutGrid.addWidget(self.pairItems([self.directButton, self.openPresetsButton, self.saveConversionButton, self.loadConversionButton, self.confirmButton]), 3, 0)

    def saveData(self, name, data):
        self.parent.createDataTabFromList(name, data, None, (None, None))
        self.parent.delete("Modify Data")

    def directConversion(self):
        if self.sidebar_layout.count():
            widgets = list(self.sidebar_layout.itemAt(i).widget() for i in range(self.sidebar_layout.count())) 
            for widget in widgets:
                widget.delete()

        for item in zip(self.data[0], self.data[1]):
            
            preset = "direct.py"
            self.addItem(key = item[0], custom = "Default", preset = preset, keylist = [item[0]])


    def loadConversion(self):
        name = SaveFile.file_dialog(self, "ModifyData\\ConversionPresets\\")
        if name != "":
            data = mph.readConversion(name)
            #Delete Current Conversion
            widgets = (self.sidebar_layout.itemAt(i).widget() for i in range(self.sidebar_layout.count())) 
            for widget in widgets:
                self.deleteWidget(widget)

            #Load Conversion
            for row in data['rows']:
                self.addItem(key = row['name'], custom = row['category'], preset = row['preset'], keylist = row['keys'])
            print(data['rows'])

    def saveConversion(self):
        name = SaveFile.file_save(self, "ModifyData\\ConversionPresets\\")
        if name != "":
            presets = self.getConversion()
            mph.saveConversion(presets, name)

    def getConversion(self, constants = False):
        key_list = self.data[0]
        presets = [key_list]
        widgets = (self.sidebar_layout.itemAt(i).widget() for i in range(self.sidebar_layout.count())) 
        for widget in widgets:
            key = widget.key()
            values = widget.getValues()
            preset_group = values[0]
            preset_name = values[1]
            keys = values[2]
            if constants:
                presets.append([key, preset_group, preset_name, *keys])
            else:
                presets.append([key, preset_group, preset_name, *keys])
        return(presets)

    def getConstants(self):
        key_list = self.data[0]
        presets = [key_list]
        widgets = (self.sidebar_layout.itemAt(i).widget() for i in range(self.sidebar_layout.count())) 
        for widget in widgets:
            constants = widget.getConstants()
            presets.append(constants)
        return(presets)


    def addItem(self, key = "", custom = None, preset = None, keylist = None, size = None):
        if size == None:
            size = self.heightVar
        buffer = PresetSelector(self, custom = custom, preset = preset, keylist = keylist, key = key, size = size)
        self.sidebar_layout.addWidget(buffer)
    
    def removeItem(self):
        if type(self.sidebar_layout.itemAt(self.sidebar_layout.count() - 1)) != type(None):
            self.sidebar_layout.itemAt(self.sidebar_layout.count() - 1).widget().delete()

    def pairItems(self, items, frame = False, size = None):
        if frame:
            pair = QFrame()
            pair.setFrameStyle(QFrame.Panel | QFrame.Raised)
            pair.setLineWidth(2)
        else:
            pair = QWidget()
        pair_layout = QHBoxLayout(pair)
        for item in items:
            pair_layout.addWidget(item)

        if size != None:
            pair.setFixedHeight(size)
        return(pair)

    def fetchPresets(self, custom = False):
        if custom:
            filenames = next(os.walk("ModifyData/ModifyPresets/"), (None, None, []))[2]
        else:
            filenames = next(os.walk("ModifyData/DefaultModifyPresets/"), (None, None, []))[2]
        return filenames

    def dropdownMenu(self, data):
        dropdown = UnscrollableQComboBox(self.sidebar)
        dropdown.addItems(data)
        return(dropdown)

    def preset(self, keys):
        presets = QWidget()
        presets_layout = QHBoxLayout()
        presets.setLayout()

class PresetSelector(QFrame):
    def __init__(self, parent, custom = None, preset = None, keylist = None, key = "", size = 100):
        super(QWidget, self).__init__()

        self.parent = parent
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.setLineWidth(2)

        self.setFixedHeight(size)

        self.key_entry = QLineEdit(key)
        self.delete_button = QPushButton("-")
        self.delete_button.clicked.connect(lambda: self.delete())
        self.delete_button.setFixedWidth(40)

        self.preset_default = preset

        self.custom_dropdown = self.parent.dropdownMenu(["Default", "Custom"])
        if custom != None:
            self.custom_dropdown.setCurrentText(custom)
        self.custom_dropdown.currentTextChanged.connect(lambda: self.updateSelector())

        self.selector_dropdown = self.parent.dropdownMenu(["None"])
        self.selector_dropdown.currentTextChanged.connect(lambda: self.updateKeys())

        self.keys = QWidget()
        self.keys_layout = QHBoxLayout()
        self.keys.setLayout(self.keys_layout)

        self.layout.addWidget(self.delete_button)
        self.layout.addWidget(self.key_entry)
        self.layout.addWidget(self.custom_dropdown)
        self.layout.addWidget(self.selector_dropdown)
        self.layout.addWidget(self.keys)

        self.updateSelector(values=keylist)

    def key(self):
        return(self.key_entry.text())

    def getKeys(self):
        keys = []
        items = (self.keys_layout.itemAt(i).widget() for i in range(self.keys_layout.count()))
        for item in items:
            keys.append(item.getValue())
        return(keys)

    def getConstants(self):
        keys = []
        items = (self.keys_layout.itemAt(i).widget() for i in range(self.keys_layout.count()))
        for item in items:
            keys.append(item.constant)
        return(keys)


    def manualUpdateSelector(self):
        self.selector_dropdown.clear()
        self.selector_dropdown.addItems(self.parent.fetchPresets(custom = (self.custom_dropdown.currentText() == "Custom")))
        if self.preset_default != None:
            self.selector_dropdown.setCurrentText(self.preset_default)

    def updateSelector(self, values = None):
        self.manualUpdateSelector()
        self.updateKeys(values = values)

    def updateKeys(self, delete = True, values = None):
        if self.selector_dropdown.currentText() != "":
            #print(f"filename: {self.selector_dropdown.currentText()}")
            params = mph.getParams(self.selector_dropdown.currentText(), custom = (self.custom_dropdown.currentText() == "Custom"))
            keys_list = params[0]
            constant_list = [key in params[1] for key in keys_list]

            if delete == True:
                for i in reversed(range(self.keys_layout.count())): 
                    self.keys_layout.itemAt(i).widget().deleteLater()
            
            if values == None:
                values = []
                for key in keys_list:
                    values.append(None)

            for key, constant, value in zip(keys_list, constant_list, values):
                if constant:
                    self.keys_layout.addWidget(PresetConstant(self, key, value))
                else:
                    self.keys_layout.addWidget(PresetDropdown(self, key, value, self.parent.data[0]))

    def getValues(self):
        return([self.custom_dropdown.currentText(), self.selector_dropdown.currentText(), self.getKeys()])

    def delete(self):
        sip.delete(self)

class PresetParameterValue(QWidget):
    def getValue(self):
        return(None)

class PresetConstant(PresetParameterValue):
    def __init__(self, parent, label, value):
        super(QWidget, self).__init__()

        self.constant = True

        self.constant_field = QLineEdit()
        if value != None:
            self.constant_field.setText(value)

        self.setLayout(self.pairItems([QLabel(f"{label}:"), self.constant_field]))

    def getValue(self):
        return(self.constant_field.text())

    def pairItems(self, items):
        pair_layout = QHBoxLayout()
        for item in items:
            pair_layout.addWidget(item)
        return(pair_layout)  

class PresetDropdown(PresetParameterValue):
    def __init__(self, parent, label, value, data):
        super(QWidget, self).__init__()

        self.constant = False
        self.parent = parent

        self.dropdown = UnscrollableQComboBox(scrollWidget = self.parent.parent.sidebar)
        self.dropdown.addItems(data)

        if value != None:
            self.dropdown.setCurrentText(value)

        self.setLayout(self.pairItems([QLabel(f"{label}:"), self.dropdown]))

    def getValue(self):
        return(self.dropdown.currentText())

    def pairItems(self, items):
        pair_layout = QHBoxLayout()
        for item in items:
            pair_layout.addWidget(item)
        return(pair_layout)

class ConcatWizard(QStackedWidget):
    def __init__(self, parent):
        super(QStackedWidget, self).__init__(parent)
        self.parent = parent
        self.currentChanged.connect(lambda: self.menuCompleted())

    def menuCompleted(self):
        if self.count() > 0:
            self.setCurrentIndex(0)
        else:
            self.parent.setCurrentWidget(self.parent.tabs)

    def createMenu(self):
        if self.count() <= 0:
            self.addWidget(ConcatMenu(self))
        self.setCurrentIndex(0)
        self.parent.setCurrentWidget(self)

class ConcatMenu(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        self.layoutGrid = QGridLayout(self)
        self.setLayout(self.layoutGrid)
        self.setAutoFillBackground(True)

        self.parent = parent
        self.tabs = self.parent.parent.tabs

        #
        self.sidebar = QVBoxLayout()
        self.tab_name = QLineEdit(tr("merge_tabs_default_name"))
        self.format_selector = QWidget()
        self.format_selector_layout = QHBoxLayout()
        self.format_selector.setLayout(self.format_selector_layout)
        self.format_label = QLabel(tr("format_selector"))

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
        

        self.confirm_button = QPushButton(tr("button_confirm"))
        self.confirm_button.clicked.connect(lambda: self.confirm())
        self.sidebar.addWidget(self.confirm_button)

        self.cancel_button = QPushButton(tr("button_cancel"))
        self.cancel_button.clicked.connect(lambda: self.deleteSelf())
        self.sidebar.addWidget(self.cancel_button)

        self.layoutGrid.addLayout(self.sidebar, 1, 0)

        self.tab_name.textChanged.connect(lambda: self.confirm_button.setEnabled(not(self.tabs.test(self.tab_name.text()))))

        self.updateList()

    def confirm(self):
        formatList = self.tabs.tabData(self.format.currentText(), keys=True)[1][0:2]

        data = []

        for tab_index in range(self.chosen_items.count()):
            tab_name = self.chosen_items.item(tab_index).text()
            tab_data = self.tabs.tabData(tab_name, keys=False)[1][1:]
            data.extend(tab_data)

        data = [*formatList, *data]

        self.tabs.createDataTabFromList(self.tab_name.text(), data, "", (None, None))
        self.deleteSelf()

    def deleteSelf(self):
        self.deleteLater()

    def updateList(self):
        self.possible_items.clear()
        self.chosen_items.clear()
        self.possible_items.addItems(self.dataTabs(self.format.currentText()))

    def dropdownMenu(self, data):
        dropdown = QComboBox()
        dropdown.addItems(data)
        return(dropdown)

    def dataTabs(self, formatTab = None):
        tabs = [*self.tabs.tablist]
        tabs = list(filter((lambda tabname: self.tabs.tablist[tabname][2] == "DataTab"), tabs))
        if formatTab != None:
            tabs = list(map(lambda tabname: (tabname, self.data(tabname)[0]), tabs))
            tabs = list(filter((lambda tab: tab[1] == self.data(formatTab)[0]), tabs))
            tabs = [tab[0] for tab in tabs]
        return(tabs)

    def data(self, name):
        return(self.tabs.tabData(name, keys=True)[1])

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

class MenuManager(QStackedWidget):
    def __init__(self, parent):
        super(QStackedWidget, self).__init__()
        self.parent = parent
        self.tabs = Tabs(self)
        self.settings = Settings(self)
        self.license = License(self)
        self.readme = ReadMe(self)
        self.importwizard = ImportWizard(self)
        self.concatWizard = ConcatWizard(self)

        self.addWidget(self.tabs)
        self.addWidget(self.settings)
        self.addWidget(self.license)
        self.addWidget(self.readme)
        self.addWidget(self.importwizard)
        self.addWidget(self.concatWizard)

        self.setCurrentWidget(self.tabs)

    def disableItemsOnMenu(self, items_disabled, items_enabled, menu):
        menu_selected = (self.currentIndex() == self.indexOf(menu))

        self.disableItemsOnCondition(items_disabled, items_enabled, menu_selected)

    def disableItemsOnCondition(self, items_disabled, items_enabled, condition):

        for item in items_disabled:
            item.setEnabled(not(condition))
        for item in items_enabled:
            item.setEnabled(condition)
        
    def hideItemsOnMenu(self, items_disabled, items_enabled, menu):
        menu_selected = (self.currentIndex() == self.indexOf(menu))
        
        self.hideItemsOnCondition(items_disabled, items_enabled, menu_selected)

    def hideItemsOnCondition(self, items_disabled, items_enabled, condition):

        for item in items_disabled:
            item.setVisible(not(condition))
        for item in items_enabled:
            item.setVisible(condition)
    
class Settings(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.parent = parent 
        self.global_config = self.getGlobalConfig()

        self.config_items = {}
        self.config_items['host'] = SettingItem(self, tr("host"), set_data= self.global_config['host'])
        self.config_items['user'] = SettingItem(self, tr("user"), set_data= self.global_config['user'])
        self.config_items['password'] = SettingItem(self, tr("password"), set_data= self.global_config['password'], echomode= QLineEdit.Password)
        self.config_items['database_name'] = SettingItem(self, tr("database_name"), set_data= self.global_config['database_name'])
        self.config_items['table_name'] = SettingItem(self, tr("table_name"), set_data= self.global_config['table_name'])
        self.config_items['current_competition_key'] = SettingItem(self, tr("current_comp_key"), set_data= self.global_config['current_competition_key'])
        self.config_items['tba_key'] = SettingItem(self, tr("TBA_key"), set_data= self.global_config['tba_key'])
        self.config_items['language'] = SettingDropdownItem(self, tr("language"), self.global_config['language'], ['English', 'Português'], ['en', 'pt'])

        for key in self.config_items.keys():
            self.layout.addWidget(self.config_items[key])
        
        self.need_to_restart = QLabel(tr("restart_needed"))
        self.layout.addWidget(self.need_to_restart)
        self.need_to_restart.setVisible(False)

        self.config_items['language'].field.currentIndexChanged.connect(lambda: self.need_to_restart.setVisible(True))

        self.buttons = QWidget()
        self.buttons_layout = QHBoxLayout()
        self.buttons.setLayout(self.buttons_layout)

        self.cancel_button = QPushButton(tr("button_cancel"))
        self.cancel_button.clicked.connect(lambda: self.cancel())
        self.confirm_button = QPushButton(tr("button_confirm"))
        self.confirm_button.clicked.connect(lambda: self.confirm())

        self.buttons_layout.addWidget(self.cancel_button)
        self.buttons_layout.addWidget(self.confirm_button)
        self.layout.addWidget(self.buttons)

    def confirm(self):
        self.global_config = self.getConfig()
        config_maker.make_config(config_maker.Global_Config(*[self.global_config[key] for key in ['host', 'user', 'password', 'database_name', 'table_name', 'current_competition_key', 'tba_key', 'language']]), "global_config.json")
        database.read_config()

        if self.need_to_restart.isVisible():
            self.parent.parent.close()

        self.exit()

    def cancel(self):
        self.global_config = self.getGlobalConfig()

        for key in self.config_items.keys():
            self.config_items[key].set_data(self.global_config[key])
        
        self.exit()

    def exit(self):
        self.parent.setCurrentWidget(self.parent.tabs)

    def getConfig(self):
        buffer = {}

        for key in self.config_items.keys():
            buffer[key] = self.config_items[key].get_data()

        return buffer
    
    def getGlobalConfig(self):
        buffer_config = config_maker.read_global_config("global_config.json")
        buffer = {}
        buffer['host'] = buffer_config.host
        buffer['user'] = buffer_config.user
        buffer['password'] = buffer_config.password
        buffer['database_name'] = buffer_config.database_name
        buffer['table_name'] = buffer_config.table_name
        buffer['current_competition_key'] = buffer_config.current_competition_key
        buffer['tba_key'] = buffer_config.tba_key
        buffer['language'] = buffer_config.language

        return(buffer)

class SettingItem(QWidget):
    def __init__(self, parent, label_text, set_data="", echomode=QLineEdit.Normal):
        super(QWidget, self).__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.echomode = echomode

        self.label = QLabel(f'{label_text}:')
        self.layout.addWidget(self.label)

        self.field = QLineEdit(set_data)
        self.field.setEchoMode(echomode)
        self.layout.addWidget(self.field)

    def get_data(self):
        return(self.field.text())

    def set_data(self, data):
        self.field.setText(data)

class SettingDropdownItem(QWidget):
    def __init__(self, parent, label_text, set_data, option_data, return_data):
        super(QWidget, self).__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.return_data = return_data

        self.label = QLabel(f'{label_text}:')
        self.layout.addWidget(self.label)


        self.field = UnscrollableQComboBox(option_data)
        for item in option_data:
            self.field.addItem(item)

        self.set_data(set_data)

        self.layout.addWidget(self.field)

    def get_data(self):
        return(self.return_data[self.field.currentIndex()])

    def set_data(self, data):
        self.field.setCurrentText(data)

class License(QTextBrowser):
    def __init__(self, parent):
        super(QWidget, self).__init__()

        self.setMarkdown(database.get_license())

class ReadMe(QTextBrowser):
    def __init__(self, parent):
        super(QWidget, self).__init__()

        self.setMarkdown(database.get_readme())

class DraggableGroupBox(QGroupBox):
    def __init__(self, parent, heightVar):
        super(DraggableGroupBox, self).__init__(parent)

        self.target = None
        self.setAcceptDrops(True)
        self.layout = QVBoxLayout(self)

        self.heightVar = heightVar

    def eventFilter(self, watched, event):
        if event.type() == QEvent.MouseButtonPress:
            self.mousePressEvent(event)
        elif event.type() == QEvent.MouseMove:
            self.mouseMoveEvent(event)
        elif event.type() == QEvent.MouseButtonRelease:
            self.mouseReleaseEvent(event)
        return super().eventFilter(watched, event)

    def get_index(self, pos):
        for i in range(self.layout.count()):
            if self.layout.itemAt(i).geometry().contains(pos) and i != self.target:
                return i

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.target = self.get_index(event.pos())
        else:
            self.target = None

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.target is not None:
            drag = QDrag(self.layout.itemAt(self.target).widget())
            pix = self.layout.itemAt(self.target).widget().grab()
            mimedata = QMimeData()
            mimedata.setImageData(pix)
            drag.setMimeData(mimedata)
            drag.setPixmap(pix)
            drag.setHotSpot(event.pos() - self.layout.itemAt(self.target).widget().pos())
            drag.exec_()

    def mouseReleaseEvent(self, event):
        self.target = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        point = QPoint(event.pos().x(), event.pos().y() - int(self.heightVar / 2))
        if not event.source().geometry().contains(event.pos()):

            for i in range(self.layout.count()):
                if i > 0:
                    if self.layout.itemAt(i).widget().pos().y() < point.y():
                        source = i + 1
                if i == 0:
                    if self.layout.itemAt(0).widget().pos().y() < point.y():
                        source = 1
                    else:
                        source = 0

            if source is None or source == self.target:
                return
            
            widgets = [self.layout.itemAt(i).widget() for i in range(self.layout.count())]

            widget = QWidgetItem(widgets[self.target])

            self.layout.insertItem(source, self.layout.takeAt(self.target))

            

    def deleteWidget(self, widget):
        sip.delete(widget)

class UnscrollableQComboBox(QComboBox):
    def __init__(self, scrollWidget=None, *args, **kwargs):
        super(UnscrollableQComboBox, self).__init__(*args, **kwargs)  
        self.scrollWidget = scrollWidget
        self.setFocusPolicy(Qt.StrongFocus)

    def wheelEvent(self, *args, **kwargs):
        if self.hasFocus():
            return QComboBox.wheelEvent(self, *args, **kwargs)
        else:
            return self.scrollWidget.wheelEvent(*args, **kwargs)
        

def start_app():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("fusion"))
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(50, 50, 50))
    palette.setColor(QtGui.QPalette.Light, QtGui.QColor(75, 75, 75))
    palette.setColor(QtGui.QPalette.Midlight, QtGui.QColor(62, 62, 62))
    palette.setColor(QtGui.QPalette.Dark, QtGui.QColor(25, 25, 25))
    palette.setColor(QtGui.QPalette.Mid, QtGui.QColor(33, 33, 33))
    palette.setColor(QtGui.QPalette.Text, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(0, 0, 0))
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(50, 50, 50))
    palette.setColor(QtGui.QPalette.Shadow, QtGui.QColor(0, 0, 0))
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(64, 174, 200))
    palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(0, 0, 0))
    palette.setColor(QtGui.QPalette.Link, QtGui.QColor(64, 174, 200))
    palette.setColor(QtGui.QPalette.LinkVisited, QtGui.QColor(64, 174, 200))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(25, 25, 25))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(255, 255, 220))
    palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(0, 0, 0))
    palette.setColor(QtGui.QPalette.PlaceholderText, QtGui.QColor(255, 255, 255, 127))

    disabled_color = QtGui.QColor(255, 80, 80, 150)
    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, disabled_color)
    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, disabled_color)
    app.setPalette(palette)
    win = Window()
    win.show()
    app.exec_()


    #APP CLOSED
    import cleanup
    cleanup.remove_temp_dir()
if __name__ == "__main__":
    import initialization
    start_app()