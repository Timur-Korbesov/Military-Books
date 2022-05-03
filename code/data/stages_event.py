import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Stages(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Stages'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    Stage = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Date_begin = sqlalchemy.Column(sqlalchemy.Date, nullable=True)
    Date_end = sqlalchemy.Column(sqlalchemy.Date, nullable=True)

    stage_events = orm.relation("Stages_Events", back_populates='stage')


class Stages_Events(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Stages_Events'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    Id_event = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Event.id"), nullable=True)
    Id_stage = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Stages.id"))

    stage = orm.relation("Stages")
    event = orm.relation("Event")
    Results = orm.relation("Results", back_populates='stage_events')
