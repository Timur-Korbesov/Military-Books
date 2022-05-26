import datetime
from flask_wtf import FlaskForm
from wtforms import SelectField, DateField
from wtforms import SubmitField
from wtforms.validators import DataRequired

import sqlite3

con = sqlite3.connect('./db/it-cube-data.db')
cur = con.cursor()
# Запросы
quare_employer = f"""
        SELECT id, FIO FROM Employees  
        """
quare_student = f"""
        SELECT id, FIO FROM Students  
        """
quare_direct = f"""
        SELECT id, Direction FROM Directions  
        """
quare_event = f"""
        SELECT id, Name_of_event FROM Event  
        """
quare_status = f"""
        SELECT id, Status_name FROM Status  
        """
quare_achievement = f"""
        SELECT id, Achievement FROM Achievement  
        """
Results_student = [(-1, ''), *cur.execute(quare_student).fetchall()]
Results_employer = [(-1, ''), *cur.execute(quare_employer).fetchall()]
Results_direct = [(-1, ''), *cur.execute(quare_direct).fetchall()]
Results_event = [(-1, ''), *cur.execute(quare_event).fetchall()]
Results_status = [(-1, ''), *cur.execute(quare_status).fetchall()]
Results_achievement = [(-1, ''), *cur.execute(quare_achievement).fetchall()]


# Класс формы
class FiltersForm(FlaskForm):
    student = SelectField('по ученикам', validators=[DataRequired()], coerce=int,
                          choices=[(student[0], student[1]) for student in Results_student])
    employer = SelectField('по наставникам', validators=[DataRequired()], coerce=int,
                           choices=[(employer[0], employer[1]) for employer in Results_employer])
    direction = SelectField('по направлениям', validators=[DataRequired()], coerce=int,
                            choices=[(direct[0], direct[1]) for direct in Results_direct])
    event = SelectField('по событиям', validators=[DataRequired()], coerce=int,
                        choices=[(event[0], event[1]) for event in Results_event])
    status = SelectField('по статусу', validators=[DataRequired()], coerce=int,
                         choices=[(status[0], status[1]) for status in Results_status])
    data_begin = DateField('от ')
    data_end = DateField('до')
    achievement = SelectField('по достижению', validators=[DataRequired()], coerce=int,
                              choices=[(achievement[0], achievement[1]) for achievement in Results_achievement])
    submit = SubmitField('Применить фильтры')
