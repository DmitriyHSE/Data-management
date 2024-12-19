from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def __init__(self):
        self.teachers_window = None  # Ссылка на окно преподавателей
        self.disciplines_window = None  # Ссылка на окно дисциплин
        self.groups_window = None  # Ссылка на окно групп
        self.students_window = None  # Ссылка на окно студентов
        self.groups_students_window = None  # Ссылка на окно группы-студенты

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1250, 800)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.schedule_table = QtWidgets.QTableWidget(self.centralwidget)
        self.schedule_table.setObjectName("schedule_table")
        self.schedule_table.setColumnCount(8)
        self.schedule_table.setRowCount(120)
        self.schedule_table.setHorizontalHeaderLabels(
            ["ID занятия", "ID преподавателя", "ID группы", "День недели", "Корпус/онлайн", "Номер аудитории",
             "Вид занятий",
             "Время"])
        self.schedule_table.verticalHeader().setVisible(False)
        self.schedule_table.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)

        # Connect buttons with their handlers
        self.connect_button = self.create_button("Подключиться к базе данных")
        self.delete_database_button = self.create_button("Удалить базу данных")
        self.add_data_button = self.create_button("Добавить данные")
        self.add_to_disciplines = self.create_button("Дисциплины", self.open_disciplines_window)
        self.add_to_groups = self.create_button("Группы", self.open_groups_window)
        self.add_to_students = self.create_button("Студенты", self.open_students_window)
        self.add_to_groups_students = self.create_button("Группы-студенты", self.open_groups_students_window)
        self.add_to_teachers = self.create_button("Преподаватели", self.open_teachers_window)

        # Label for the table title
        self.label_title = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.label_title.setFont(font)
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        self.label_title.setText("Расписание")

        # Main Layout
        main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        title_layout = QtWidgets.QHBoxLayout()
        title_layout.addStretch(1)
        title_layout.addWidget(self.label_title)
        title_layout.addStretch(1)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.delete_database_button)
        button_layout.addWidget(self.add_data_button)
        button_layout.addWidget(self.add_to_disciplines)
        button_layout.addWidget(self.add_to_teachers)
        button_layout.addWidget(self.add_to_groups)
        button_layout.addWidget(self.add_to_students)
        button_layout.addWidget(self.add_to_groups_students)

        main_layout.addLayout(title_layout)
        main_layout.addWidget(self.schedule_table)
        main_layout.addLayout(button_layout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def create_button(self, text, handler=None):
        button = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(9)
        button.setFont(font)
        button.setText(text)
        if handler:
            button.clicked.connect(handler)
        return button

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Расписание"))

    # Handlers for button clicks

    def open_teachers_window(self):
        # Проверяем, существует ли окно и не видно ли оно
        if self.teachers_window is None or not self.teachers_window.isVisible():
            self.open_teachers_data_window()

    def open_disciplines_window(self):
        if self.disciplines_window is None or not self.disciplines_window.isVisible():
            self.open_disciplines_data_window()

    def open_groups_window(self):
        if self.students_window is None or not self.students_window.isVisible():
            self.open_groups_data_window()

    def open_students_window(self):
        if self.groups_window is None or not self.groups_window.isVisible():
            self.open_students_data_window()

    def open_groups_students_window(self):
        if self.groups_students_window is None or not self.groups_students_window.isVisible():
            self.open_groups_students_data_window()

    def open_teachers_data_window(self):
        # Если окно уже существует, то сначала удаляем его
        if self.teachers_window is not None:
            if self.teachers_window.isVisible():
                self.teachers_window.close()  # Закрываем окно, если оно открыто
            self.teachers_window.deleteLater()  # Удаление окна из памяти

        # Создаем новое окно
        self.teachers_window = QtWidgets.QWidget()
        self.teachers_window.setWindowTitle("Преподаватели")

        new_table = QtWidgets.QTableWidget(self.teachers_window)
        new_table.setColumnCount(2)  # Количество столбцов
        new_table.setRowCount(20)  # Замените на актуальное количество записей
        new_table.setHorizontalHeaderLabels(
            ["ID преподавателя", "ФИО"])

        layout = QtWidgets.QVBoxLayout(self.teachers_window)
        layout.addWidget(new_table)
        self.teachers_window.setLayout(layout)
        self.teachers_window.resize(800, 600)

        # Обработчик закрытия окна
        self.teachers_window.destroyed.connect(self.on_teachers_window_closed)

        self.teachers_window.show()  # Показываем окно после всех настроек

    def on_teachers_window_closed(self):
        # Сбрасываем ссылку, когда окно закрылось
        self.teachers_window = None

    def open_disciplines_data_window(self):
        # Если окно уже существует, то сначала удаляем его
        if self.disciplines_window is not None:
            if self.disciplines_window.isVisible():
                self.disciplines_window.close()  # Закрываем окно, если оно открыто
            self.disciplines_window.deleteLater()  # Удаление окна из памяти

        # Создаем новое окно
        self.disciplines_window = QtWidgets.QWidget()
        self.disciplines_window.setWindowTitle("Дисциплины")

        new_table = QtWidgets.QTableWidget(self.disciplines_window)
        new_table.setColumnCount(2)  # Количество столбцов
        new_table.setRowCount(9)  # Замените на актуальное количество записей
        new_table.setHorizontalHeaderLabels(["ID дисциплины", "Дисциплины"])

        layout = QtWidgets.QVBoxLayout(self.disciplines_window)
        layout.addWidget(new_table)
        self.disciplines_window.setLayout(layout)
        self.disciplines_window.resize(600, 400)

        # Обработчик закрытия окна
        self.disciplines_window.destroyed.connect(self.on_disciplines_window_closed)

        self.disciplines_window.show()  # Показываем окно после всех настроек

    def on_disciplines_window_closed(self):
        # Сбрасываем ссылку, когда окно закрылось
        self.disciplines_window = None

    def open_groups_data_window(self):
        # Если окно уже существует, то сначала удаляем его
        if self.groups_window is not None:
            if self.groups_window.isVisible():
                self.groups_window.close()  # Закрываем окно, если оно открыто
            self.groups_window.deleteLater()  # Удаление окна из памяти

        # Создаем новое окно
        self.groups_window = QtWidgets.QWidget()
        self.groups_window.setWindowTitle("Группы")

        new_table = QtWidgets.QTableWidget(self.groups_window)
        new_table.setColumnCount(2)  # Количество столбцов
        new_table.setRowCount(10)  # Замените на актуальное количество записей
        new_table.setHorizontalHeaderLabels(["ID группы", "Название группы", "Количество пар в неделю"])

        layout = QtWidgets.QVBoxLayout(self.groups_window)
        layout.addWidget(new_table)
        self.groups_window.setLayout(layout)
        self.groups_window.resize(400, 400)

        # Обработчик закрытия окна
        self.groups_window.destroyed.connect(self.on_groups_window_closed)

        self.groups_window.show()  # Показываем окно после всех настроек

    def on_groups_window_closed(self):
        # Сбрасываем ссылку, когда окно закрылось
        self.groups_window = None

    def open_students_data_window(self):
        # Если окно уже существует, то сначала удаляем его
        if self.students_window is not None:
            if self.students_window.isVisible():
                self.students_window.close()  # Закрываем окно, если оно открыто
            self.students_window.deleteLater()  # Удаление окна из памяти

        # Создаем новое окно
        self.students_window = QtWidgets.QWidget()
        self.students_window.setWindowTitle("Студенты")

        new_table = QtWidgets.QTableWidget(self.students_window)
        new_table.setColumnCount(2)  # Количество столбцов
        new_table.setRowCount(211)  # Замените на актуальное количество записей
        new_table.setHorizontalHeaderLabels(["ID студента", "ФИО"])

        layout = QtWidgets.QVBoxLayout(self.students_window)
        layout.addWidget(new_table)
        self.students_window.setLayout(layout)
        self.students_window.resize(700, 350)

        # Обработчик закрытия окна
        self.students_window.destroyed.connect(self.on_students_window_closed)

        self.students_window.show()  # Показываем окно после всех настроек

    def on_students_window_closed(self):
        # Сбрасываем ссылку, когда окно закрылось
        self.students_window = None

    def open_groups_students_data_window(self):
        # Если окно уже существует, то сначала удаляем его
        if self.groups_students_window is not None:
            if self.groups_students_window.isVisible():
                self.groups_students_window.close()  # Закрываем окно, если оно открыто
            self.groups_students_window.deleteLater()  # Удаление окна из памяти

        # Создаем новое окно
        self.groups_students_window = QtWidgets.QWidget()
        self.groups_students_window.setWindowTitle("Группы-Студенты")

        new_table = QtWidgets.QTableWidget(self.groups_students_window)
        new_table.setColumnCount(2)  # Количество столбцов
        new_table.setRowCount(211)  # Замените на актуальное количество записей
        new_table.setHorizontalHeaderLabels(["ID группы", "ID студента"])

        layout = QtWidgets.QVBoxLayout(self.groups_students_window)
        layout.addWidget(new_table)
        self.groups_students_window.setLayout(layout)
        self.groups_students_window.resize(500, 350)

        # Обработчик закрытия окна
        self.groups_students_window.destroyed.connect(self.on_groups_students_window_closed)

        self.groups_students_window.show()  # Показываем окно после всех настроек

    def on_groups_students_window_closed(self):
        # Сбрасываем ссылку, когда окно закрылось
        self.groups_students_window = None

    def open_new_window(self, title):
        new_window = QtWidgets.QWidget()
        new_window.setWindowTitle(title)
        new_table = QtWidgets.QTableWidget(new_window)
        new_table.setColumnCount(8)
        new_table.setRowCount(5)
        new_table.setHorizontalHeaderLabels(
            ["ID занятия", "ID преподавателя", "ID группы", "День недели", "Корпус/онлайн", "Номер аудитории",
             "Вид занятий",
             "Время"])
        layout = QtWidgets.QVBoxLayout(new_window)
        layout.addWidget(new_table)
        new_window.setLayout(layout)
        new_window.resize(800, 600)
        new_window.show()
