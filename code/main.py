from datetime import datetime
import sqlite3

from flask import Flask, render_template, make_response, session, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import redirect

from data import db_session
from data.results import Results, Achievement
from data.students import Students, Studies_it_cube
from data.direction import Directions
from data.event import Event
from data.stages_event import Stages_Events
from data.employees import Employees, StatusEmployer
from forms.user import RegisterForm, LoginForm
from forms.students_forms import AddStudents
from forms.jobs import JobsForm
from gg.data.jobs import Jobs


app = Flask(__name__)
app.config['SECRET_KEY'] = 'it-cube-ol15'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(Employees).get(user_id)


@app.route("/index")
@app.route("/")
def index():
    jobs = None
    jobs = None
    db_sess = db_session.create_session()
    # if current_user.is_authenticated:
    #     jobs = db_sess.query(Jobs)
    return render_template("index.html", jobs=jobs)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(Employees).filter(Employees.Email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(Employees).filter(Employees.Email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        if db_sess.query(Employees).filter(Employees.Number_phone == form.number_phone.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким номером телефона уже существует")
        employer = Employees(
            FIO=form.FIO.data,
            Email=form.email.data,
            Date_of_birth=form.date_of_birth.data,
            Place_of_residence=form.place_of_residence.data,
            Number_phone=form.number_phone.data,
            Gender=form.gender.data,
            Status=form.status.data,
            Note=form.note.data
        )
        employer.set_password(form.password.data)
        db_sess.add(employer)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/addresult',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = JobsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = Jobs()
        jobs.team_leader = form.team_leader.data
        jobs.job = form.title_of_activity.data
        jobs.work_size = form.work_size.data
        jobs.collaborators = form.list_of_collaborators.data
        jobs.is_finished = form.is_finished.data
        current_user.jobs.append(jobs)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('addresult.html', title='Добавление результата',
                           form=form)


@app.route('/students')
def students():
    db_sess = db_session.create_session()

    res_dict = {}
    for stud in db_sess.query(Students).all():
        res_dict[stud.id] = [stud.FIO, stud.Date_of_birth, stud.Class, stud.Place_of_residence,
                             stud.School, stud.Number_phone_student, stud.Number_phone_parent,
                             stud.Gender, stud.Note]
    return render_template('students.html', all_students=res_dict)


@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    form = AddStudents()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        new_student = Students(
            FIO=form.FIO.data,
            Date_of_birth=form.date_of_birth.data,
            Class=form.class_number.data,
            Сertificate_DO=int(form.certificate_do.data),
            Place_of_residence=form.place_of_residence.data,
            School=form.school.data,
            Number_phone_student=form.number_phone.data,
            Number_phone_parent=form.number_phone_parent.data,
            Gender=form.gender.data,
            Note=form.note.data
        )
        if not db_sess.query(Students).filter(Students.Number_phone_student == form.number_phone.data).first():
            db_sess.add(new_student)
            db_sess.commit()
    return render_template('add_student.html', form=form)


@app.route('/employees')
def employees():
    db_sess = db_session.create_session()
    res_dict = {}
    for empl in db_sess.query(Employees).all():
        status = db_sess.query(StatusEmployer).filter(StatusEmployer.id == empl.Status).first()
        res_dict[empl.id] = [empl.FIO, empl.Email, empl.Hashed_password, empl.Date_of_birth,
                             empl.Place_of_residence, empl.Number_phone, empl.Gender, status.Role,
                             empl.Note]
    return render_template('employees.html', all_employees=res_dict)


@app.route('/reports')
def reports():
    db_sess = db_session.create_session()

    res_dict = {}
    for result in db_sess.query(Results).all():
        student_info = db_sess.query(Studies_it_cube).filter(Studies_it_cube.Id_student == result.Id_student).first()
        student = db_sess.query(Students).filter(Students.id == student_info.Id_student).first().FIO

        employeer = db_sess.query(Employees).filter(Employees.id == result.Id_employer).first().FIO

        direction = db_sess.query(Directions).filter(Directions.id == student_info.Direction).first().Direction

        id_event = db_sess.query(Stages_Events).filter(Stages_Events.id == result.Id_stage_event).first().Id_event
        event = db_sess.query(Event).filter(Event.id == id_event).first().Name_of_event

        res = db_sess.query(Achievement).filter(Achievement.id == result.Id_achievement).first().Achievement

        res_dict[result.id] = [student, employeer, direction, event, res]

    return render_template('reports.html', all_reports=res_dict)


#
# @app.route('/news/<int:id>', methods=['GET', 'POST'])
# @login_required
# def edit_news(id):
#     form = NewsForm()
#     if request.method == "GET":
#         db_sess = db_session.create_session()
#         news = db_sess.query(News).filter(News.id == id,
#                                           News.user == current_user
#                                           ).first()
#         if news:
#             form.title.data = news.title
#             form.content.data = news.content
#             form.is_private.data = news.is_private
#         else:
#             abort(404)
#     if form.validate_on_submit():
#         db_sess = db_session.create_session()
#         news = db_sess.query(News).filter(News.id == id,
#                                           News.user == current_user
#                                           ).first()
#         if news:
#             news.title = form.title.data
#             news.content = form.content.data
#             news.is_private = form.is_private.data
#             db_sess.commit()
#             return redirect('/')
#         else:
#             abort(404)
#     return render_template('news.html',
#                            title='Редактирование новости',
#                            form=form
#                            )
#
#
# @app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
# @login_required
# def news_delete(id):
#     db_sess = db_session.create_session()
#     news = db_sess.query(News).filter(News.id == id,
#                                       News.user == current_user
#                                       ).first()
#     if news:
#         db_sess.delete(news)
#         db_sess.commit()
#     else:
#         abort(404)
#     return redirect('/')


def main():
    db_session.global_init("db/it-cube-data.db")
    app.run()


if __name__ == '__main__':
    main()
