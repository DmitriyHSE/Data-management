from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from database import Database
import design
import traceback

class StartWindow(QtWidgets.QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.ui = design.Ui_MainWindow()
        self.ui.setupUi(self)
        self.app = app
        self.ui.connect_button.clicked.connect(self.connect_to_database)

    def connect_to_database(self):
        try:
            self.app.connect(
                self.ui.database_name.text(),
                self.ui.user.text(),
                self.ui.password.text(),
                self.ui.host.text(),
                self.ui.port.text()
            )
            self.close()
        except Exception:
            print(traceback.format_exc())
            self.message("Connection failed!", traceback.format_exc())

    def message(self, text, details, icon=QMessageBox.Warning):
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        msg.setIcon(icon)
        msg.setText(text)
        msg.setDetailedText(details)
        msg.addButton(QMessageBox.Ok)
        msg.exec()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = design.Ui_MainWindow()
        self.ui.setupUi(self)
        self.db = None
        self.connection_window = StartWindow(self)

        # Connect buttons to functions
        self.ui.add_button.clicked.connect(self.add_schedule_record)
        self.ui.update_button.clicked.connect(self.update_selected_record)
        self.ui.delete_button.clicked.connect(self.delete_selected_record)
        self.ui.clear_button.clicked.connect(self.clear_table)
        self.ui.search_button.clicked.connect(self.search_schedule_record)
        self.ui.connect_button.clicked.connect(self.show_start_window)

        # Set up the table
        self.columns_schedule = [
            "ID Урока", "ID Учителя", "ID Группы", "День недели",
            "Корпус/Онлайн", "Аудитория", "Тип урока", "Время"
        ]
        self.ui.schedule_table.setColumnCount(len(self.columns_schedule))
        self.ui.schedule_table.setHorizontalHeaderLabels(self.columns_schedule)

    def show_start_window(self):
        self.connection_window.show()

    def connect(self, db_name, user, password, host, port):
        try:
            self.db = Database(db_name, user, password, host, port)
            data = self.db.get_schedule()
            self.set_table_data(self.ui.schedule_table, data)
        except Exception:
            print(traceback.format_exc())
            self.message("Error connecting to database!", traceback.format_exc())

    def set_table_data(self, table, data):
        try:
            table.setRowCount(len(data))
            for i, row in enumerate(data):
                for j, value in enumerate(row):
                    table.setItem(i, j, QTableWidgetItem(str(value)))
        except Exception:
            print(traceback.format_exc())
            self.message("Error setting table data!", traceback.format_exc())

    def add_schedule_record(self):
        try:
            record = (
                self.ui.lesson_id.text(),
                self.ui.teacher_id.text(),
                self.ui.group_id.text(),
                self.ui.day_of_week.text(),
                self.ui.korpus_online.text(),
                self.ui.auditorium_number.text(),
                self.ui.lesson_type.text(),
                self.ui.lesson_time.text()
            )
            if all(record):
                self.db.add_schedule(record)
                data = self.db.get_schedule()
                self.set_table_data(self.ui.schedule_table, data)
                self.clear_input_fields()
            else:
                self.message("Fill in all fields!", "")
        except Exception:
            print(traceback.format_exc())
            self.message("Error adding record!", traceback.format_exc())

    def update_selected_record(self):
        try:
            current_row = self.ui.schedule_table.currentRow()
            if current_row < 0:
                self.message("No row selected!", "")
                return

            record = (
                self.ui.lesson_id.text(),
                self.ui.teacher_id.text(),
                self.ui.group_id.text(),
                self.ui.day_of_week.text(),
                self.ui.korpus_online.text(),
                self.ui.auditorium_number.text(),
                self.ui.lesson_type.text(),
                self.ui.lesson_time.text()
            )

            if all(record):
                self.db.update_schedule(self.ui.schedule_table.item(current_row, 0).text(), record)
                data = self.db.get_schedule()
                self.set_table_data(self.ui.schedule_table, data)
                self.clear_input_fields()
            else:
                self.message("Fill in all fields!", "")
        except Exception:
            print(traceback.format_exc())
            self.message("Error updating record!", traceback.format_exc())

    def delete_selected_record(self):
        try:
            current_row = self.ui.schedule_table.currentRow()
            if current_row < 0:
                self.message("No row selected!", "")
                return

            lesson_id = self.ui.schedule_table.item(current_row, 0).text()
            self.db.delete_schedule(lesson_id)
            data = self.db.get_schedule()
            self.set_table_data(self.ui.schedule_table, data)
        except Exception:
            print(traceback.format_exc())
            self.message("Error deleting record!", traceback.format_exc())

    def clear_table(self):
        try:
            self.db.clear_schedule()
            self.ui.schedule_table.setRowCount(0)
        except Exception:
            print(traceback.format_exc())
            self.message("Error clearing table!", traceback.format_exc())

    def search_schedule_record(self):
        try:
            search_text = self.ui.lesson_id.text()
            if search_text:
                data = self.db.search_schedule(search_text)
                self.set_table_data(self.ui.schedule_table, data)
            else:
                data = self.db.get_schedule()
                self.set_table_data(self.ui.schedule_table, data)
        except Exception:
            print(traceback.format_exc())
            self.message("Error searching records!", traceback.format_exc())

    def clear_input_fields(self):
        self.ui.lesson_id.clear()
        self.ui.teacher_id.clear()
        self.ui.group_id.clear()
        self.ui.day_of_week.clear()
        self.ui.korpus_online.clear()
        self.ui.auditorium_number.clear()
        self.ui.lesson_type.clear()
        self.ui.lesson_time.clear()

    def message(self, text, details, icon=QMessageBox.Warning):
        msg = QMessageBox()
        msg.setWindowTitle("Message")
        msg.setIcon(icon)
        msg.setText(text)
        msg.setDetailedText(details)
        msg.addButton(QMessageBox.Ok)
        msg.exec()
