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
    result = orm.relation('Result')
