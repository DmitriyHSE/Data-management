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
    def create_database(self):
        self.cursor.callproc("create_database")
