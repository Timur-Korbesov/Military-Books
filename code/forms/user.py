from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, DateField, TextAreaField, BooleanField, SelectField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Email


class RegisterForm(FlaskForm):
    FIO = StringField('ФИО', validators=[DataRequired()])
    email = EmailField('Адресс электронной почты', validators=[Email(), DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    date_of_birth = DateField('Дата рождения', validators=[DataRequired()])
    place_of_residence = StringField('Место проживания', validators=[DataRequired()])
    number_phone = StringField('Номер телефона', validators=[DataRequired()])
    gender = SelectField('Ваш пол', validators=[DataRequired()], coerce=str, choices=[('Мужской', 'Мужской'),
                                                                                      ('Женский', 'Женский')])
    status = SelectField('Ваш статус', validators=[DataRequired()], coerce=int, choices=[(1, 'Методист'),
                                                                                         (2, 'Директор'),
                                                                                         (3, 'Педагог ДО'),
                                                                                         (4, 'Администратор'),
                                                                                         (5, 'Педагог организатор')])
    note = TextAreaField('Дополнительно')
    submit = SubmitField('Зарегестрироваться')


class LoginForm(FlaskForm):
    email = EmailField('Адресс электронной почты', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Авторизироваться')
