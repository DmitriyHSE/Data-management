import sys
from PyQt5 import QtWidgets
from gui import main_window


def main():
    app = QtWidgets.QApplication([])
    application = main_window()
    application.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()