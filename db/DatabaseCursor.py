import psycopg2
from my_logging import my_logging

logger = my_logging.get_logger(__name__)


class DatabaseCursor:
    """
    Database cursor object in a context manager format to make sure the all the resources are cleaned up and free after disconnected from the database
    """

    def __init__(self, conn_str):
        try:
            self.conn = psycopg2.connect(**conn_str)
            self.conn.autocommit = True
            self.cur = self.conn.cursor()

        except Exception as e:
            raise Exception("Failed to connect to PostgreSQL\n{}".format(e))

    def __enter__(self):
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info("Exiting PostgreSQL...")

        self.cur.close()
        self.conn.close()

        logger.info("Exited PostgreSQL!")
