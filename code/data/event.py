import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Participation_employees(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Participation_employees'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    Id_event = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Event.id"), nullable=True)
    Id_employer = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Employees.id"), nullable=True)
    Note = sqlalchemy.Column(sqlalchemy.Text)

    event = orm.relation('Event')
    employer = orm.relation('Employees')


class Status(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Status'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    Status_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)


class Form_of_Holding(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Form_of_holding'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    Form = sqlalchemy.Column(sqlalchemy.String, nullable=True)


class Event(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Event'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    Name_of_event = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Organizer = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Description = sqlalchemy.Column(sqlalchemy.Text)
    Website = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Link_to_position = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Link_to_regestration = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    Form_of_holding = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Form_of_holding.id"), nullable=True)
    Status = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Status.id"), nullable=True)
    Direction = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Directions.id"), nullable=True)

    Age = sqlalchemy.Column(sqlalchemy.String)
    Class = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Note = sqlalchemy.Column(sqlalchemy.Text)
    Photo = sqlalchemy.Column(sqlalchemy.BLOB)
    Number_of_participants = sqlalchemy.Column(sqlalchemy.String)

    direction = orm.relation('Directions')
    participation_employees = orm.relation("Participation_employees", back_populates='event')
    stage_events = orm.relation("Stages_Events", back_populates='event')
