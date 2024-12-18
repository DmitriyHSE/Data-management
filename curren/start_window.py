# -*- coding: utf-8 -*-
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(500, 433)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.host = QtWidgets.QLineEdit(self.centralwidget)
        self.host.setGeometry(QtCore.QRect(80, 110, 141, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.host.setFont(font)
        self.host.setObjectName("host")
        self.connect_button = QtWidgets.QPushButton(self.centralwidget)
        self.connect_button.setGeometry(QtCore.QRect(190, 330, 121, 41))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.connect_button.setFont(font)
        self.connect_button.setObjectName("connect_button")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(80, 80, 151, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.port = QtWidgets.QLineEdit(self.centralwidget)
        self.port.setGeometry(QtCore.QRect(80, 180, 141, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.port.setFont(font)
        self.port.setObjectName("port")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(80, 150, 151, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.database_name = QtWidgets.QLineEdit(self.centralwidget)
        self.database_name.setGeometry(QtCore.QRect(180, 260, 141, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.database_name.setFont(font)
        self.database_name.setText("")
        self.database_name.setObjectName("database_name")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(190, 230, 121, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.user = QtWidgets.QLineEdit(self.centralwidget)
        self.user.setGeometry(QtCore.QRect(270, 110, 141, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.user.setFont(font)
        self.user.setObjectName("user")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(270, 80, 151, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.password = QtWidgets.QLineEdit(self.centralwidget)
        self.password.setGeometry(QtCore.QRect(270, 180, 141, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.password.setFont(font)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setObjectName("password")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(270, 150, 151, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Start"))
        self.host.setText(_translate("MainWindow", "localhost"))
        self.connect_button.setText(_translate("MainWindow", "Начать"))
        self.label.setText(_translate("MainWindow", "Host"))
        self.port.setText(_translate("MainWindow", "5432"))
        self.label_2.setText(_translate("MainWindow", "Порт"))
        self.label_3.setText(_translate("MainWindow", "Имя базы данных"))
        self.user.setText(_translate("MainWindow", "newuser"))
        self.label_4.setText(_translate("MainWindow", "Имя пользователя"))
        self.password.setText(_translate("MainWindow", "newpass"))
        self.label_5.setText(_translate("MainWindow", "Пароль"))