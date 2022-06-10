import datetime
from flask_wtf import FlaskForm
from wtforms import SelectField, DateField
from wtforms import SubmitField
from wtforms.validators import DataRequired

import sqlite3


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


def update_reports(student, employer, direction, event, status, achievement):
    con = sqlite3.connect('./db/it-cube-data.db')
    cur = con.cursor()
    results_student = [(-1, ''), *cur.execute(quare_student).fetchall()]
    results_employer = [(-1, ''), *cur.execute(quare_employer).fetchall()]
    results_direct = [(-1, ''), *cur.execute(quare_direct).fetchall()]
    results_event = [(-1, ''), *cur.execute(quare_event).fetchall()]
    results_status = [(-1, ''), *cur.execute(quare_status).fetchall()]
    results_achievement = [(-1, ''), *cur.execute(quare_achievement).fetchall()]

    student.choices = [(student[0], student[1]) for student in results_student]
    employer.choices = [(employer[0], employer[1]) for employer in results_employer]
    direction.choices = [(direct[0], direct[1]) for direct in results_direct]
    event.choices = [(event[0], event[1]) for event in results_event]
    status.choices = [(status[0], status[1]) for status in results_status]
    achievement.choices = [(achievement[0], achievement[1]) for achievement in results_achievement]


# Класс формы
class FiltersForm(FlaskForm):
    student = SelectField('по ученикам', validators=[DataRequired()], coerce=int,
                          choices=[])
    employer = SelectField('по наставникам', validators=[DataRequired()], coerce=int,
                           choices=[])
    direction = SelectField('по направлениям', validators=[DataRequired()], coerce=int,
                            choices=[])
    event = SelectField('по мероприятиямм', validators=[DataRequired()], coerce=int,
                        choices=[])
    status = SelectField('по статусу', validators=[DataRequired()], coerce=int,
                         choices=[])
    data_begin = DateField('от')
    data_end = DateField('до')
    achievement = SelectField('по достижению', validators=[DataRequired()], coerce=int,
                              choices=[])
    submit = SubmitField('Применить фильтры')
