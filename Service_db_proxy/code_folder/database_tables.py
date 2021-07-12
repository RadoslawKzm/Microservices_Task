# pip3 install imports
from sqlalchemy import DECIMAL, TIMESTAMP, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

# user created modules
from Service_db_proxy.code_folder.database_repr_class import ReprClass


class BaseTable(declarative_base(), ReprClass):
    __tablename__ = "base_table"
    UUID = Column(UUID, primary_key=True)
    TIMESTAMP = Column(TIMESTAMP)
    AMOUNT = Column(DECIMAL)
    CURRENCY = Column(String)
    EXCHANGE_RATE = Column(DECIMAL)
    BITCOIN_AMOUNT = Column(DECIMAL)

    def as_dict(self) -> dict:
        self.TIMESTAMP = str(self.TIMESTAMP)
        self.AMOUNT = float(self.AMOUNT)
        self.EXCHANGE_RATE = float(self.EXCHANGE_RATE)
        self.BITCOIN_AMOUNT = float(self.BITCOIN_AMOUNT)
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
