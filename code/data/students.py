import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class StudiesITCube(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Studies_it_cube'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    Direction = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Directions.id"), nullable=True)
    Date_of_admission = sqlalchemy.Column(sqlalchemy.Date, nullable=True)
    Date_of_deductions = sqlalchemy.Column(sqlalchemy.Date, nullable=True)
    Id_student = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Students.id"), nullable=True)
    Id_employeer = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Employees.id"), nullable=True)
    Note = sqlalchemy.Column(sqlalchemy.Text)
    student = orm.relation('Student')
    direction = orm.relation('Direction')
    employeer = orm.relation('Employees')
    event = orm.relation('Event')


class Student(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Students'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    FIO = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Date_of_birth = sqlalchemy.Column(sqlalchemy.Date, nullable=True)
    Class = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    Сertificate_DO = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    Place_of_residence = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    School = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Number_phone_student = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Number_phone_parant = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Gender = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Note = sqlalchemy.Column(sqlalchemy.Text)
    studies_it_cube = orm.relation("StudiesITCube", back_populates='student')
    result = orm.relation("Result", back_populates='student')

