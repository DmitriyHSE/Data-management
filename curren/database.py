import psycopg2 as ps
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import name, user, password, host  # Убедитесь, что config.py содержит корректные параметры подключения

class Database:
    def __init__(self, name, user, password, host, port=5432):
        self.dbname = name.strip()
        self.user = user.strip()
        self.password = password.strip()
        self.host = host.strip()
        self.port = port

        # Подключение к базе данных postgres для создания новой базы данных
        self.connectDB("postgres")
        self.cursor.execute("SELECT * FROM pg_catalog.pg_database WHERE datname = %s", (self.dbname,))
        flag = self.cursor.fetchone()

        # Создание базы данных, если её не существует
        if flag is None:
            print(f"Database '{self.dbname}' not found. Creating...")
            self.cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.dbname)))

        self.connection.close()

        # Подключение к созданной (или существующей) базе данных
        self.connectDB(self.dbname)

        # Выполнение SQL-функций, если база данных была создана
        if flag is None:
            print(f"Initializing database '{self.dbname}' with functions.sql...")
            with self.connection.cursor() as cursor_:
                try:
                    with open("functions.sql", "r", encoding="utf-8") as file:
                        cursor_.execute(file.read())
                    self.connection.commit()
                except FileNotFoundError:
                    print("File 'functions.sql' not found. Please ensure it exists in the working directory.")
                except Exception as e:
                    print(f"Error while executing 'functions.sql': {e}")

    def connectDB(self, name):
        """Подключение к базе данных с заданным именем."""
        try:
            print(f"Connecting to database: {name}")
            self.connection = ps.connect(
                dbname=name,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                options="-c client_encoding=UTF8"
            )
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cursor = self.connection.cursor()
            print(f"Connected to database: {name}")
        except ps.OperationalError as e:
            print(f"Error connecting to database '{name}': {e}")
            raise

    def create_database(self):
        """Пример вызова функции create_database (если она определена в functions.sql)."""
        try:
            print("Calling stored procedure 'create_database'...")
            self.cursor.callproc("create_database")
            print("Procedure 'create_database' executed successfully.")
        except Exception as e:
            print(f"Error calling 'create_database': {e}")
    def delete_database(self):
        self.connectDB("postgres")
        self.cursor = self.connection.cursor()
        self.cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(self.dbname)))
        self.connection.close()
    def get_schedule(self):
        self.cursor.callproc("get_schedule")
        return self.cursor.fetchone()[0]
    def add_to_schedule(self, lesson_id,teacher_id,group_id,day_of_the_week,korpus,number_of_auditoria,type_of_lesson,lesson_time):
        self.cursor.callproc("add_to_schedule", (lesson_id,teacher_id,group_id,day_of_the_week,korpus,number_of_auditoria,type_of_lesson,lesson_time))

    def add_to_disciplines(self, discipline_id, title):
        self.cursor.callproc("add_to_disciplines", (discipline_id, title))

    def update_schedule_by_lesson_id(self,new_lesson_id,lesson_id):
        self.cursor.callproc("update_schedule_lesson_id", (new_lesson_id,lesson_id,))

    def update_schedule_by_korpus(self,new_korpus,lesson_id):
        self.cursor.callproc("update_schedule_korpus", (new_korpus,lesson_id,))

    def update_schedule_by_teacher_id(self,new_teacher_id,lesson_id):
        self.cursor.callproc("update_schedule_teacher_id", (new_teacher_id,lesson_id,))

    def update_schedule_by_korpus(self,new_day_of_the_week,lesson_id):
        self.cursor.callproc("update_schedule_day_of_the_week", (new_day_of_the_week,lesson_id,))

    def update_schedule_by_korpus(self,new_number_of_auditoria,lesson_id):
        self.cursor.callproc("update_schedule_number_of_auditoria", (new_number_of_auditoria,lesson_id,))

    def update_schedule_by_korpus(self,new_type_of_lesson,lesson_id):
        self.cursor.callproc("update_type_of_lesson", (new_type_of_lesson,lesson_id,))
