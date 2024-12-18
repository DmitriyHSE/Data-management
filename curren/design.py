from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.schedule_table = QtWidgets.QTableWidget(self.centralwidget)
        self.schedule_table.setObjectName("schedule_table")
        self.schedule_table.setColumnCount(8)
        self.schedule_table.setRowCount(5)  # Это нужно изменить в зависимости от количества записей в базе данных
        self.schedule_table.setHorizontalHeaderLabels(
            ["Lesson id", "Teacher id", "Group id", "День недели", "Корпус/онлайн", "Номер аудитории", "Вид занятий",
             "Время"])
        self.schedule_table.verticalHeader().setVisible(False)
        self.schedule_table.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)  # Разрешаем редактирование

        # Connect button
        self.connect_button = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.connect_button.setFont(font)
        self.connect_button.setObjectName("connect_button")

        # Delete database button
        self.delete_database_button = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.delete_database_button.setFont(font)
        self.delete_database_button.setObjectName("delete_database_button")

        # Add data button
        self.add_data_button = QtWidgets.QPushButton(self.centralwidget)  # New button
        font = QtGui.QFont()
        font.setPointSize(9)
        self.add_data_button.setFont(font)
        self.add_data_button.setObjectName("add_data_button")  # New object name


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

        button_layout = QtWidgets.QHBoxLayout()  # Новый layout для кнопок
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.delete_database_button)
        button_layout.addWidget(self.add_data_button) # Добавлена новая кнопка

        main_layout.addLayout(title_layout)
        main_layout.addWidget(self.schedule_table)
        main_layout.addLayout(button_layout)  # Добавляем layout с кнопками
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Расписание"))
        self.connect_button.setText(_translate("MainWindow", "Подключиться к базе данных"))
        self.delete_database_button.setText(_translate("MainWindow", "Удалить базу данных"))
        self.add_data_button.setText(_translate("MainWindow", "Добавить данные")) # Текст для новой кнопки