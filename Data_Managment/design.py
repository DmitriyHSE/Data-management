from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def __init__(self):
        self.teachers_window = None  # Ссылка на окно преподавателей

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
            ["Lesson id", "Teacher id", "Group id", "День недели", "Корпус/онлайн", "Номер аудитории", "Вид занятий",
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
    def open_disciplines_window(self):
        self.open_new_window("Дисциплины")

    def open_groups_window(self):
        self.open_new_window("Группы")

    def open_students_window(self):
        self.open_new_window("Студенты")

    def open_groups_students_window(self):
        self.open_new_window("Группы-студенты")

    def open_teachers_window(self):
        self.open_teachers_data_window()

    def open_teachers_data_window(self):
        # Проверяем, открыто ли уже окно преподавателей
        if self.teachers_window is None:
            self.teachers_window = QtWidgets.QWidget()
            self.teachers_window.setWindowTitle("Преподаватели")

            new_table = QtWidgets.QTableWidget(self.teachers_window)
            new_table.setColumnCount(5)  # Количество столбцов
            new_table.setRowCount(120)  # Замените на актуальное количество записей
            new_table.setHorizontalHeaderLabels(
                ["Teacher id", "ФИО", "Дисциплина", "Группа", "Контакт"])

            # Пример заполнения данными
            for row in range(5):  # Замените на актуальное количество записей
                new_table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(row)))
                new_table.setItem(row, 1, QtWidgets.QTableWidgetItem("Преподаватель " + str(row)))
                new_table.setItem(row, 2, QtWidgets.QTableWidgetItem("Дисциплина " + str(row)))
                new_table.setItem(row, 3, QtWidgets.QTableWidgetItem("Группа " + str(row)))
                new_table.setItem(row, 4, QtWidgets.QTableWidgetItem("Контакт " + str(row)))

            layout = QtWidgets.QVBoxLayout(self.teachers_window)
            layout.addWidget(new_table)
            self.teachers_window.setLayout(layout)
            self.teachers_window.resize(800, 600)
            self.teachers_window.show()

            # Обработчик закрытия окна
            self.teachers_window.destroyed.connect(self.on_teachers_window_closed)

    def on_teachers_window_closed(self):
        self.teachers_window = None  # Сбрасываем ссылку, когда окно закрылось

    def open_new_window(self, title):
        new_window = QtWidgets.QWidget()
        new_window.setWindowTitle(title)
        new_table = QtWidgets.QTableWidget(new_window)
        new_table.setColumnCount(8)
        new_table.setRowCount(120)
        new_table.setHorizontalHeaderLabels(
            ["Lesson id", "Teacher id", "Group id", "День недели", "Корпус/онлайн", "Номер аудитории", "Вид занятий", "Время"])
        layout = QtWidgets.QVBoxLayout(new_window)
        layout.addWidget(new_table)
        new_window.setLayout(layout)
        new_window.resize(800, 600)
        new_window.show()  # Открываем новое окно