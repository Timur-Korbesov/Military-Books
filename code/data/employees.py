import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class StatusEmpoyeer(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Status_employees'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    Role = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    employeer = orm.relation("Employees", back_populates='status_employeer')


class Employees(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Employees'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    FIO = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Email = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True)
    Hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Date_of_birth = sqlalchemy.Column(sqlalchemy.Date, nullable=True)
    Place_of_residence = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Number_phone = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Gender = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Status = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("Status_employees.id"), nullable=True)
    Note = sqlalchemy.Column(sqlalchemy.Text)

    status_employeer = orm.relation('StatusEmpoyeer')

    def __repr__(self):
        return f"<User> {self.name} {self.email}"

    def set_password(self, password):
        self.Hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.Hashed_password, password)
