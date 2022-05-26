from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TextAreaField, SelectField
from wtforms.validators import DataRequired

import sqlite3

con = sqlite3.connect('./db/it-cube-data.db')
cur = con.cursor()

quare_direct = f"""
        SELECT id, Direction FROM Directions  
        """
quare_employer = f"""
        SELECT id, FIO FROM Employees  
        """
Results_direct = cur.execute(quare_direct).fetchall()
Results_employer = cur.execute(quare_employer).fetchall()


class AddStudents(FlaskForm):
    FIO = StringField('ФИО', validators=[DataRequired()])
    date_of_birth = DateField('Дата рождения', validators=[DataRequired()])
    class_number = StringField('Класс', validators=[DataRequired()])
    certificate_do = StringField('Сертификат дополнительного образования', validators=[DataRequired()])
    place_of_residence = StringField('Место жительства', validators=[DataRequired()])
    school = StringField('Школа', validators=[DataRequired()])
    number_phone = StringField('Номер телефона', validators=[DataRequired()])
    number_phone_parent = StringField('Номер телефона родителя', validators=[DataRequired()])
    gender = SelectField('Пол', validators=[DataRequired()], coerce=str, choices=[('Мужской', 'Мужской'),
                                                                                  ('Женский', 'Женский')])
    note = TextAreaField('Примечание')
    submit = SubmitField('Подтвердить')


class AddStudyItCube(FlaskForm):
    Direction = SelectField('Направление', validators=[DataRequired()], coerce=int,
                            choices=[(direct[0], direct[1]) for direct in Results_direct])
    Date_of_admission = DateField('Дата зачисления', validators=[DataRequired()])
    Date_of_deductions = DateField('Дата отчисления', validators=[DataRequired()])
    Id_employer = SelectField('Наставник', validators=[DataRequired()], coerce=int,
                              choices=[(employer[0], employer[1]) for employer in Results_employer])
    submit = SubmitField('Подтвердить')
