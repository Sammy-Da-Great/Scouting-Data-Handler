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

if __name__ == "__main__":
    import initialization

import sys
import config_maker
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtGui import QDrag
import database
import os
import ModifyData.ModifyPresetHandler as mph
import tba_api
from datetime import datetime
import sip

import language_manager
from language_manager import tr

#####
palette = QtGui.QPalette()
palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(255, 255, 255))
palette.setColor(QtGui.QPalette.Button, QtGui.QColor(50, 50, 50))
palette.setColor(QtGui.QPalette.Light, QtGui.QColor(75, 75, 75))
palette.setColor(QtGui.QPalette.Midlight, QtGui.QColor(62, 62, 62))
palette.setColor(QtGui.QPalette.Mid, QtGui.QColor(33, 33, 33))
palette.setColor(QtGui.QPalette.Dark, QtGui.QColor(25, 25, 25))
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
#####






version = "2025.5.30"

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

class Tabs(QTabWidget):
    def __init__(self, parent):
        super(QTabWidget, self).__init__(parent)
        self.parent = parent
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(lambda index: self.widget(index).delete_self())

    def saveCurrentTabAsCSV(self):
        file = SaveFile.data_save(self, name = self.tabText(self.currentIndex()) + ".csv")
        if file != "":
            try:
                database.write_csv(file, self.current_tab().data())
            except Exception as e:
                QMessageBox.critical(self, "Error Occurred", str(e))
    
    def saveCurrentTabSQL(self, save_as = False):

        index = self.currentIndex()
        name = self.tabText(index)
        tab = self.widget(index)

        data = tab.data()
        
        db_address = tab.db_address


        if db_address is None:
                db_address = (None, None)

        if not isinstance(db_address, tuple):
                print(f'Attempted to save data with an incorrect db_address: {str(db_address)}. Defaulting to (None, None)')
                db_address = (None, None)

        if not all(db_address) or save_as:
            if db_address == (None, None):
                db_address = ("", "")
            dialog = SaveSQLAsDialog(db_address = db_address)
            if dialog.exec() == 1:
                db_address = (dialog.databaseInput.text(), dialog.tableInput.text())
                tab.db_address = db_address
            else:
                db_address = (None, None)
        
        if all(db_address):
            import mysql.connector
            try:
                database.write_to_database(data[1:], db_address, data[0])
            except mysql.connector.errors.ProgrammingError as e:
                QMessageBox.critical(self, "Failed to Save Data", str(e))
                print(f'Failed to save data: {e}')
            except Exception as e:
                QMessageBox.critical(self, "Error Occurred", str(e))
                print(f'Error Occurred: {e}')

    def current_tab(self):
        return self.currentWidget()

    def add(self, data, name, origin = None, force_name = False):
        if not(force_name):
            names = [self.tabText(index) for index in range(self.count())]
            if name in names:
                i = 1
                
                while f'{name} ({i})' in names:
                    i = i + 1
                name = f'{name} ({i})'
        
        self.addTab(DataTab(self, data, origin = origin), name)

    def test(self, name = None):
        if name is None:
            return self.count() > 0
        else:
            if self.count() > 0:
                return name in [self.tabText(i) for i in range(self.count())]
            else:
                return False
    
    def tab_list(self):
        return [self.widget(i) for i in range(self.count())]
    
    def tab_by_name(self, name): #Not recommended for use
        tabs = dict(zip([tab.name() for tab in self.tab_list()], self.tab_list()))
        return(tabs[name])

