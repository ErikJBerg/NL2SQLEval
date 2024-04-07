import sqlite3


class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_path)
        return self.connection

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def get_cursor(self):
        if not self.connection:
            self.connect()
        return self.connection.cursor()