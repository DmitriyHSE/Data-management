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
)
from PyQt6.QtCore import Qt
import psycopg2

# Настройки подключения (замените на ваши)
DB_USER = "postgres"
DB_PASSWORD = "admin"
DB_HOST = "127.0.0.1"
DB_PORT = "5432"


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
            cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
            # Исключаем 'Lessons_per_week' из списка колонок
            self.columns = [row[0] for row in cur.fetchall() if row[0] != "lessons_per_week"]

            layout = QFormLayout()
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
            self.reject()  # Закрываем диалог, если не удалось получить поля
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
        self.table_windows = {}  # Словарь для хранения открытых окон с таблицами
        self.setWindowTitle("Управление базами данных")
        self.setGeometry(100, 100, 300, 300)  # Задаем размеры окна

        # Создаем кнопки для создания, удаления и просмотра таблиц
        create_db_button = QPushButton("Создать базу данных", self)
        create_db_button.clicked.connect(self.create_database)

        delete_db_button = QPushButton("Удалить базу данных", self)
        delete_db_button.clicked.connect(self.delete_database)

        show_tables_button = QPushButton("Показать таблицы", self)
        show_tables_button.clicked.connect(self.show_tables)

        # Создаем компоновку
        layout = QVBoxLayout()
        layout.addWidget(create_db_button)
        layout.addWidget(delete_db_button)
        layout.addWidget(show_tables_button)

        # Создаем виджет
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)



    def get_existing_databases(self):
        """Функция для получения списка существующих баз данных."""
        conn = None
        try:
            conn = psycopg2.connect(
                user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            cur = conn.cursor()
            cur.execute(
                "SELECT datname FROM pg_database WHERE datistemplate = false;"
            )
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

            cur.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';"
            )
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
        add_data_dialog = AddDataDialog(self, table_name, db_name)
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
            columns = list(data.keys())
            values = list(data.values())
            placeholders = ', '.join(['%s'] * len(values))  # Подготавливаем placeholders

            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders});"
            cur.execute(query, values)
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

            confirm = QMessageBox.question(
                self,
                "Подтверждение",
                f"Вы уверены, что хотите очистить таблицу '{table_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirm == QMessageBox.StandardButton.Yes:
                cur.execute(f"TRUNCATE TABLE {table_name} CASCADE;")
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

            update_query = f"UPDATE {table_name} SET {update_column} = %s WHERE {where_clause}"
            cur.execute(update_query, (new_value, *primary_values))
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
                delete_query = f"DELETE FROM {table_name} WHERE {where_clause}"
                cur.execute(delete_query, primary_values)
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

    def create_db_structure(self, db_name):
        conn = None
        try:
            conn = psycopg2.connect(
                user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            conn.autocommit = True  # Для выполнения create database
            cur = conn.cursor()

            cur.execute(f"CREATE DATABASE {db_name}")
            QMessageBox.information(
                self, "Успех", f"База данных '{db_name}' успешно создана."
            )

            conn.close()  # Закрываем соединение и сразу открываем новое
            conn = psycopg2.connect(
                database=db_name,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
            )
            cur = conn.cursor()
            # SQL-запрос для создания таблиц (если их еще нет)
            create_tables_query = """
                CREATE TABLE IF NOT EXISTS Disciplines (
                    Disciple_id TEXT PRIMARY KEY,
                    Name TEXT
                );

                CREATE TABLE IF NOT EXISTS Teachers (
                    Teacher_id TEXT PRIMARY KEY,
                    FIO TEXT
                );

                CREATE TABLE IF NOT EXISTS Groups (
                    Group_id TEXT PRIMARY KEY,
                    GroupName TEXT,
                    Lessons_per_week INT DEFAULT 1
                );
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

                 CREATE TABLE IF NOT EXISTS Students (
                    Student_id TEXT PRIMARY KEY,
                    FIO TEXT
                );
               CREATE TABLE IF NOT EXISTS Group_Students (
                   Group_id TEXT REFERENCES Groups(Group_id),
                   Student_id TEXT REFERENCES Students(Student_id),
                   PRIMARY KEY(Group_id, Student_id)
               );

            """

            # SQL-запрос для создания индекса по полю Name в таблице Disciplines
            create_index_query = """
                CREATE INDEX IF NOT EXISTS idx_disciplines_name ON Disciplines(Name);
            """
            # SQL-запрос для создания триггера
            create_trigger_query = """
            CREATE OR REPLACE FUNCTION set_default_lessons_per_week()
            RETURNS TRIGGER AS $$
            BEGIN
              NEW.Lessons_per_week := 1;
              RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS set_default_lessons_per_week_trigger ON Groups;
            CREATE TRIGGER set_default_lessons_per_week_trigger
            BEFORE INSERT ON Groups
            FOR EACH ROW
            EXECUTE FUNCTION set_default_lessons_per_week();
            """

            # Выполняем SQL-запросы для создания таблиц, индекса и триггера
            cur.execute(create_tables_query)
            cur.execute(create_index_query)
            cur.execute(create_trigger_query)
            conn.commit()
            QMessageBox.information(
                self,
                "Успех",
                f"Структура базы данных '{db_name}' успешно создана.",
            )

        except psycopg2.Error as e:
            # Выводим сообщение об ошибке, если возникла проблема
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось создать базу данных:\n{e}"
            )

        finally:
            if conn:
                cur.close()
                conn.close()

    def delete_db_structure(self, db_name):
        conn = None
        try:
            conn = psycopg2.connect(
                user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            conn.autocommit = True
            cur = conn.cursor()

            cur.execute(f"DROP DATABASE {db_name}")
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
