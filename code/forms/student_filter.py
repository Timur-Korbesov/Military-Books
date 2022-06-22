import datetime
from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired

import sqlite3

# Запросы
quare_employer = f"""
        SELECT id, FIO FROM Employees  
        """
quare_schools = f"""
        SELECT id, School FROM Schools  
        """
quare_direct = f"""
        SELECT id, Direction FROM Directions  
        """


def update_filter(school, employer, direction, class_1, class_2):
    con = sqlite3.connect('./db/it-cube-data.db')
    cur = con.cursor()
    results_school = [(-1, ''), *sorted(cur.execute(quare_schools).fetchall(), key=lambda n: n[1])]
    results_employer = [(-1, ''), *sorted(cur.execute(quare_employer).fetchall(), key=lambda n: n[1])]
    results_direct = [(-1, ''), *sorted(cur.execute(quare_direct).fetchall(), key=lambda n: n[1])]

    school.choices = [(schol[0], schol[1]) for schol in results_school]
    employer.choices = [(employer[0], employer[1]) for employer in results_employer]
    direction.choices = [(direct[0], direct[1]) for direct in results_direct]
    class_1.choices = [(-1, ''), *[(i, i) for i in range(1, 12)]]
    class_2.choices = [(-1, ''), *[(i, i) for i in range(1, 12)]]


# Класс формы
class FiltersStudentsForm(FlaskForm):
    place = StringField('по месту проживания')
    school = SelectField('по школе', validators=[DataRequired()], coerce=int,
                         choices=[])
    gender = SelectField('по полу', validators=[DataRequired()], coerce=str,
                         choices=[['False', ''],
                                  ['Мужской', 'Мужской'],
                                  ['Женский', 'Женский']])
    class_1 = SelectField('по классу c', validators=[DataRequired()], coerce=int,
                          choices=[])
    class_2 = SelectField('по', validators=[DataRequired()], coerce=int,
                          choices=[])
    direction = SelectField('по направлению', validators=[DataRequired()], coerce=int,
                            choices=[])
    employer = SelectField('по наставнику', validators=[DataRequired()], coerce=int,
                           choices=[])
    data_begin = DateField('по дате рождения от')
    data_end = DateField('до')
    submit = SubmitField('Применить фильтры')
