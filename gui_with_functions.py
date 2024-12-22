import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QLineEdit,
    QLabel,
    QDialog,
    QDialogButtonBox,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QCheckBox,
    QFormLayout,
    QMenu,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt
import psycopg2

# Настройки подключения (замените на ваши)
DB_USER = "user1"
DB_PASSWORD = "1"
DB_HOST = "127.0.0.1"
DB_PORT = "5432"

class Database:
    def __init__(self, name, user, password, host, port=5432):
        self.dbname = name.strip()
        self.user = user.strip()
        self.password = password.strip()
        self.host = host.strip()
        self.port = port
        self.connection = None
        self.cursor = None

    def connectDB(self):
        try:
            self.connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                options="-c client_encoding=UTF8"
            )
            self.cursor = self.connection.cursor()

        except psycopg2.OperationalError as e:
            print(f"Error connecting to database '{self.dbname}': {e}")
            raise

    def close_connection(self):
        if self.connection:
            if self.cursor:
               self.cursor.close()
            self.connection.close()

    def get_all_column_names(self, selected_table):
        try:
            self.cursor.execute("SELECT * FROM public.get_column_names(%s);", (selected_table,))
            result = self.cursor.fetchall()
            if result:
                return [row[0] for row in result]
            return None
        except Exception as e:
            print(f"Error calling get_column_names: {e}")
            return None
class SearchDialog(QDialog):
    def __init__(self, parent=None, db_name=None, tables=None):
        super().__init__(parent)
        self.setWindowTitle("Поиск в таблице")
        self.db_name = db_name

        self.table_label = QLabel("Выберите таблицу:")
        self.table_combo = QComboBox()
        if tables:
            self.table_combo.addItems(tables)

        self.column_label = QLabel("Выберите столбец:")
        self.column_combo = QComboBox()

        if tables:
            self.table_combo.setCurrentIndex(0)  # Устанавливаем первый элемент
            self.update_columns()  # Вызываем update_columns после инициализации table_combo

        self.table_combo.currentIndexChanged.connect(self.update_columns)

        self.search_label = QLabel("Введите значение для поиска:")
        self.search_input = QLineEdit()

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.table_label)
        layout.addWidget(self.table_combo)
        layout.addWidget(self.column_label)
        layout.addWidget(self.column_combo)
        layout.addWidget(self.search_label)
        layout.addWidget(self.search_input)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_search_text(self):
        return self.search_input.text().strip()

    def get_selected_table(self):
        return self.table_combo.currentText()

    def get_selected_column(self):
        return self.column_combo.currentText()

    def update_columns(self):
        conn = None
        try:
            conn = psycopg2.connect(
                database=self.db_name, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            cur = conn.cursor()
            with open("functions.sql", "r") as file:
                sql_script = file.read()
            cur.execute(sql_script)
            selected_table = self.table_combo.currentText()
            #cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{selected_table}'")
            cur.execute("SELECT * FROM public.get_column_names(%s);", (selected_table,))
            columns = [row[0] for row in cur.fetchall()]
            text_columns = []
            for column in columns:
                #cur.execute(
                 #   f"SELECT data_type, is_nullable FROM information_schema.columns WHERE table_name = '{selected_table}' and column_name = '{column}';")
                cur.execute("SELECT * FROM public.get_column_info(%s, %s);", (selected_table, column))
                data_type, is_nullable = cur.fetchone()
                if (data_type == 'text' or data_type == 'character varying') and is_nullable == 'YES':
                    cur.execute("SELECT public.check_primary_key(%s, %s);", (selected_table, column))
                    is_primary = cur.fetchone()[0]
                    if is_primary == 0:
                        text_columns.append(column)
            self.column_combo.clear()
            self.column_combo.addItems(text_columns)
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить поля таблицы: {e}")
        finally:
            if conn:
                cur.close()
                conn.close()


class CreateDatabaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создать базу данных")

        self.db_name_label = QLabel("Имя базы данных:", self)
        self.db_name_input = QLineEdit(self)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.db_name_label)
        layout.addWidget(self.db_name_input)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_db_name(self):
        return self.db_name_input.text().strip()


