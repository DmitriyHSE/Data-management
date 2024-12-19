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
        self.connect_button.clicked.connect(self.show_start)
        #self.delete_button.clicked.connect(self.delete_by_FIO)  #
        self.delete_database_button.clicked.connect(self.delete_database)  #
        self.schedule_table = ["Lesson id", "Teacher id", "Group id", "День недели", "Корпус/онлайн", "Номер аудитории", "Вид занятий", "Время"]
        self.disciplines_table = ["ID дисциплины", "Дисциплины"]
    def show_start(self):
        self.connectionWindow.show()

    def connect(self, name, user, password, host, port):
        self.db = Database(name, user, password, host, port)
    def delete_database(self):
        try:
            if self.db is not None:
                self.db.delete_database()
                self.schedule_table=[]
                self.set_data(self.department_table, self.columns_departments, self.data_departments)
                self.set_data(self.person_table, self.columns_persons, self.data_persons)
                self.db = None
                self.connectionWindow = None
                self.connectionWindow = startWindow(self)
            else:
                self.message("Check if you have connected to db")
        except Exception as ex:
            self.message("Error during deleting database!", traceback.format_exc())
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