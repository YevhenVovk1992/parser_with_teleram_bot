import os
import asyncpg
import psycopg2


class PostgresDB:
    def __init__(self, database):
        self.user = os.environ.get('POSTGRES_USER')
        self.password = os.environ.get('POSTGRES_PASSWORD')
        self.database = database
        self.host = os.environ.get('DB_HOST')
        self.port = os.environ.get('DB_PORT')

    async def async_db_connect(self):
        """
        Create async connection to the database
        """
        return await asyncpg.connect(user=self.user,
                                     password=self.password,
                                     database=self.database,
                                     host=self.host,
                                     port=self.port
                                     )

    def db_connect(self):
        return psycopg2.connect(user=self.user,
                                password=self.password,
                                database=self.database,
                                host=self.host,
                                port=self.port
                                )
