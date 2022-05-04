import os
import sqlite3
from datetime import datetime

from flask import Flask, render_template, make_response, session, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import redirect, secure_filename

from data import db_session
from data.students import Students
from data.employees import Employees
from data.results import Results
from data.stages_event import Stages_Events
from forms.user import RegisterForm, LoginForm
from forms.result import ResultsForm, EventForm
from forms import result

app = Flask(__name__)
app.config['SECRET_KEY'] = 'it-cube-ol15'
login_manager = LoginManager()
login_manager.init_app(app)

# Формы для результатов
form_event = EventForm
results_stages = []


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


@app.route('/results_event', methods=['GET', 'POST'])
@login_required
def results_event():
    global form_event, results_stages
    form_event = EventForm()
    print(form_event.event.data, '-----------------------------------------22----------------')
    con = sqlite3.connect('./db/it-cube-data.db')
    cur = con.cursor()
    if form_event.is_submitted():
        event_id = form_event.event.data
        results_stages_id = cur.execute(result.quare_stages_id, (event_id,)).fetchall()
        results_stages = []
        for i in results_stages_id:
            res_stages = cur.execute(result.quare_stages, (i[0],)).fetchall()
            results_stages.append(res_stages[0])
        return redirect('/results')
    return render_template('results_event.html', title='Добавление результата',
                           form=form_event)


@app.route('/results', methods=['GET', 'POST'])
@login_required
def results():
    global results_stages, form_event
    form_result = ResultsForm()
    form_result.stage.choices = [(stage[0], stage[1]) for stage in results_stages]
    print('-----------------------------------------------------')
    print(form_result.FIO.choices)
    con = sqlite3.connect('./db/it-cube-data.db')
    cur = con.cursor()
    if form_result.validate_on_submit():
        quare_stages_events = f"""
                SELECT id FROM Stages_Events
                WHERE id_event == ? AND id_stage == ?
                """
        result_stage_id = cur.execute(quare_stages_events, (form_event.event.data, form_result.stage.data)).fetchall()
        db_sess = db_session.create_session()

        f = request.files['achievement_photo']
        path = 'static/img/' + secure_filename(f.filename)
        f.save(path)
        with open(path, 'rb') as file:
            blob_data = file.read()
        os.remove(path)
        res = Results(
            Id_stage_event=result_stage_id[0][0],
            Id_student=form_result.FIO.data,
            Id_achievement=form_result.achievement.data,
            Id_employer=form_result.FIO_employer.data,
            Diploms=blob_data
        )
        db_sess.add(res)
        db_sess.commit()
        return redirect('/results')
    return render_template('results.html', title='Добавление результата',
                           form=form_result)


@app.route('/students')
def students():
    # students = Student()
    # students.FIO = "Корбесов Тимур Тамазиевич"
    # students.FIO = "30.04.2007"
    # students.Class = 9
    # students.Сertificate_DO = 2115631
    # students.Place_of_residence = "с.Карджин"
    # students.School = "МБОУ СОШ №2"
    # students.Number_phone_student = "89034830885"
    # students.Number_phone_parent = "89289397448"
    # students.Gender = "муж"
    # students.Note = ""
    db_sess = db_session.create_session()
    # db_sess.add(students)
    # db_sess.commit()
    res_dict = {}

    for stud in db_sess.query(Student).all():
        res_dict[stud.id] = [stud.FIO, stud.Date_of_birth, stud.Class, stud.Place_of_residence,
                             stud.School, stud.Number_phone_student, stud.Number_phone_parent,
                             stud.Gender, stud.Note]
    return render_template('students.html', all_students=res_dict)


@app.route('/employees')
def employees():
    db_sess = db_session.create_session()


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
