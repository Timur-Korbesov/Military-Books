from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, DateField, TextAreaField, BooleanField, SelectField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired


class AddStudents(FlaskForm):
    FIO = StringField('ФИО', validators=[DataRequired()])
    email = EmailField('Адрес электронной почты')
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
    submit = SubmitField('Добавить ученика')