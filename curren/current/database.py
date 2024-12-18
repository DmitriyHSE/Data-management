import psycopg2 as ps
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class Database:
    def __init__(self, name, user, password, host, port):
        self.dbname = name
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connectDB("postgres")
        self.createDatabase()
        self.closeDB()
        self.connectDB(self.dbname)
        self.createScheduleTableAndFunctions()

    def connectDB(self, dbname):
        """Connect to a specific database."""
        self.conn = ps.connect(
            dbname=dbname, user=self.user, password=self.password, host=self.host, port=self.port
        )
        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cursor = self.conn.cursor()

    def closeDB(self):
        """Close the connection to the database."""
        self.cursor.close()
        self.conn.close()

    def createDatabase(self):
        """Create the database if it doesn't already exist."""
        self.cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (self.dbname,))
        if not self.cursor.fetchone():
            self.cursor.execute(f"CREATE DATABASE {self.dbname}")

    def createScheduleTableAndFunctions(self):
        """Load the SQL file to create the table and functions."""
        with open("functions.sql", "r", encoding="utf-8") as f:
            sql_code = f.read()
            self.cursor.execute(sql_code)

    def add_schedule_entry(
        self, lesson_id, teacher_id, group_id, day_of_the_week, korpus_or_online, number_of_auditoria, type_of_lesson, time
    ):
        """Add a new schedule entry by calling the add_to_schedule function."""
        self.cursor.execute(
            "SELECT add_to_schedule(%s, %s, %s, %s, %s, %s, %s, %s);",
            (lesson_id, teacher_id, group_id, day_of_the_week, korpus_or_online, number_of_auditoria, type_of_lesson, time),
        )

    def delete_schedule_entry(self, lesson_id):
        """Delete a schedule entry by calling the delete_schedule_entry_by_id function."""
        self.cursor.execute("SELECT delete_schedule_entry_by_id(%s);", (lesson_id,))

    def clear_schedule(self):
        """Clear all schedule entries by calling the clear_schedule function."""
        self.cursor.execute("SELECT clear_schedule();")

    def update_schedule_type_of_lesson(self, new_type, lesson_id):
        """Update the type of lesson by calling the update_schedule_type_of_lesson function."""
        self.cursor.execute("SELECT update_schedule_type_of_lesson(%s, %s);", (new_type, lesson_id))

    def get_all_schedule_entries(self):
        """Retrieve all schedule entries as JSON."""
        self.cursor.execute("SELECT get_schedule_entries();")
        return self.cursor.fetchone()[0]

    def find_schedule_by_teacher(self, teacher_id):
        """Find schedule entries by teacher_id."""
        self.cursor.execute("SELECT find_schedule_by_teacher(%s);", (teacher_id,))
        return self.cursor.fetchone()[0]

    def find_schedule_by_day(self, day_of_the_week):
        """Find schedule entries by day_of_the_week."""
        self.cursor.execute("SELECT find_schedule_by_day(%s);", (day_of_the_week,))
        return self.cursor.fetchone()[0]
