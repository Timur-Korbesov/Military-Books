from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SelectField, DateField
from wtforms import SubmitField
from wtforms.validators import DataRequired

import sqlite3


quare_form_hold = f"""
        SELECT id, Form FROM Form_of_holding  
        """
quare_status = f"""
        SELECT id, Status_name FROM Status  
        """
quare_direct = f"""
        SELECT id, Direction FROM Directions  
        """
quare_employer = f"""
        SELECT id, FIO FROM Employees  
        """


def update_event(form_of_holding, status, direction, employer):
    con = sqlite3.connect('./db/it-cube-data.db')
    cur = con.cursor()
    results_form_hold = cur.execute(quare_form_hold).fetchall()
    results_status = cur.execute(quare_status).fetchall()
    results_direct = cur.execute(quare_direct).fetchall()
    results_employer = cur.execute(quare_employer).fetchall()

    form_of_holding.choices = [(form_hold[0], form_hold[1]) for form_hold in results_form_hold]
    direction.choices = [(direct[0], direct[1]) for direct in results_direct]
    status.choices = [(status[0], status[1]) for status in results_status]
    employer.choices = [(employer[0], employer[1]) for employer in results_employer]


class AddEventForm(FlaskForm):
    Name_of_event = StringField('Название мероприятия', validators=[DataRequired()])
    Organizer = StringField('Организатор', validators=[DataRequired()])
    Description = TextAreaField('Описание', validators=[DataRequired()])
    Website = StringField('Сайт', validators=[DataRequired()])
    Link_to_position = StringField('Ссылка на положение', validators=[DataRequired()])
    Link_to_regestration = StringField('Ссылка на регистрацию', validators=[DataRequired()])

    Form_of_holding = SelectField('Форма проведения', validators=[DataRequired()], coerce=int,
                                  choices=[])
    Status = SelectField('Статус', validators=[DataRequired()], coerce=int,
                         choices=[])
    Direction = SelectField('Направление', validators=[DataRequired()], coerce=int,
                            choices=[])
    Employer = SelectField('Наставник', validators=[DataRequired()], coerce=int,
                           choices=[])
    Age = StringField('Возрастные ограничения')
    Class = StringField('Промежуток классов', validators=[DataRequired()])
    Number_of_participants = StringField('Примерное количество участнков')
    Note = TextAreaField('Примечания')
    Photo = FileField('Фото мероприятия')
    submit = SubmitField('Подтвердить')


class AddStageForm(FlaskForm):
    Stage = StringField('Этап мероприятия', validators=[DataRequired()])
    Date_begin = DateField('Дата начала', validators=[DataRequired()])
    Date_end = DateField('Дата окончания', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')


class AddDirection(FlaskForm):
    direction = StringField('Название направления', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')


class AddFormOfHolding(FlaskForm):
    form_of_hold = StringField('Форма проведения', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')


class AddStatus(FlaskForm):
    status = StringField('Статус мероприятия', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')
