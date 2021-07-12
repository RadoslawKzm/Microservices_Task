# built in imports
import os

# pip3 install imports
from fastapi import status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DbContext(sessionmaker):
    """
    Context manager class for managing SQLalchemy session objects.
    It manages opening transactions, returns session object then after transaction commits/rollbacks and closes.
    It manages all fallbacks for user.
    User doesn't need to worry about commiting changes to DB and exception handling.
    """

    def __init__(self, *args, status_success: status, status_fail: status, **kwargs):
        super(DbContext, self).__init__(*args, **kwargs)
        self.status_success = status_success
        self.status_fail = status_fail
        self.json = {}

    def __enter__(self):
        """
        :return: SQLalchemy session object for context manager to operate on.
        """
        self.session = self()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if any((exc_type, exc_val, exc_tb)):
            self.session.rollback()
            self.session.close()
            self.status_code = self.status_fail
            self.json = {"exc_type": str(exc_type), "exc_val": str(exc_val), "exc_tb": str(exc_tb)}
            return True  # gracefully suppressing
        self.session.commit()
        self.session.close()
        self.status_code = self.status_success

    @staticmethod
    def get_engine():
        """
        Simple function for getting SQLalchemy engine object
        :return: SQLalchemy engine object with established connection
        """
        POSTGRES_USER = os.getenv("POSTGRES_USER", False)
        POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", False)
        POSTGRES_HOSTNAME = os.getenv("POSTGRES_HOSTNAME", False)
        POSTGRES_DB = os.getenv("POSTGRES_DB", False)
        return create_engine(
            f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOSTNAME}/{POSTGRES_DB}"
        )
