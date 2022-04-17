import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class Employees(SqlAlchemyBase, UserMixin):
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
    Status = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Note = sqlalchemy.Column(sqlalchemy.Text)

    # jobs = orm.relation("Jobs", back_populates='user')

    def __repr__(self):
        return f"<User> {self.name} {self.email}"

    def set_password(self, password):
        self.Hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.Hashed_password, password)
