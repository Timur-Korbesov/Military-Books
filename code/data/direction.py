import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Direction(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Directions'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    Direction = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Note = sqlalchemy.Column(sqlalchemy.Text)
    studies_it_cube = orm.relation("StudiesITCube", back_populates='direction')
    event = orm.relation("Event", back_populates='direction')