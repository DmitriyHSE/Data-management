from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from database import Database
import start_window
import traceback
import design


class startWindow(QtWidgets.QMainWindow, start_window.Ui_MainWindow):
    def __init__(self, app):
        super().__init__()
        self.setupUi(self)
        self.app = app
        self.connect_button.clicked.connect(self.connect_to_database)

    def connect_to_database(self):
        try:
            self.app.connect(self.database_name.text(), self.user.text(), self.password.text(), self.host.text(), self.port.text())
            self.close()
        except Exception as ex:
            print(traceback.format_exc())
            self.message("There is no such database!", traceback.format_exc())


class main_window(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.db = None
        self.setupUi(self)
        self.connectionWindow = startWindow(self)
        self.add_person_button.clicked.connect(self.add_person_record)  #
        self.add_department_button.clicked.connect(self.add_department_record)  #
        self.clear_person_button.clicked.connect(self.clear_person)  #
        self.clear_department_button.clicked.connect(self.clear_department)  #
        self.delete_button.clicked.connect(self.delete_by_FIO)  #
        self.delete_database_button.clicked.connect(self.delete_database)  #
        self.search_button.clicked.connect(self.search_by_FIO)
        self.clear_all.clicked.connect(self.clear_database)
        self.delete_chosen_button.clicked.connect(self.delete_chosen)
        self.connect_button.clicked.connect(self.show_start)
        self.columns_departments = ['id', 'name', 'last_update']
        self.columns_persons = ['id', 'title', 'FIO', 'department']
        self.person_table.itemChanged.connect(self.update_persons)
        self.department_table.itemChanged.connect(self.update_departments)
        self.person_table.setColumnCount(4)
        self.department_table.setColumnCount(3)
        self.person_table.setHorizontalHeaderLabels(self.columns_persons)
        self.department_table.setHorizontalHeaderLabels(self.columns_departments)
        self.edit_flag = False

    def show_start(self):
        self.connectionWindow.show()

    def connect(self, name, user, password, host, port):
        self.db = Database(name, user, password, host, port)

    def set_data(self, table, columns, data):
        self.edit_flag = True
        try:
            if data is not None:
                table.setRowCount(len(data))
                for i, row in enumerate(data):
                    for j, col in enumerate(columns):
                        table.setItem(i, j, QTableWidgetItem(str(row[col])))

            else:
                table.setRowCount(0)
        except Exception as ex:
            self.message("Error during setting data!", traceback.format_exc())
        self.edit_flag = False

    def message(self, error, detailed_error="idk", icon=QMessageBox.Warning):
        msg = QMessageBox()
        msg.setWindowTitle("Отчёт")
        msg.setIcon(icon)
        msg.setText(f"{error}")
        msg.setDetailedText(detailed_error)
        msg.addButton(QMessageBox.Ok)
        msg.exec()

    def add_person_record(self):
        try:
            title = self.person_title.text()
            FIO = self.person_FIO.text()
            department = self.person_department.text()
            if title != "" and FIO != "" and department != "" and self.db is not None:
                self.db.add_to_person(title, FIO, department)
                self.data_persons = self.db.get_persons()
                self.set_data(self.person_table, self.columns_persons, self.data_persons)
                self.person_title.clear()
                self.person_FIO.clear()
                self.person_department.clear()
            else:
                self.message(
                    "Check if all fields are filled or if you have connected to db")
        except Exception as ex:
            self.message("Error during adding data!", traceback.format_exc())

    def add_department_record(self):
        try:
            id = self.department_ID.text()
            name = self.department_name.text()
            if id != "" and name != "" and self.db is not None:
                self.db.add_to_department(id, name)
                self.data_departments = self.db.get_departments()
                self.set_data(self.department_table, self.columns_departments, self.data_departments)
                self.department_ID.clear()
                self.department_name.clear()
            else:
                self.message("Check if all fields are filled or if you have connected to db")

        except Exception as ex:
            print(traceback.format_exc())
            self.message("Error during adding data!", str(ex))

    def clear_person(self):
        try:
            self.db.clear_persons()
            self.data_persons = self.db.get_persons()
            self.set_data(self.person_table, self.columns_persons, self.data_persons)
        except Exception as ex:
            self.message("Error during clearing data!", traceback.format_exc())

    def clear_department(self):
        try:
            self.db.clear_departments()
            self.data_departments = self.db.get_departments()
            self.set_data(self.department_table, self.columns_departments, self.data_departments)
        except Exception as ex:
            self.message("Error during clearing data!", traceback.format_exc())

    def clear_database(self):
        try:
            self.clear_person()
            self.clear_department()
        except Exception as ex:
            self.message("Error during clearing data!", traceback.format_exc())

    def delete_database(self):
        try:
            if self.db is not None:
                self.db.delete_database()
                self.data_departments = []
                self.data_persons = []
                self.set_data(self.department_table, self.columns_departments, self.data_departments)
                self.set_data(self.person_table, self.columns_persons, self.data_persons)
                self.db = None
                self.connectionWindow = None
                self.connectionWindow = startWindow(self)
            else:
                self.message("Check if you have connected to db")
        except Exception as ex:
            self.message("Error during deleting database!", traceback.format_exc())

    def delete_by_FIO(self):
        try:
            FIO = self.data_to_delete.text()
            if FIO != "" and self.db is not None:
                self.db.delete_person_by_FIO(FIO)
                self.data_persons = self.db.get_persons()
                self.set_data(self.person_table, self.columns_persons, self.data_persons)
                self.data_to_delete.clear()
            else:
                self.message("Check if all fields are filled or if you have connected to db")
        except Exception as ex:
            self.message("Error during deleting data!", traceback.format_exc())

    def find_by_FIO(self):
        try:
            FIO = self.data_to_delete.text()
            if FIO != "" and self.db is not None:
                self.set_data(self.person_table, self.columns_persons, self.db.delete_person_by_FIO(FIO))
                self.set_data(self.department_table, self.columns_departments, self.db.find_department(FIO))
                self.data_to_delete.clear()
            if FIO == "":
                self.set_data(self.person_table, self.columns_persons, self.data_persons)
                self.set_data(self.department_table, self.columns_departments, self.data_departments)
            else:
                self.message("Check if you have connected to db")
        except Exception as ex:
            self.message("Error during data search!", traceback.format_exc())

    def update_persons(self, item):
        if not self.edit_flag:
            try:
                if item.column() == 1:
                    self.db.update_person_by_title(item.text(), self.person_table.item(item.row(), 0).text())
                elif item.column() == 2:
                    self.db.update_person_by_FIO(item.text(), self.person_table.item(item.row(), 0).text())
                elif item.column() == 3:
                    self.db.update_person_by_department(item.text(), self.person_table.item(item.row(), 0).text())
                self.data_persons = self.db.get_persons()
                self.set_data(self.person_table, self.columns_persons, self.data_persons)
            except Exception:
                self.message("Error during data update!", traceback.format_exc())

    def update_departments(self, item):
        if not self.edit_flag:
            try:
                if item.column() == 0:
                    self.db.update_department_by_id(item.text(), self.data_departments[item.row()]['name'])
                elif item.column() == 1:
                    self.db.update_department_by_name(item.text(), self.department_table.item(item.row(), 0).text())
                self.data_departments = self.db.get_departments()
                self.set_data(self.department_table, self.columns_departments, self.data_departments)
            except Exception:
                print(traceback.format_exc())
                self.message("Error during data update!", traceback.format_exc())

    def search_by_FIO(self):
        try:
            FIO = self.data_to_delete.text()
            if FIO != "" and self.db is not None:
                self.set_data(self.person_table, self.columns_persons, self.db.find_person_by_FIO(FIO))
                self.set_data(self.department_table, self.columns_departments, self.db.find_department(FIO))
                self.data_to_delete.clear()
                self.data_to_delete.clear()
            else:
                self.set_data(self.person_table, self.columns_persons, self.data_persons)
                self.set_data(self.department_table, self.columns_departments, self.data_departments)
        except Exception:
            self.message("Error during data search!", traceback.format_exc())

    def delete_chosen(self):
        if len(self.department_table.selectedIndexes()):
            try:
                for i in self.department_table.selectedIndexes():
                    self.db.delete_department_chosen(self.data_departments[i.row()]['id'])
                    self.data_departments = self.db.get_departments()
                    self.set_data(self.department_table, self.columns_departments, self.data_departments)
            except Exception:
                self.message("Error during data delete!", traceback.format_exc())
        else:
            try:
                for i in self.person_table.selectedIndexes():
                    self.db.delete_person_chosen(self.data_persons[i.row()]['id'])
                    self.data_persons = self.db.get_persons()
                    self.set_data(self.person_table, self.columns_persons, self.data_persons)
            except Exception:
                self.message("Error during data delete!", traceback.format_exc())