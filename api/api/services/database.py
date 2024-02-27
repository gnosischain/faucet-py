import sqlite3


class Database:
    def __init__(self, db_name):
        # self.client = Client()
        # self.client.connect(db_address, db_port)
        # self.cache = self.client.get_or_create_cache(db_name)
        self.connection = sqlite3.connect(db_name)

    def get_connection(self):
        self.connection.row_factory = sqlite3.Row
        return self.connection


class DatabaseSingleton:
    _instance = None

    def __new__(cls, db_name):
        if not hasattr(cls, 'instance'):
            cls.instance = Database(db_name)
        return cls.instance