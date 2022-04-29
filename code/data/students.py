import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Student(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Students'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    FIO = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Date_of_birth = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Class = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    Сertificate_DO = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    Place_of_residence = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    School = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Number_phone_student = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Number_phone_parent = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Gender = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Note = sqlalchemy.Column(sqlalchemy.Text)