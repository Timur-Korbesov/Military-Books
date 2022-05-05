import os
import sqlite3

from flask import Flask, render_template, make_response, session, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort
from werkzeug.utils import redirect, secure_filename

from data import db_session
from data.students import Students, Studies_it_cube
from data.employees import Employees, StatusEmployer
from data.results import Results, Achievement
from data.event import Event, Participation_employees, Form_of_Holding, Status
from data.direction import Directions
from data.stages_event import Stages_Events, Stages
from forms.user import RegisterForm, LoginForm
from forms.result import ResultsForm, EventForm
from forms.event import AddEventForm, AddStageForm
from forms import result
from forms.students_forms import AddStudents

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
    db_sess = db_session.create_session()
    events = db_sess.query(Event).all()
    empls_partic = db_sess.query(Participation_employees).all()
    empls = db_sess.query(Employees).all()
    status = db_sess.query(Status).all()
    form_of_hold = db_sess.query(Form_of_Holding).all()
    direct = db_sess.query(Directions).all()
    return render_template("index.html", events=events, empls_partic=empls_partic, status=status,
                           form_of_hold=form_of_hold,
                           direct=direct, empls=empls)


@app.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    form = AddEventForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        event = Event(
            Name_of_event=form.Name_of_event.data,
            Organizer=form.Organizer.data,
            Description=form.Description.data,
            Website=form.Website.data,
            Link_to_position=form.Link_to_position.data,
            Link_to_regestration=form.Link_to_regestration.data,
            Form_of_holding=form.Form_of_holding.data,
            Status=form.Status.data,
            Direction=form.Direction.data,
            Age=form.Age.data,
            Class=form.Class.data,
            Note=form.Note.data,
            Number_of_participants=form.Number_of_participants.data
        )
        db_sess.add(event)
        db_sess.commit()

        event_id = db_sess.query(Event).all()[-1]
        partic_empl = Participation_employees(
            Id_event=event_id.id,
            Id_emloyer=form.Employer.data,
            Note=None
        )
        db_sess.add(partic_empl)
        db_sess.commit()
        return redirect('/add_event_stage')
    return render_template('event.html', title='Добавление события',
                           form=form)


@app.route('/add_event_stage', methods=['GET', 'POST'])
@login_required
def add_event_stage():
    form = AddStageForm()
    con = sqlite3.connect('./db/it-cube-data.db')
    cur = con.cursor()
    quare_event = f"""
            SELECT id, Name_of_event FROM Event  
            """
    form.Event.choices = [(ev[0], ev[1]) for ev in cur.execute(quare_event).fetchall()]
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        stage = Stages(
            Stage=form.Stage.data,
            Date_begin=form.Date_begin.data,
            Date_end=form.Date_end.data
        )
        db_sess.add(stage)
        db_sess.commit()
        stage_id = db_sess.query(Stages).all()[-1]
        stage_event = Stages_Events(
            Id_event=form.Event.data,
            Id_stage=stage_id.id
        )
        db_sess.add(stage_event)
        db_sess.commit()
        return redirect('/add_event_stage')
    return render_template('event_stage.html', title='Добавление этапа',
                           form=form)


@app.route("/event/<int:id>", methods=['GET', 'POST'])
@login_required
def event(id):
    form = AddEventForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        event = db_sess.query(Event).filter(Event.id == id).first()
        employer_id = db_sess.query(Participation_employees).filter(
            Participation_employees.Id_event == event.id).first().Id_employer
        employer = db_sess.query(Employees).filter(Employees.id == employer_id).first()
        if event:
            form.Name_of_event.data = event.Name_of_event
            form.Organizer.data = event.Organizer
            form.Description.data = event.Description
            form.Website.data = event.Website
            form.Link_to_position.data = event.Link_to_position
            form.Link_to_regestration.data = event.Link_to_regestration
            form.Form_of_holding.data = event.Form_of_holding
            form.Status.data = event.Status
            form.Direction.data = event.Direction
            form.Employer.data = employer.FIO
            form.Age.data = event.Age
            form.Class.data = event.Class
            form.Note.data = event.Note
            form.Number_of_participants.data = event.Number_of_participants
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        event = db_sess.query(Event).filter(Event.id == id).first()
        if event:
            event.Name_of_event = form.Name_of_event.data,
            event.Organizer = form.Organizer.data,
            event.Description = form.Description.data,
            event.Website = form.Website.data,
            event.Link_to_position = form.Link_to_position.data,
            event.Link_to_regestration = form.Link_to_regestration.data,
            event.Form_of_holding = form.Form_of_holding.data,
            event.Status = form.Status.data,
            event.Direction = form.Direction.data,
            event.Age = form.Age.data,
            event.Class = form.Class.data,
            event.Note = form.Note.data,
            event.Number_of_participants = form.Number_of_participants.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('event.html',
                           title='Редактирование события',
                           form=form
                           )


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
        redirect('/add_student')
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
    for resul in db_sess.query(Results).all():
        student_info = db_sess.query(Studies_it_cube).filter(Studies_it_cube.Id_student == resul.Id_student).first()
        student = db_sess.query(Students).filter(Students.id == student_info.Id_student).first().FIO

        employeer = db_sess.query(Employees).filter(Employees.id == resul.Id_employer).first().FIO

        direction = db_sess.query(Directions).filter(Directions.id == student_info.Direction).first().Direction

        id_event = db_sess.query(Stages_Events).filter(Stages_Events.id == resul.Id_stage_event).first().Id_event
        event = db_sess.query(Event).filter(Event.id == id_event).first().Name_of_event

        res = db_sess.query(Achievement).filter(Achievement.id == resul.Id_achievement).first().Achievement

        res_dict[resul.id] = [student, employeer, direction, event, res]

    return render_template('reports.html', all_reports=res_dict)


def main():
    db_session.global_init("db/it-cube-data.db")
    app.run()


if __name__ == '__main__':
    main()