class DeleteDatabaseDialog(QDialog):
    def __init__(self, parent=None, db_names=None):
        super().__init__(parent)
        self.setWindowTitle("Удалить базу данных")

        self.db_select_label = QLabel("Выберите базу данных для удаления:", self)
        self.db_select_combo = QComboBox(self)
        if db_names:
            self.db_select_combo.addItems(db_names)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.db_select_label)
        layout.addWidget(self.db_select_combo)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_selected_db(self):
        return self.db_select_combo.currentText()


class SelectDatabaseDialog(QDialog):
    def __init__(self, parent=None, db_names=None):
        super().__init__(parent)
        self.setWindowTitle("Выбрать базу данных")

        self.db_select_label = QLabel("Выберите базу данных:", self)
        self.db_select_combo = QComboBox(self)
        if db_names:
            self.db_select_combo.addItems(db_names)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.db_select_label)
        layout.addWidget(self.db_select_combo)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_selected_db(self):
        return self.db_select_combo.currentText()


class AddDataDialog(QDialog):
    def __init__(self, parent=None, table_name=None, db_name=None):
        super().__init__(parent)
        self.setWindowTitle(f"Добавить данные в таблицу '{table_name}'")
        self.table_name = table_name
        self.db_name = db_name
        self.field_inputs = {}

        self.conn = None
        try:
            self.conn = psycopg2.connect(
                database=db_name, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            cur = self.conn.cursor()
            with open("functions.sql", "r") as file:
                sql_script = file.read()
            cur.execute(sql_script)
            print("Робит11")
            cur.execute("SELECT public.get_column_names(%s);", (table_name,))
            print("Робит22")
            #cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
            self.columns = [row[0] for row in cur.fetchall() if row[0] != "lessons_per_week"]
            layout = QFormLayout()
            print(len(self.columns))
            for column in self.columns:
                label = QLabel(column)
                input_field = QLineEdit()
                layout.addRow(label, input_field)
                self.field_inputs[column] = input_field
            button_box = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
            button_box.accepted.connect(self.accept)
            button_box.rejected.connect(self.reject)
            layout.addRow(button_box)
            self.setLayout(layout)


        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить поля таблицы: {e}")
            self.reject()  # Закрываем диалог если не удалось получить поля
        finally:
            if self.conn:
                cur.close()
                self.conn.close()

    def get_data(self):
        data = {}
        for column, input_field in self.field_inputs.items():
            data[column] = input_field.text().strip()
        return data


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("База данных")
        self.setGeometry(100, 100, 800, 600)
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.table_windows = {}

        self.create_db_button = QPushButton("Создать базу данных", self)
        self.create_db_button.clicked.connect(self.create_db_dialog)
        self.layout.addWidget(self.create_db_button)

        self.delete_db_button = QPushButton("Удалить базу данных", self)
        self.delete_db_button.clicked.connect(self.delete_db_dialog)
        self.layout.addWidget(self.delete_db_button)

        self.show_tables_button = QPushButton("Показать таблицы", self)
        self.show_tables_button.clicked.connect(self.show_tables_dialog)
        self.layout.addWidget(self.show_tables_button)

        search_db_button = QPushButton("Поиск", self)
        search_db_button.clicked.connect(self.search_data)
        self.layout.addWidget(search_db_button)

        delete_search_button = QPushButton("Удалить по поиску", self)
        delete_search_button.clicked.connect(self.delete_by_search)
        self.layout.addWidget(delete_search_button)

    def create_db_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Создать базу данных")

        db_name_label = QLabel("Имя базы данных:")
        db_name_input = QLineEdit()

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(lambda: self.create_db_structure(db_name_input.text().strip(), dialog))
        button_box.rejected.connect(dialog.reject)
        layout = QVBoxLayout()
        layout.addWidget(db_name_label)
        layout.addWidget(db_name_input)
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        dialog.exec()

    def delete_db_dialog(self):
        db_names = self.get_existing_databases()
        if not db_names:
            QMessageBox.warning(
                self, "Предупреждение", "Нет доступных баз данных для удаления."
            )
            return
        select_db_dialog = SelectDatabaseDialog(self, db_names=db_names)
        result = select_db_dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            db_name = select_db_dialog.get_selected_db()
            if db_name:
                confirm = QMessageBox.question(
                    self,
                    "Подтверждение",
                    f"Вы уверены, что хотите удалить базу данных '{db_name}'?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if confirm == QMessageBox.StandardButton.Yes:
                    self.delete_db_structure(db_name)

    def show_tables_dialog(self):  # Исправлен вызов метода
        print("1")
        db_names = self.get_existing_databases()
        print("2")
        if not db_names:
            QMessageBox.warning(
                self, "Предупреждение", "Нет доступных баз данных для отображения."
            )
            return
        select_db_dialog = SelectDatabaseDialog(self, db_names=db_names)
        result = select_db_dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            db_name = select_db_dialog.get_selected_db()
            if db_name:
                self.show_tables_content(db_name)

    def get_existing_databases(self):
        """Функция для получения списка существующих баз данных."""
        conn = None
        try:
            conn = psycopg2.connect(
                database="postgres", user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            cur = conn.cursor()
            with open("functions.sql", "r") as file:
                sql_script = file.read()
            cur.execute(sql_script)
            cur.callproc("get_databases")
            db_names = [row[0] for row in cur.fetchall()]
            return db_names
        except psycopg2.Error as e:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось получить список баз данных:\n{e}"
            )
            return []
        finally:
            if conn:
                cur.close()
                conn.close()

    def create_database(self):
        create_db_dialog = CreateDatabaseDialog(self)
        result = create_db_dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            db_name = create_db_dialog.get_db_name()
            if db_name:
                self.create_db_structure(db_name)
            else:
                QMessageBox.warning(
                    self, "Предупреждение", "Имя базы данных не может быть пустым."
                )

    def delete_database(self):
        db_names = self.get_existing_databases()
        if not db_names:
            QMessageBox.warning(
                self, "Предупреждение", "Нет доступных баз данных для удаления."
            )
            return

        delete_db_dialog = DeleteDatabaseDialog(self, db_names=db_names)
        result = delete_db_dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            db_name = delete_db_dialog.get_selected_db()
            if db_name:
                self.delete_db_structure(db_name)
            else:
                QMessageBox.warning(
                    self, "Предупреждение", "База данных для удаления не выбрана."
                )

    def show_tables(self):
        db_names = self.get_existing_databases()
        if not db_names:
            QMessageBox.warning(
                self, "Предупреждение", "Нет доступных баз данных для просмотра."
            )
            return

        select_db_dialog = SelectDatabaseDialog(self, db_names=db_names)
        result = select_db_dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            db_name = select_db_dialog.get_selected_db()
            if db_name:
                self.show_tables_content(db_name)
            else:
                QMessageBox.warning(
                    self, "Предупреждение", "База данных для просмотра не выбрана."
                )

    def show_tables_content(self, db_name):
        conn = None
        try:
            conn = psycopg2.connect(
                database=db_name, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            cur = conn.cursor()
            with open("functions.sql", "r") as file:
                sql_script = file.read()
            cur.execute(sql_script)
            cur.callproc("get_public_tables")
            tables = [row[0] for row in cur.fetchall()]

            if not tables:
                QMessageBox.information(
                    self, "Информация", f"В базе данных '{db_name}' нет таблиц."
                )
                return

            tabs = QTabWidget(self)
            tabs.currentChanged.connect(
                lambda index: self.on_tab_changed(index, tabs, db_name))  # Подключение обработчика

            for table in tables:
                table_widget = QTableWidget()
                self.update_table_data(table_widget, table, db_name)
                table_widget.itemChanged.connect(
                    lambda item, t=table, tw=table_widget: self.cell_changed(item, t, db_name, tw))
                table_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                table_widget.customContextMenuRequested.connect(
                    lambda pos, t=table, tw=table_widget: self.show_context_menu(pos, t, db_name, tw))

                clear_table_button = QPushButton(f"Очистить таблицу {table}")
                clear_table_button.clicked.connect(
                    lambda checked, t=table, tw=table_widget: self.clear_table(t, db_name, tw))

                add_data_button = QPushButton(f"Добавить в таблицу {table}")
                add_data_button.clicked.connect(lambda checked, t=table, tw=table_widget: self.add_data(t, db_name, tw))

                layout = QVBoxLayout()
                layout.addWidget(table_widget)
                layout.addWidget(clear_table_button)
                layout.addWidget(add_data_button)

                table_widget_container = QWidget()
                table_widget_container.setLayout(layout)
                tabs.addTab(table_widget_container, table)

            table_window = QMainWindow(self)
            table_window.setWindowTitle(f"Содержимое таблиц '{db_name}'")
            table_window.setCentralWidget(tabs)
            table_window.setGeometry(100, 100, 800, 600)
            table_window.show()

            self.table_windows[db_name] = table_window

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось отобразить таблицы: {e}")
        finally:
            if conn:
                cur.close()
                conn.close()

    def add_data(self, table_name, db_name, table_widget):
        print("Add data1")
        add_data_dialog = AddDataDialog(self, table_name, db_name)
        print("add data2")
        result = add_data_dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            data = add_data_dialog.get_data()
            if data:
                self.insert_data_into_table(table_name, db_name, data, table_widget)
            else:
                QMessageBox.warning(self, "Предупреждение", "Не удалось получить данные")


    def insert_data_into_table(self, table_name, db_name, data, table_widget):
        conn = None
        try:
            conn = psycopg2.connect(
                database=db_name, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            cur = conn.cursor()
            #with open("functions.sql", "r") as file:
             #   sql_script = file.read()
            #cur.execute(sql_script)
            columns = list(data.keys())
            values = list(data.values())
            placeholders = ', '.join(['%s'] * len(values))  # Подготавливаем placeholders
            print("Yes99")
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders});"
            cur.execute(query, values)
            print("Yes991")
            conn.commit()
            QMessageBox.information(self, "Успех", f"Данные успешно добавлены в таблицу '{table_name}'.")
            self.update_table_data(table_widget, table_name, db_name)

        except psycopg2.Error as e:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось добавить данные в таблицу: {e}"
            )

        finally:
            if conn:
                cur.close()
                conn.close()

    def clear_table(self, table_name, db_name, table_widget):
        conn = None
        try:
            conn = psycopg2.connect(
                database=db_name, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            cur = conn.cursor()
            with open("functions.sql", "r") as file:
                sql_script = file.read()
            cur.execute(sql_script)
            confirm = QMessageBox.question(
                self,
                "Подтверждение",
                f"Вы уверены, что хотите очистить таблицу '{table_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirm == QMessageBox.StandardButton.Yes:
                cur.callproc("truncate_table",(table_name,))
                #cur.execute(f"TRUNCATE TABLE {table_name} CASCADE;")
                conn.commit()
                QMessageBox.information(self, "Успех", f"Таблица '{table_name}' очищена.")

                # Обновляем данные в виджете
                self.update_table_data(table_widget, table_name, db_name)

        except psycopg2.Error as e:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось очистить таблицу: {e}"
            )
        finally:
            if conn:
                cur.close()
                conn.close()

    def cell_changed(self, item, table_name, db_name, table_widget):
        conn = None
        try:
            conn = psycopg2.connect(
                database=db_name, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            cur = conn.cursor()
            with open("functions.sql", "r") as file:
                sql_script = file.read()
            cur.execute(sql_script)
            row = item.row()
            col = item.column()
            new_value = item.text()
            cur.execute(f"SELECT * FROM {table_name}")
            rows = cur.fetchall()
            headers = [desc[0] for desc in cur.description]

            if not rows:
                QMessageBox.critical(self, "Ошибка", f"Таблица '{table_name}' пуста.")
                return
            if row >= len(rows):
                QMessageBox.critical(self, "Ошибка", f"Выбрана несуществующая строка.")
                return

            primary_keys = self.get_primary_keys(table_name, db_name)
            if not primary_keys:
                QMessageBox.critical(self, "Ошибка", f"Не удалось получить первичные ключи таблицы {table_name}.")
                return

            where_clause = ' AND '.join([f"{key} = %s" for key in primary_keys])
            primary_values = [str(rows[row][headers.index(key)]) for key in primary_keys]
            update_column = headers[col]

            # Проверка на изменение
            if str(rows[row][col]) == new_value:
                return

            #update_query = f"UPDATE {table_name} SET {update_column} = %s WHERE {where_clause}"
            #cur.execute(update_query, (new_value, *primary_values))
            cur.execute("SELECT public.update_table_record(%s, %s, %s, %s, %s);",
                        (table_name, primary_keys, primary_values, update_column, new_value))
            conn.commit()
            QMessageBox.information(self, "Успех", "Ячейка успешно обновлена.")
            self.update_table_data(table_widget, table_name, db_name)

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить ячейку: {e}")
        finally:
            if conn:
                cur.close()
                conn.close()

    def show_context_menu(self, position, table_name, db_name,
                          table_widget):  # Исправлено - table_widget теперь используется в функции
        menu = QMenu(self)
        delete_action = menu.addAction("Удалить строку")

        # Выделяем строку перед показом меню
        row = table_widget.rowAt(position.y())
        table_widget.selectRow(row)

        action = menu.exec(table_widget.viewport().mapToGlobal(position))
        if action == delete_action:
            self.delete_row(table_name, db_name, table_widget, position)

    def delete_row(self, table_name, db_name, table_widget, position):
        conn = None
        try:
            conn = psycopg2.connect(
                database=db_name, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            cur = conn.cursor()
            with open("functions.sql", "r") as file:
                sql_script = file.read()
            cur.execute(sql_script)
            row = table_widget.rowAt(position.y())  # Получаем номер строки

            cur.execute(f"SELECT * FROM {table_name}")
            rows = cur.fetchall()
            headers = [desc[0] for desc in cur.description]

            if not rows:
                QMessageBox.critical(self, "Ошибка", f"Таблица '{table_name}' пуста.")
                return
            if row >= len(rows) or row < 0:
                QMessageBox.critical(self, "Ошибка", f"Выбрана несуществующая строка.")
                return

            primary_keys = self.get_primary_keys(table_name, db_name)
            if not primary_keys:
                QMessageBox.critical(self, "Ошибка", f"Не удалось получить первичные ключи таблицы {table_name}.")
                return

            where_clause = ' AND '.join([f"{key} = %s" for key in primary_keys])
            primary_values = [str(rows[row][headers.index(key)]) for key in primary_keys]

            confirm = QMessageBox.question(
                self,
                "Подтверждение",
                f"Вы уверены, что хотите удалить строку из таблицы '{table_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirm == QMessageBox.StandardButton.Yes:
                #delete_query = f"DELETE FROM {table_name} WHERE {where_clause}"
                #cur.execute(delete_query, primary_values)
                cur.execute("SELECT public.delete_table_record(%s, %s, %s);",
                            (table_name, primary_keys, primary_values))
                conn.commit()
                QMessageBox.information(self, "Успех", "Строка успешно удалена.")
                self.update_table_data(table_widget, table_name, db_name)

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить строку: {e}")
        finally:
            if conn:
                cur.close()
                conn.close()

    def get_primary_keys(self, table_name, db_name):
        conn = None
        try:
            conn = psycopg2.connect(
                database=db_name, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            cur = conn.cursor()
            #with open("functions.sql", "r") as file:
             #   sql_script = file.read()
            #cur.execute(sql_script)
            #cur.execute("SELECT public.get_primary_key_columns(%s);", (table_name,))
            cur.execute(f"""
              SELECT kcu.column_name
              FROM information_schema.table_constraints AS tc
              JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
              AND tc.table_name = kcu.table_name
              WHERE tc.constraint_type = 'PRIMARY KEY'
              AND tc.table_name = '{table_name}';
              """)
            primary_keys = [row[0] for row in cur.fetchall()]
            return primary_keys

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить первичные ключи: {e}")
            return []
        finally:
            if conn:
                cur.close()
                conn.close()

    def on_tab_changed(self, index, tabs, db_name):
        # Получаем имя вкладки (таблицы) по индексу
        table_name = tabs.tabText(index)
        if table_name == "groups":  # Проверяем, что это вкладка "groups"
            widget_container = tabs.widget(index)  # Получаем виджет текущей вкладки
            table_widget = widget_container.layout().itemAt(0).widget()  # Получаем QTableWidget
            self.update_table_data(table_widget, table_name, db_name)  # Обновляем данные
    def update_table_data(self, table_widget, table_name, db_name):
        conn = None
        try:
            conn = psycopg2.connect(
                database=db_name, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            cur = conn.cursor()

            # Обновление поля lessons_per_week в таблице Groups
            if table_name == "schedule":
                cur.execute("""
                    UPDATE groups
                    SET lessons_per_week = (
                        SELECT COUNT(*)
                        FROM schedule
                        WHERE schedule.group_id = groups.group_id
                    );
                """)
                conn.commit()

            # Получение данных для отображения в таблице
            cur.execute(f"SELECT * FROM {table_name}")
            rows = cur.fetchall()
            headers = [desc[0] for desc in cur.description]

            table_widget.setColumnCount(len(headers))
            table_widget.setHorizontalHeaderLabels(headers)
            table_widget.setRowCount(len(rows))

            for row_idx, row_data in enumerate(rows):
                for col_idx, cell_data in enumerate(row_data):
                    item = QTableWidgetItem(str(cell_data))

                    # Делаем ячейки lessons_per_week неизменяемыми
                    if headers[col_idx] == "lessons_per_week":
                        item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)

                    table_widget.setItem(row_idx, col_idx, item)

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить данные: {e}")
        finally:
            if conn:
                cur.close()
                conn.close()

    def search_data(self):
        db_names = self.get_existing_databases()
        if not db_names:
            QMessageBox.warning(
                self, "Предупреждение", "Нет доступных баз данных для поиска."
            )
            return

        select_db_dialog = SelectDatabaseDialog(self, db_names=db_names)
        result = select_db_dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            db_name = select_db_dialog.get_selected_db()
            if db_name:
                self.perform_search(db_name)
            else:
                QMessageBox.warning(
                    self, "Предупреждение", "База данных для поиска не выбрана."
                )

    def perform_search(self, db_name):
        conn = None
        try:
            conn = psycopg2.connect(
                database=db_name, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            cur = conn.cursor()

            cur.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';")
            tables = [row[0] for row in cur.fetchall()]
            search_dialog = SearchDialog(self, db_name, tables)
            result = search_dialog.exec()
            if result == QDialog.DialogCode.Accepted:
                search_text = search_dialog.get_search_text()
                table_name = search_dialog.get_selected_table()
                selected_column = search_dialog.get_selected_column()
                if search_text and table_name and selected_column:
                    self.show_search_results(db_name, table_name, search_text, selected_column)
                else:
                    QMessageBox.warning(self, "Предупреждение",
                                        "Поисковой запрос, таблица или столбец не могут быть пустыми.")

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить поиск: {e}")
        finally:
            if conn:
                cur.close()
                conn.close()

    def show_search_results(self, db_name, table_name, search_text, selected_column):
        conn = None
        try:
            conn = psycopg2.connect(
                database=db_name, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM {table_name} WHERE {selected_column} LIKE %s", ('%' + search_text + '%',))
            rows = cur.fetchall()
            headers = [desc[0] for desc in cur.description]
            if not rows:
                QMessageBox.information(self, "Информация",
                                        f"По запросу '{search_text}' в таблице '{table_name}' по столбцу '{selected_column}' ничего не найдено.")
                return

            table_widget = QTableWidget()
            table_widget.setColumnCount(len(headers))
            table_widget.setHorizontalHeaderLabels(headers)
            table_widget.setRowCount(len(rows))

            for row_idx, row_data in enumerate(rows):
                for col_idx, cell_data in enumerate(row_data):
                    item = QTableWidgetItem(str(cell_data))
                    table_widget.setItem(row_idx, col_idx, item)

            search_window = QMainWindow(self)
            search_window.setWindowTitle(
                f"Результаты поиска '{search_text}' в таблице '{table_name}' по столбцу '{selected_column}'")
            search_window.setCentralWidget(table_widget)
            search_window.setGeometry(100, 100, 600, 400)
            search_window.show()

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить поиск: {e}")
        finally:
            if conn:
                cur.close()
                conn.close()

    def delete_by_search(self):
        db_names = self.get_existing_databases()
        if not db_names:
            QMessageBox.warning(
                self, "Предупреждение", "Нет доступных баз данных для удаления по поиску."
            )
            return
        select_db_dialog = SelectDatabaseDialog(self, db_names=db_names)
        result = select_db_dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            db_name = select_db_dialog.get_selected_db()
            if db_name:
                self.perform_delete_by_search(db_name)
            else:
                QMessageBox.warning(
                    self, "Предупреждение", "База данных для удаления по поиску не выбрана."
                )

    def perform_delete_by_search(self, db_name):
        conn = None
        try:
            conn = psycopg2.connect(
                database=db_name, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            cur = conn.cursor()

            cur.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';")
            tables = [row[0] for row in cur.fetchall()]
            search_dialog = SearchDialog(self, db_name, tables)
            result = search_dialog.exec()
            if result == QDialog.DialogCode.Accepted:
                search_text = search_dialog.get_search_text()
                table_name = search_dialog.get_selected_table()
                selected_column = search_dialog.get_selected_column()
                if search_text and table_name and selected_column:
                    self.delete_search_results(db_name, table_name, search_text, selected_column)
                else:
                    QMessageBox.warning(self, "Предупреждение",
                                        "Поисковой запрос, таблица или столбец не могут быть пустыми.")

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить поиск для удаления: {e}")
        finally:
            if conn:
                cur.close()
                conn.close()

    def delete_search_results(self, db_name, table_name, search_text, selected_column):
        conn = None
        try:
            conn = psycopg2.connect(
                database=db_name, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM {table_name} WHERE {selected_column} LIKE %s", ('%' + search_text + '%',))
            rows = cur.fetchall()
            if not rows:
                QMessageBox.information(self, "Информация",
                                        f"По запросу '{search_text}' в таблице '{table_name}' по столбцу '{selected_column}' ничего не найдено.")
                return

            confirm = QMessageBox.question(
                self,
                "Подтверждение",
                f"Вы уверены, что хотите удалить все строки, где столбец '{selected_column}' содержит '{search_text}' в таблице '{table_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if confirm == QMessageBox.StandardButton.Yes:
                cur.execute(f"DELETE FROM {table_name} WHERE {selected_column} LIKE %s", ('%' + search_text + '%',))
                conn.commit()
                QMessageBox.information(self, "Успех",
                                        f"Были удалены все строки, где столбец '{selected_column}' содержал '{search_text}' из таблицы '{table_name}'.")

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить поиск и удаление: {e}")
        finally:
            if conn:
                cur.close()
                conn.close()

    def create_db_structure(self, db_name, dialog):
        if not db_name:
            QMessageBox.warning(self, "Предупреждение", "Имя базы данных не может быть пустым.")
            return
        conn = None
        try:
            conn = psycopg2.connect(
                database="postgres",user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute(f"CREATE DATABASE {db_name}")
            self.create_tables(db_name)
            QMessageBox.information(self, "Успех", f"База данных '{db_name}' успешно создана.")
            dialog.accept()
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать базу данных: {e}")
        finally:
            if conn:
                cur.close()
                conn.close()

    def create_tables(self, db_name):
        conn = None
        try:
            conn = psycopg2.connect(
                database=db_name, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            cur = conn.cursor()
            cur.execute("""
              CREATE TABLE IF NOT EXISTS Disciplines (
                    Disciple_id TEXT PRIMARY KEY,
                    Name TEXT
                );
           """)
            cur.execute("""
              CREATE TABLE IF NOT EXISTS Teachers (
                    Teacher_id TEXT PRIMARY KEY,
                    FIO TEXT
                );
            """)
            cur.execute("""
              CREATE TABLE IF NOT EXISTS Groups (
                    Group_id TEXT PRIMARY KEY,
                    GroupName TEXT,
                    Lessons_per_week INT DEFAULT 0
                );
           """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Schedule (
                    Lesson_id TEXT PRIMARY KEY,
                    Teacher_id TEXT REFERENCES Teachers(Teacher_id),
                    Group_id TEXT REFERENCES Groups(Group_id),
                    DayOfWeek TEXT,
                    Building_online TEXT,
                    RoomNumber TEXT,
                    LessonType TEXT,
                    LessonTime TEXT
                );
            """)
            cur.execute("""
               CREATE TABLE IF NOT EXISTS Students (
                    Student_id TEXT PRIMARY KEY,
                    FIO TEXT
                );
            """)
            cur.execute("""
              CREATE TABLE IF NOT EXISTS Group_Students (
                   Group_id TEXT REFERENCES Groups(Group_id),
                   Student_id TEXT REFERENCES Students(Student_id),
                   PRIMARY KEY(Group_id, Student_id)
               );
            """)
            cur.execute(
                "CREATE INDEX idx_schedule_group_id ON Schedule(Group_id)")  # Создаём индекс на Schedule(group_id)
            cur.execute("""
           CREATE OR REPLACE FUNCTION set_lessons_per_week() RETURNS TRIGGER AS $$
              BEGIN
                  UPDATE Groups SET lessons_per_week = (
                        SELECT COUNT(*)
                        FROM Schedule
                        WHERE group_id = NEW.group_id
                    )
                  WHERE group_id = NEW.group_id;
                RETURN NEW;
              END;
           $$ LANGUAGE plpgsql;

           CREATE TRIGGER schedule_changes
              AFTER INSERT OR UPDATE OR DELETE ON Schedule
              FOR EACH ROW
             EXECUTE FUNCTION set_lessons_per_week();
          """)
            conn.commit()
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать таблицы: {e}")
        finally:
            if conn:
                cur.close()
                conn.close()

        def delete_db_structure(self, db_name):
        conn = None
        try:
            conn = psycopg2.connect(
                database="postgres", user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            conn.autocommit = True
            cur = conn.cursor()
            with open("functions.sql", "r") as file:
                sql_script = file.read()
            cur.execute(sql_script)
            cur.execute("SELECT public.drop_database_command(%s)", (db_name,))
            drop_command = cur.fetchone()[0] # Получаем SQL запрос из процедуры
            cur.execute(drop_command) #Выполняем полученную команду

            QMessageBox.information(self, "Успех", f"База данных '{db_name}' успешно удалена.")

            # Закрываем окно с таблицами если оно открыто
            if db_name in self.table_windows:
                self.table_windows[db_name].close()
                del self.table_windows[db_name]

        except psycopg2.Error as e:
            # Выводим сообщение об ошибке, если возникла проблема
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить базу данных:\n{e}")
        finally:
            if conn:
                cur.close()
                conn.close()
#the end
