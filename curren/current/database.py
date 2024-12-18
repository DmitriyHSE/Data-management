import psycopg2 as ps
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class Database(object):
    def __init__(self, name, user, password, host, port):
        self.dbname = name
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connectDB("postgres")
        self.cursor.execute("SELECT * FROM pg_catalog.pg_database WHERE datname = %s", (self.dbname,))
        flag = self.cursor.fetchone()
        if flag is None:
            self.cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.dbname)))
        self.connection.close()
        self.connectDB(self.dbname)
        if flag is None:
            with self.connection.cursor() as cursor_:
                cursor_.execute(open("functions.sql", "r").read())

    def connectDB(self, name):
        self.connection = ps.connect(
            dbname=name,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
        self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cursor = self.connection.cursor()

    def delete_database(self):
        self.connectDB("postgres")
        self.cursor.execute(sql.SQL(f"DROP DATABASE {self.dbname}"))
        self.connection.close()
        del self

    def create_database(self):
        self.cursor.callproc("create_database")

    def get_all_schedule_entries(self):
        self.cursor.callproc("get_all_schedule_entries")
        return self.cursor.fetchone()[0]

    def add_schedule_entry(
        self, lesson_id, teacher_id, group_id, day_of_the_week, korpus_or_online, number_of_auditoria, type_of_lesson, time
    ):
        self.cursor.callproc(
            "add_to_schedule",
            (lesson_id, teacher_id, group_id, day_of_the_week, korpus_or_online, number_of_auditoria, type_of_lesson, time)
        )

    def find_schedule_by_teacher(self, teacher_id):
        self.cursor.callproc("find_schedule_by_teacher", (teacher_id,))
        return self.cursor.fetchone()[0]

    def find_schedule_by_day(self, day_of_the_week):
        self.cursor.callproc("find_schedule_by_day", (day_of_the_week,))
        return self.cursor.fetchone()[0]

    def update_schedule_type_of_lesson(self, new_type, lesson_id):
        self.cursor.callproc("update_type_of_lesson", (new_type, lesson_id))

    def delete_schedule_entry(self, lesson_id):
        self.cursor.callproc("delete_schedule_entry", (lesson_id,))

    def clear_schedule(self):
        self.cursor.callproc("clear_schedule")

    def disconnect(self):
        self.connection.close()
