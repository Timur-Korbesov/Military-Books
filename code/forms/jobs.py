from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class JobsForm(FlaskForm):
    title_of_activity = StringField('Job Title', validators=[DataRequired()])
    team_leader = IntegerField('Team leader id', validators=[DataRequired()])
    work_size = IntegerField('Work Size', validators=[DataRequired()])
    list_of_collaborators = StringField('Collaborators', validators=[DataRequired()])
    is_finished = BooleanField('is job finished?')
    submit = SubmitField('Применить')