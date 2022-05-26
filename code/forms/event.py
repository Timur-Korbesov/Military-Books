from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SelectField, DateField
from wtforms import SubmitField
from wtforms.validators import DataRequired

import sqlite3

con = sqlite3.connect('./db/it-cube-data.db')
cur = con.cursor()

quare_form_hold = f"""
        SELECT id, Form FROM Form_of_holding  
        """
quare_status = f"""
        SELECT id, Status_name FROM Status  
        """
quare_direct = f"""
        SELECT id, Direction FROM Directions  
        """
quare_event = f"""
        SELECT id, Name_of_event FROM Event  
        """
quare_employer = f"""
        SELECT id, FIO FROM Employees  
        """
Results_form_hold = cur.execute(quare_form_hold).fetchall()
Results_status = cur.execute(quare_status).fetchall()
Results_direct = cur.execute(quare_direct).fetchall()
Results_event = cur.execute(quare_event).fetchall()
Results_employer = cur.execute(quare_employer).fetchall()


class AddEventForm(FlaskForm):
    Name_of_event = StringField('Название события', validators=[DataRequired()])
    Organizer = StringField('Организатор', validators=[DataRequired()])
    Description = TextAreaField('Описание', validators=[DataRequired()])
    Website = StringField('Сайт', validators=[DataRequired()])
    Link_to_position = StringField('Ссылка на положение', validators=[DataRequired()])
    Link_to_regestration = StringField('Ссылка на регистрацию', validators=[DataRequired()])

    Form_of_holding = SelectField('Форма проведения', validators=[DataRequired()], coerce=int,
                                  choices=[(form_hold[0], form_hold[1]) for form_hold in Results_form_hold])
    Status = SelectField('Статус', validators=[DataRequired()], coerce=int,
                         choices=[(status[0], status[1]) for status in Results_status])
    Direction = SelectField('Направление', validators=[DataRequired()], coerce=int,
                            choices=[(direct[0], direct[1]) for direct in Results_direct])
    Employer = SelectField('Наставник', validators=[DataRequired()], coerce=int,
                           choices=[(employer[0], employer[1]) for employer in Results_employer])
    Age = StringField('Возрастные ограничения')
    Class = StringField('Промежуток классов', validators=[DataRequired()])
    Number_of_participants = StringField('Примерное количество участнков')
    Note = TextAreaField('Примечания')
    Photo = FileField('Фото события')
    submit = SubmitField('Подтвердить')


class AddStageForm(FlaskForm):
    Stage = StringField('Этап события', validators=[DataRequired()])
    Date_begin = DateField('Дата начала', validators=[DataRequired()])
    Date_end = DateField('Дата окончания', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')
