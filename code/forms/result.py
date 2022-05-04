from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import StringField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired

import sqlite3

con = sqlite3.connect('./db/it-cube-data.db')
cur = con.cursor()

quare_student = f"""
        SELECT id, FIO FROM Students  
        """
quare_event = f"""
        SELECT id, Name_of_event FROM Event  
        """
quare_achievement = f"""
        SELECT id, Achievement FROM Achievement  
        """
quare_employer = f"""
        SELECT id, FIO FROM Employees  
        """
quare_stages_id = f"""
        SELECT id_stage FROM Stages_Events
        WHERE id_event == ?
        """
quare_stages = f"""
        SELECT id, Stage FROM Stages
        WHERE id == ?
        """
Results_student = cur.execute(quare_student).fetchall()
Results_event = cur.execute(quare_event).fetchall()
Results_achievement = cur.execute(quare_achievement).fetchall()
Results_employer = cur.execute(quare_employer).fetchall()
Results_stages_id = cur.execute(quare_stages_id, (Results_event[0][0], )).fetchall()
Results_stages = []
for i in Results_stages_id:
    res_stages = cur.execute(quare_stages, (i[0], )).fetchall()
    Results_stages.append(res_stages[0])


class EventForm(FlaskForm):
    event = SelectField('Событие', validators=[DataRequired()], coerce=int,
                        choices=[(event[0], event[1]) for event in Results_event])
    submit = SubmitField('Подтвердить событие')


class ResultsForm(FlaskForm):
    stage = SelectField('Этап события', validators=[DataRequired()], coerce=int,
                        choices=[(stage[0], stage[1]) for stage in Results_stages], )
    FIO = SelectField('ФИО ученика', validators=[DataRequired()], coerce=int,
                      choices=[(student[0], student[1]) for student in Results_student])
    achievement = SelectField('Достижение', validators=[DataRequired()], coerce=int,
                              choices=[(achievement[0], achievement[1]) for achievement in Results_achievement])
    FIO_employer = SelectField('Наставник', validators=[DataRequired()], coerce=int,
                               choices=[(employer[0], employer[1]) for employer in Results_employer])
    achievement_photo = FileField('Электронный вид достижения')
    submit = SubmitField('Добавить результат')