class MenuBar(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.tabs = parent.tabs
        self.menus = parent.menus
        self._createMenuBar()

    def set_open_table(self, button, target_database):
        button.triggered.connect(lambda: self.open_table(button.text(), (target_database, button.text()), button.parent().parent().title() + "/" + button.parent().title() + "/", button.parent().parent().title()))

    def open_table(self, file_name, db_address, category, action):
        database_name = db_address[0]
        table_name = db_address[1]
        if not os.path.isdir("tmp/" + category):
            os.makedirs("tmp/" + category)
        if action == tr("view"):
            self.tabs.add(db_address, file_name)

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
        self.saveActionSQLAs = self.create_toolbar_button(tr("save_current_SQL_as"), file_dropdown, lambda: self.tabs.saveCurrentTabSQL(save_as = True))
        self.saveActionCSV = self.create_toolbar_button(tr("save_current_csv_as"), file_dropdown, lambda: self.tabs.saveCurrentTabAsCSV())
        self.exitAction = self.create_toolbar_button(tr("exit"), file_dropdown, self.parent.close)

        file_dropdown.aboutToShow.connect(lambda: self.menus.hideItemsOnCondition([], [self.saveActionSQL, self.saveActionSQLAs, self.saveActionCSV], self.menus.isMenu(self.tabs) and self.tabs.test()))
        
        #
        editDropdown = self.create_toolbar_dropdown(tr("edit_dropdown"), menuBar)
        merge_tabs = self.create_toolbar_button(tr("concat_menu"), editDropdown, lambda: self.menus.concatWizard.createMenu())
        modify_keys = self.create_toolbar_button(tr("modify_menu"), editDropdown, lambda: self.menus.modifyWizard.createMenu())
        data_button = self.create_toolbar_button(tr("data_menu"), editDropdown, lambda: self.menus.setCurrentWidget(self.tabs))
        settings_button = self.create_toolbar_button(tr("settings_menu"), editDropdown, lambda: self.menus.settings.display())

        editDropdown.aboutToShow.connect(lambda: self.menus.hideItemsOnMenu([], [merge_tabs, modify_keys], self.tabs))
        editDropdown.aboutToShow.connect(lambda: self.menus.disableItemsOnCondition([], [merge_tabs, modify_keys], self.tabs.test()))
        editDropdown.aboutToShow.connect(lambda: self.menus.disableItemsOnMenu([data_button], [], self.menus.tabs))
        editDropdown.aboutToShow.connect(lambda: self.menus.disableItemsOnMenu([settings_button], [], self.menus.settings))

        #Database
        database_names = database.get_all_databases()

        database_dropdown = self.create_toolbar_dropdown(tr("database_dropdown"), menuBar)

        self.menus.currentChanged.connect(lambda: self.menus.disableItemsOnMenu([], [database_dropdown], self.menus.tabs))

        view_dropdown = self.create_toolbar_dropdown(tr("view"), database_dropdown)
        self.database_dropdowns(database_names, view_dropdown)

        # self.database_dropdowns(database_names, export_dropdown)

        import_button = self.create_toolbar_button(tr("import_data"), database_dropdown, lambda: self.menus.importwizard.importData())
        # Validation
        query_drop = self.create_toolbar_dropdown(tr("query"), menuBar)
        saved_queries_drop = self.create_toolbar_dropdown(tr("SQL_query"), query_drop)
        tba_drop = self.create_toolbar_dropdown(tr("TBA_query"), query_drop)

        # self.create_toolbar_button('Request Teams', tba_import_drop, lambda: self.tabs.add(tba_api.generate_team_data(config_maker.read_global_config().current_competition_key), 'TBA Request'))
        self.create_toolbar_button('Request Matches', tba_drop, lambda: self.tabs.add(tba_api.generate_match_data(config_maker.read_global_config().current_competition_key), 'TBA Request'))
        self.create_toolbar_button('Request Matches (Teams)', tba_drop, lambda: self.tabs.add(tba_api.generate_match_teams(config_maker.read_global_config().current_competition_key), 'TBA Request'))
        self.create_toolbar_button('Request Coral From Matches', tba_drop, lambda: self.tabs.add(tba_api.get_coral_from_each_match(config_maker.read_global_config().current_competition_key), 'TBA Request'))

        for sql_script in database.get_sql_scripts():
            filename = sql_script[0]
            filepath = sql_script[1]
            self.sqlScriptButton(filename, filepath, saved_queries_drop)


        #
        helpDropdown = self.create_toolbar_dropdown(tr("help_menu"), menuBar)
        self.create_toolbar_button(tr("about_menu"), helpDropdown, lambda: self.menus.setCurrentWidget(self.menus.readme))
        self.create_toolbar_button(tr("license_menu"), helpDropdown, lambda: self.menus.setCurrentWidget(self.menus.license))
        #

    def manyDataCreateTab(self, filename, filepath):
        data = database.run_sql_script(filepath)
        for data_item in zip(data, range(len(data))):
            self.tabs.add(data_item[0], f'{filename}')

    def sqlScriptButton(self, filename, filepath, drop):
        self.create_toolbar_button(filename, drop, lambda: self.manyDataCreateTab(filename, filepath))


    def updateMenuBar(self):
        self._createMenuBar()

class SaveFile(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__()
        self.setGeometry(50, 50, 500, 300)

    def file_save(self, name):
        filename = QFileDialog.getSaveFileName(self, tr("save_file"), name, tr("comma_separated"))[0]
        return filename

    def file_dialog(self, name = "", extension = tr("comma_separated"), many = False): # Returns a filepath
        if many == False:
            return QFileDialog.getOpenFileName(self, tr("open_file"), name, extension)[0]
        else:
            return QFileDialog.getOpenFileNames(self, tr("open_file"), name, extension)[0]

    def data_save(self, name = "", extension = tr("comma_separated")): # Saves to a chosen .csv
        return QFileDialog.getSaveFileName(self, tr("save_file"), name, extension)[0]

class DataTab(QStackedWidget):
    def __init__(self, parent, data, origin = None):
        super(QStackedWidget, self).__init__(parent)
        self.parent = parent

        self.data_menu = self.DataMenu(self)
        self.progress_menu = self.ProgressMenu(self)

        self.db_address = None

        self.progress_menu.data_loader.on_finished.connect(self.finish)
        self.progress_menu.data_loader.errorOccurred.connect(self.on_errorOccurred)
        self.progress_menu.data_loader.setValue.connect(lambda y, x, item: self.data_menu.setItem(y, x, QTableWidgetItem(item)))

        self.addWidget(self.data_menu)
        self.addWidget(self.progress_menu)


        self.set_data(data, origin = origin)
    
    def index(self):
        return self.parent.indexOf(self)
    
    def name(self):
        return self.parent.tabText(self.index())

    def delete_self(self):
        self.progress_menu.thread.quit()
        self.deleteLater()

    def set_data(self, data, origin = None):
        if isinstance(data, list): #if data list
            if isinstance(origin, str):
                self.data_menu.origin_label.setText(str(origin))
            elif origin == (None, None) or origin is None:
                origin = ""
                self.db_address = (None, None)
                self.data_menu.origin_label.setText("")
            elif isinstance(origin, tuple):
                self.data_menu.origin_label.setText(f'{origin[0]}.{origin[1]}')
                self.db_address = origin
            self.progress_menu.load_data(data)

        elif isinstance(data, tuple): #if from database
            self.db_address = data
            if origin is None:
                self.data_menu.origin_label.setText(f'{data[0]}.{data[1]}')
            elif isinstance(origin, tuple):
                self.data_menu.origin_label.setText(f'{origin[0]}.{origin[1]}')
            data = database.read_table(data)
        
            self.progress_menu.load_data(data)

        else:
            print(f"set_data cannot accept type {type(data)}")
            self.deleteLater()

    def data(self):
        return self.data_menu.data()

    @pyqtSlot(str)
    def on_errorOccurred(self, msg):
        self.progress_menu.thread.quit()
        self.progress_menu.error_label.setText(msg)
        QMessageBox.critical(self, "Error Occurred", msg)

    @pyqtSlot()
    def finish(self):
        self.setCurrentWidget(self.data_menu)
        self.progress_menu.thread.quit()

    class DataMenu(QWidget):
        def __init__(self, parent):
            super(QWidget, self).__init__(parent)
            self.parent = parent
            self.origin_label = QLabel("")
            self.table = QTableWidget()
            self.layout = QVBoxLayout()

            self.layout.addWidget(self.origin_label)
            self.layout.addWidget(self.table)

            self.setLayout(self.layout)
        
        def data(self):
            data = []
            data.append([self.table.horizontalHeaderItem(column).text() for column in range(self.table.columnCount())])
            
            for row in range(self.table.rowCount()):
                row_buffer = []
                for column in range(self.table.columnCount()):
                    try:
                        item = self.table.item(row, column)

                        if item is None:
                            item_text = ""
                        else:
                            item_text = item.text()

                        row_buffer.append(item_text)
                    except Exception as e:
                        QMessageBox.critical(self, f"Error Occurred When Retrieving Data From {self.parent.name()}", f'Item ({row}, {column}): {e}')
                data.append(row_buffer)
            return data

        @pyqtSlot(int, int, str)
        def setItem(self, y, x, item):
            if y == -1:
                self.table.setHorizontalHeaderItem(x, item)
            else:
                self.table.setItem(y, x, item)
    
    class ProgressMenu(QWidget):

        start_loading = pyqtSignal(list)

        def __init__(self, parent):
            super(QWidget, self).__init__(parent)
            self.parent = parent
            self.progress = QProgressBar()
            self.error_label = QLabel("")
            self.layout = QVBoxLayout()

            self.layout.addWidget(self.progress)
            self.layout.addWidget(self.error_label)

            self.setLayout(self.layout)

            self.thread = QThread(self)
            self.data_loader = self.DataLoader()
            self.data_loader.progressChanged.connect(self.progress.setValue)

        def init_sequence(self):
            self.progress.setValue(0)
            self.progress.setMaximum(0)
            self.error_label.setText("")
            self.error_label.setEnabled(False)
            self.parent.setCurrentWidget(self)

        def load_data(self, data):
            self.init_sequence()

            if isinstance(data, list): #if datalist
                data = data

            elif isinstance(data, tuple): #if db_address
                data = database.read_table(data)
            else:
                print(f"set_data cannot accept type {type(data)}")
                data = None

            if not data is None:
                self.progress.setMaximum(len(data) * len(data[0]))
                self.parent.data_menu.table.setRowCount(len(data) - 1)
                self.parent.data_menu.table.setColumnCount(len(data[0]))

                self.thread.start()
                self.data_loader.moveToThread(self.thread)


                self.start_loading.connect(self.data_loader.fillTable)
                self.start_loading.emit(data)

        class DataLoader(QObject):
            progressChanged = pyqtSignal(int)
            setValue = pyqtSignal(int, int, str)
            started = pyqtSignal()
            on_finished = pyqtSignal()
            errorOccurred = pyqtSignal(str)

            @pyqtSlot(list)
            def fillTable(self, data):
                row_total = len(data)
                column_total = len(data[0])
                for row in range(0, row_total):
                    if data[row]:
                        for column in range(0, column_total):
                            try:
                                item = str(data[row][column])
                                self.setValue.emit(row - 1, column, item)
                                self.progressChanged.emit((row * column_total) + column + 1)
                            except Exception as e:
                                self.errorOccurred.emit(f'item {column}, {row}: {str(e)}')
                    else:
                        self.errorOccurred.emit(f'row {row} is empty')
                self.on_finished.emit()

class SaveSQLAsDialog(QDialog):
    def __init__(self, parent=None, db_address=(None, None)):
        super().__init__(parent)
        currentDatabase = db_address[0]
        if currentDatabase == None:
            currentDatabase = config_maker.read_global_config().database_name
        currentTable = db_address[1]
        self.setWindowTitle(tr("save_current_SQL_as"))
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.databaseLabel = QLabel(tr("database_name"))
        self.layout.addWidget(self.databaseLabel)
        self.databaseInput = QLineEdit()
        self.databaseInput.setText(currentDatabase)
        self.layout.addWidget(self.databaseInput)
        self.tableLabel = QLabel(tr("table_name"))
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

            if filepaths == None or not filepaths:
                filepaths = SaveFile.file_dialog(self, many = True)
            if filepaths:
                if len(filepaths) > 0:
                    for filepath in filepaths:
                        self.addWidget(self.ImportMenu(self, filepath))
            self.setCurrentIndex(0)
        
        if filepaths:
            self.parent.setCurrentWidget(self)

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
                self.table.setVerticalHeaderLabels([tr("key_header"), tr("datatype_header"), "1", "2"])
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


            data_confirmed = [keys, types, *data_buffer]

            self.parent.parent.tabs.add(data_confirmed, self.tab_name.text(), origin = self.filepath)
            self.deleteSelf()

        def deleteSelf(self):
            self.deleteLater()

        def updateConfirm(self):
            banned_names = [""]

            if (self.tab_name.text() in banned_names):
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

class ModifyWizard(QStackedWidget):
    def __init__(self, parent):
        super(QStackedWidget, self).__init__(parent)
        self.parent = parent
        self.currentChanged.connect(lambda: self.menuCompleted())
        self.tabs = self.parent.tabs

    def menuCompleted(self):
        if self.count() > 0:
            self.setCurrentIndex(0)
        else:
            self.parent.setCurrentWidget(self.parent.tabs)

    def createMenu(self):
        tab = self.tabs.current_tab()
        data = tab.data()
        if (self.count() <= 0) and not (data is None):

                self.addWidget(self.ModifyMenu(self, tab))

                self.setCurrentIndex(0)
                self.parent.setCurrentWidget(self)
        elif (self.count() > 0):
            self.setCurrentIndex(0)
            self.parent.setCurrentWidget(self)
        else:
            print("Attempted to modify nothing.")

    class ModifyMenu(QWidget):
        def __init__(self, parent, tab):
            super(QWidget, self).__init__(parent)

            self.layoutGrid = QGridLayout(self)
            self.setLayout(self.layoutGrid)
            self.setAutoFillBackground(True)

            self.tab = tab

            self.parent = parent
            self.db_address = self.tab.db_address

            self.data = self.tab.data()
            
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
            self.modify_target = QLabel(f'{tr("modify_target")}: {self.tab.name()}')

            self.directButton = QPushButton(tr("direct"))
            self.directButton.clicked.connect(lambda: self.directConversion())

            self.cancel_button = QPushButton(tr("button_cancel"))
            self.cancel_button.clicked.connect(lambda: self.deleteSelf())

            self.openPresetsButton = QPushButton(tr("open_presets_folder"))
            self.openPresetsButton.clicked.connect(lambda: mph.openFolder())
            self.confirmButton = QPushButton(tr("button_confirm"))
            self.confirmButton.clicked.connect(lambda: self.saveData(self.nameInput.text(), mph.runConversion(self.getConversion(), self.data, self.getConstants())))

            self.nameInput.textChanged.connect(lambda: self.confirmButton.setEnabled(not(self.parent.tabs.test(self.nameInput.text()))))
            self.nameInput.setPlaceholderText(tr("tab_name"))

            self.saveConversionButton = QPushButton(tr("save_conversion"))
            self.saveConversionButton.clicked.connect(lambda: self.saveConversion())

            self.loadConversionButton = QPushButton(tr("load_conversion"))
            self.loadConversionButton.clicked.connect(lambda: self.loadConversion())
            

            self.layoutGrid.addWidget(self.pairItems([self.addItemButton, self.removeItemButton]), 2, 0)
            self.layoutGrid.addWidget(self.nameInput, 1, 0)
            self.layoutGrid.addWidget(self.modify_target, 0, 0)

            self.layoutGrid.addWidget(self.scroll_area, 3, 0)

            self.layoutGrid.addWidget(self.pairItems([self.directButton, self.openPresetsButton, self.saveConversionButton, self.loadConversionButton]), 4, 0)
            self.layoutGrid.addWidget(self.pairItems([self.cancel_button, self.confirmButton]), 5, 0)

        def saveData(self, name, data):
            self.parent.tabs.add(data, name, origin = self.db_address)
            self.deleteSelf()

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

        def deleteSelf(self):
            self.deleteLater()

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
        self.key_entry.setPlaceholderText(tr("key"))
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

        self.updateSelector(values = keylist)

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
                    self.keys_layout.addWidget(self.PresetConstant(self, key, value))
                else:
                    self.keys_layout.addWidget(self.PresetDropdown(self, key, value, self.parent.data[0]))

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
            self.addWidget(self.ConcatMenu(self))
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

            self.format = self.dropdownMenu([tab.name() for tab in self.dataTabs()])
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
            formatList = self.tabs.tab_by_name(self.format.currentText()).data()[0:1]

            data = []

            for tab in [self.tabs.tab_by_name(self.chosen_items.item(tab_index).text()) for tab_index in range(self.chosen_items.count())]:
                tab_data = tab.data()[2:]
                data.extend(tab_data)

            data = [*formatList, *data]

            self.tabs.add(data, self.tab_name.text(), origin = None)
            self.deleteSelf()

        def deleteSelf(self):
            self.deleteLater()

        def updateList(self):
            self.possible_items.clear()
            self.chosen_items.clear()
            self.possible_items.addItems([tab.name() for tab in self.dataTabs(formatTab = self.tabs.tab_by_name(self.format.currentText()))])

        def dropdownMenu(self, data):
            dropdown = QComboBox()
            dropdown.addItems(data)
            return(dropdown)

        def dataTabs(self, formatTab = None):
            tabs = self.tabs.tab_list()
            if formatTab != None:
                tabs = list(filter((lambda tab: tab.data()[0:1] == formatTab.data()[0:1]), tabs)) #filter for only tabs with same keys and data types
            return(tabs)

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
        self.modifyWizard = ModifyWizard(self)

        self.addWidget(self.tabs)
        self.addWidget(self.settings)
        self.addWidget(self.license)
        self.addWidget(self.readme)
        self.addWidget(self.importwizard)
        self.addWidget(self.concatWizard)
        self.addWidget(self.modifyWizard)

        self.setCurrentWidget(self.tabs)

    def isMenu(self, menu):
        return self.currentIndex() == self.indexOf(menu)

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
        self.config_items['host'] = self.SettingItem(self, tr("host"), set_data= self.global_config['host'])
        self.config_items['user'] = self.SettingItem(self, tr("user"), set_data= self.global_config['user'])
        self.config_items['password'] = self.SettingItem(self, tr("password"), set_data= self.global_config['password'], echomode= QLineEdit.Password)
        self.config_items['database_name'] = self.SettingItem(self, tr("database_name"), set_data= self.global_config['database_name'])
        self.config_items['table_name'] = self.SettingItem(self, tr("table_name"), set_data= self.global_config['table_name'])
        self.config_items['current_competition_key'] = self.SettingItem(self, tr("current_competition_key"), set_data= self.global_config['current_competition_key'])
        self.config_items['tba_key'] = self.SettingItem(self, tr("TBA_key"), set_data= self.global_config['tba_key'])
        self.config_items['language'] = self.SettingDropdownItem(self, tr("language"), self.global_config['language'], list(language_manager.language_list.values()), list(language_manager.language_list.keys()))

        for key in self.config_items.keys():
            self.layout.addWidget(self.config_items[key])

        self.restart_criteria = {}
        
        self.need_to_restart = QLabel(tr("restart_needed"))
        self.layout.addWidget(self.need_to_restart)
        self.need_to_restart.setVisible(False)

        self.config_items['language'].field.currentIndexChanged.connect(lambda: self.check_restart_needed('language', 'language'))

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

    def check_restart_needed(self, option_key, key_in_config):
        self.restart_criteria[key_in_config] = (self.config_items[option_key].get_data() != self.global_config[key_in_config])
        needed = any(self.restart_criteria.values())
        self.need_to_restart.setVisible(needed)

    def confirm(self):
        self.global_config = self.getConfig()
        config_maker.make_config(config_maker.Global_Config(*[self.global_config[key] for key in ['host', 'user', 'password', 'database_name', 'table_name', 'current_competition_key', 'tba_key', 'language']]), "global_config.json")
        database.read_config()

        if any(self.restart_criteria.values()):
            print("Setting changes require restart. Closing app...")
            self.parent.parent.close()

        self.exit()

    def cancel(self):
        self.global_config = self.getGlobalConfig()

        for key in self.config_items.keys():
            self.config_items[key].set_data(self.global_config[key])
        
        self.exit()

    def exit(self):
        self.parent.setCurrentWidget(self.parent.tabs)

    def display(self):
        for key in self.config_items.keys():
            self.config_items[key].set_data(self.global_config[key])
        self.parent.setCurrentWidget(self)

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
            self.option_data = option_data

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
            self.field.setCurrentText(self.option_data[self.return_data.index(data)])

class License(QTextBrowser):
    def __init__(self, parent):
        super(QWidget, self).__init__()
        self.setOpenLinks(False)
        self.setOpenExternalLinks(False)

        self.setMarkdown(database.get_license())

class ReadMe(QTextBrowser):
    def __init__(self, parent):
        super(QWidget, self).__init__()
        self.setOpenLinks(False)
        self.setOpenExternalLinks(False)

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

class ScrollLabel(QScrollArea):
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)

        self.setWidgetResizable(True)

        content = QWidget(self)
        self.setWidget(content)

        lay = QVBoxLayout(content)

        self.label = QLabel(content)

        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.label.setWordWrap(True)

        lay.addWidget(self.label)

    def setText(self, text):
        self.label.setText(text)

def start_app():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("fusion"))
    app.setPalette(palette)
    win = Window()
    win.show()
    app.exec_()


    #APP CLOSED
    import cleanup
    cleanup.remove_temp_dir()

if __name__ == "__main__":
    start_app()