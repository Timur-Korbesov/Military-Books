import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Achievement(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Achievement'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    Achievement = sqlalchemy.Column(sqlalchemy.String, nullable=True)


class Result(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Results'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    Id_student = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("Students.id"))
    Id_event = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Event.id"), nullable=True)
    Id_achievement = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Achievement.id"), nullable=True)
    Id_employer = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Employees.id"), nullable=True)
    Diploms = sqlalchemy.Column(sqlalchemy.BLOB, nullable=True)

    employer = orm.relation("Employees")
    student = orm.relation("Students")
    event = orm.relation("Event")
