from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.ext.declarative import declarative_base  # Фабрика базовых классов
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine  # Реализация поддержки асинхронных запросов к БД
from sqlalchemy.orm import sessionmaker, relationship
import os
from dotenv import load_dotenv  # pip install python-dotenv
from sqlalchemy_utils import EmailType  # pip install SQLAlchemy-Utils

load_dotenv()

user = os.getenv('PG_USER')
psw = os.getenv('PG_PASSWORD')
db = os.getenv('PG_DB')
host = os.getenv('PG_HOST')
port = os.getenv('PG_PORT')


# Подключение к БД
PG_DSN = f'postgresql+asyncpg://{user}:{psw}@{host}:{port}/{db}'
# Движок
engine = create_async_engine(PG_DSN)
# expire_on_commit=False, чтобы сессия не истекала, после того как мы сделали коммит
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
# Базовый класс
Base = declarative_base()


class Adv(Base):
    __tablename__ = 'adv'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False, index=True)
    message = Column(String)
    creation_time = Column(DateTime, server_default=func.now())
    owner = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("adv_users.id", ondelete="CASCADE"))
    user = relationship("User", lazy="joined")


class User(Base):

    __tablename__ = "adv_users"

    id = Column(Integer, primary_key=True)
    email = Column(EmailType, unique=True, index=True, nullable=False)
    password = Column(String(60), nullable=False)
    registration_time = Column(DateTime, server_default=func.now())