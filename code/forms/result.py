from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired


class ResultForm(FlaskForm):
    FIO = StringField('ФИО', validators=[DataRequired()])
    event = SelectField('Событие', validators=[DataRequired()])
    achievement = SelectField('Достижение', validators=[DataRequired()])
    FIO_employer = SelectField('Наставник', validators=[DataRequired()])
    achievement_photo = FileField('Электронный вид достижения', validators=[DataRequired()])
    # gender = SelectField('Ваш пол', validators=[DataRequired()], coerce=str, choices=[('Мужской', 'Мужской'),
    #                                                                                   ('Женский', 'Женский')])
    # status = SelectField('Ваш статус', validators=[DataRequired()], coerce=int, choices=[(1, 'Методист'),
    #                                                                                      (2, 'Директор'),
    #                                                                                      (2, 'Педагог ДО'),
    #                                                                                      (2, 'Администратор'),
    #                                                                                      (2, 'Педагог организатор')])
    submit = SubmitField('Добавить результат')

