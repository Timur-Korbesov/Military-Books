import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Achievmient(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Achievmient'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    Achievement = sqlalchemy.Column(sqlalchemy.String, nullable=True)


class Result(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Results'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    Id_student = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("Student.id"))
    Id_event = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Event.id"), nullable=True)
    Id_achievement = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Achievmient.id"), nullable=True)
    Id_employeer = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Employees.id"), nullable=True)
    Diploms = sqlalchemy.Column(sqlalchemy.BLOB, nullable=True)

    employeer = orm.relation("Employees")
    student = orm.relation("Student")
    event = orm.relation("Event")
