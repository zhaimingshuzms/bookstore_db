from typing import Union
import logging
import os
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    LargeBinary,
    Enum,
    Float,
    ForeignKey,
)
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import exists
from .config import *

Base = declarative_base()

class User(Base):
    __tablename__ = "User"
    id = Column(String(ID_LEN),primary_key=True,comment="user_id")
    password = Column(String(PASSWORD_LEN),nullable=False,comment="password")
    balance = Column(Integer,nullable=False,comment="balance")
    token = Column(String(TOKEN_LEN),nullable=False,comment="token")
    terminal = Column(String(TOKEN_LEN),nullable=False,comment="terminal")

class Book(Base):
    __tablename__ = "Book"
    book_id = Column(String(ID_LEN),primary_key=True,nullable=False,comment="book_id")
    store_id = Column(String(ID_LEN),ForeignKey("UsertoStore.store_id"),primary_key=True,nullable=False,comment="store_id")
    
    # book_infos
    title = Column(Text,nullable=False,index=True)
    author = Column(Text,nullable=False,index=True)
    publisher = Column(Text,nullable=False,index=True)
    original_title = Column(Text,nullable=False,index=True)
    translator = Column(Text,nullable=False,index=True)
    pub_year = Column(Text,nullable=False,index=True)
    pages = Column(Text,nullable=False,index=True)
    price = Column(Integer,nullable=False,index=True)
    binding = Column(Text,nullable=False,index=True)
    isbn = Column(Text,nullable=False,index=True)
    currency_unit = Column(Text, nullable=False, index=True)

    tags = Column(Text,nullable=False)
    pictures = Column(Text,nullable=False)
    author_intro = Column(Text,nullable=False)
    book_intro = Column(Text,nullable=False)
    content = Column(Text,nullable=False)

    stock_level = Column(Integer,nullable=False)

class UsertoStore(Base):
    __tablename__ = "UsertoStore"
    user_id = Column(String(ID_LEN),ForeignKey("User.id"),nullable=False)
    store_id = Column(String(ID_LEN),primary_key=True,nullable=False)

class Order(Base):
    __tablename__ = "Order"
    order_id = Column(String(ID_LEN),primary_key=True,nullable=False)
    buyer = Column(String(ID_LEN),ForeignKey("User.id",ondelete="SET NULL"),nullable=True)
    store_id = Column(String(ID_LEN),ForeignKey("UsertoStore.store_id"),nullable=False,comment="store_id")
    state = Column(Enum("unpaid", "paid", "delivered", "canceled", "finished",name="state"),nullable=False)
    total_price = Column(Integer,nullable=False)
    timestamp = Column(Float,nullable=False)

class OrdertoBooks(Base):
    __tablename__ = "OrdertoBooks"
    order_id = Column(String(ID_LEN),ForeignKey("Order.order_id"),primary_key=True,nullable=False)
    # book_id = Column(String(ID_LEN),ForeignKey("UsertoStore.store_id"),primary_key=True,comment="book_id")
    # vitual books are valid
    book_id = Column(String(ID_LEN),primary_key=True,comment="book_id")
    count = Column(Integer,nullable=False)
    price = Column(Integer,nullable=False)

class SQLinterface:
    def __init__(self,username,password,database):
        self.engine = create_engine(f'postgresql://{username}:{password}@localhost/{database}')
        try:
            self.session = sessionmaker(self.engine)
            self.create_all()
            logging.info("init success")
        except SQLAlchemyError as e:
            logging.error(e)
            exit(0)
    def __del__(self):
        self.drop_all()
    
    def create_all(self):
        Base.metadata.create_all(self.engine)

    def drop_all(self):
        Base.metadata.drop_all(self.engine)

db : SQLinterface = None

def init_database(username,password,database):
    global db
    db = SQLinterface(username,password,database)

def get_session():
    global db
    return db.session()

# APIs to check id existence.
def user_id_exists(user_id: str) -> bool:
    session = get_session()
    result = session.query(exists().where(User.id==user_id)).scalar()
    session.close()
    return result


def store_id_exists(store_id: str) -> bool:
    session = get_session()
    result = session.query(exists().where(UsertoStore.store_id==store_id)).scalar()
    session.close()
    return result


def order_id_exists(order_id: str) -> bool:
    session = get_session()
    result = session.query(exists().where(Order.order_id==order_id)).scalar()
    session.close()
    return result

def book_id_exists(book_id: str) -> bool:
    session = get_session()
    result = session.query(exists().where(Book.book_id==book_id)).scalar()
    session.close()
    return result