import os
import datetime
import sqlite3
import pandas as pd

from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, login_required, logout_user
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
    events_actually = []
    now_date = datetime.date.today()
    for ev in events:
        stages_id = db_sess.query(Stages_Events).filter(ev.id == Stages_Events.Id_event).all()
        for stage_id in stages_id:
            st = db_sess.query(Stages).filter(stage_id.Id_stage == Stages.id).first()
            if st.Date_begin >= now_date:
                events_actually.append(ev)
                break
    status = db_sess.query(Status).all()
    form_of_hold = db_sess.query(Form_of_Holding).all()
    direct = db_sess.query(Directions).all()
    return render_template("index.html", events=events, status=status,
                           form_of_hold=form_of_hold, events_actually=events_actually,
                           direct=direct)


@app.route("/event_more/<int:id>")
@login_required
def event_more(id):
    db_sess = db_session.create_session()
    event = db_sess.query(Event).filter(Event.id == id).first()
    empls_partic = db_sess.query(Participation_employees).filter(event.id == Participation_employees.Id_event).all()
    employes = []
    for empl in empls_partic:
        empls = db_sess.query(Employees).filter(Employees.id == empl.Id_employer).first()
        employes.append(empls.FIO)
    status = db_sess.query(Status).filter(event.Status == Status.id).first()
    form_hold = db_sess.query(Form_of_Holding).filter(event.Form_of_holding == Form_of_Holding.id).first()
    direction = db_sess.query(Directions).filter(event.Direction == Directions.id).first()
    stages_id = db_sess.query(Stages_Events).filter(event.id == Stages_Events.Id_event).all()
    stages = []
    for stage_id in stages_id:
        stage = db_sess.query(Stages).filter(stage_id.Id_stage == Stages.id).first()
        stages.append(stage)
    return render_template('event_more.html', title='Подробности события',
                           event=event, empl_partic=empls_partic, status=status,
                           form_hold=form_hold, direction=direction, employees=employes,
                           stages=stages)


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
            Id_employer=form.Employer.data,
            Note=None
        )
        db_sess.add(partic_empl)
        db_sess.commit()
        return redirect('/')
    return render_template('event.html', title='Добавление события',
                           form=form)


@app.route('/add_event_stage/<int:id>', methods=['GET', 'POST'])
@login_required
def add_event_stage(id):
    form = AddStageForm()
    db_sess = db_session.create_session()
    event = db_sess.query(Event).filter(Event.id == id).first()
    if form.validate_on_submit():
        stage = Stages(
            Stage=form.Stage.data,
            Date_begin=form.Date_begin.data,
            Date_end=form.Date_end.data
        )
        db_sess.add(stage)
        db_sess.commit()
        stage_id = db_sess.query(Stages).all()[-1]
        stage_event = Stages_Events(
            Id_event=id,
            Id_stage=stage_id.id
        )
        db_sess.add(stage_event)
        db_sess.commit()
        return redirect(f'/event_more/{id}')
    return render_template('event_stage.html', title='Добавление этапа', event=event,
                           form=form, edit_or_add='добавления')


@app.route("/stage/<int:id>", methods=['GET', 'POST'])
@login_required
def stage(id):
    form = AddStageForm()
    db_sess = db_session.create_session()
    event_id = db_sess.query(Stages_Events).filter(Stages_Events.Id_stage == id).first().Id_event
    event = db_sess.query(Event).filter(Event.id == event_id).first()
    if request.method == "GET":
        stage = db_sess.query(Stages).filter(Stages.id == id).first()
        if stage:
            form.Stage.data = stage.Stage
            form.Date_begin.data = stage.Date_begin
            form.Date_end.data = stage.Date_end
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        stage = db_sess.query(Stages).filter(Stages.id == id).first()
        if stage:
            stage.Stage = form.Stage.data
            stage.Date_begin = form.Date_begin.data
            stage.Date_end = form.Date_end.data
            db_sess.commit()
            return redirect(f'/event_more/{event.id}')
        else:
            abort(404)
    return render_template('event_stage.html',
                           title='Редактирование этапа', event=event,
                           form=form, edit_or_add='редактирования'
                           )


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
            event.Name_of_event = form.Name_of_event.data
            event.Organizer = form.Organizer.data
            event.Description = form.Description.data
            event.Website = form.Website.data
            event.Link_to_position = form.Link_to_position.data
            event.Link_to_regestration = form.Link_to_regestration.data
            event.Form_of_holding = form.Form_of_holding.data
            event.Status = form.Status.data
            event.Direction = form.Direction.data
            event.Age = form.Age.data
            event.Class = form.Class.data
            event.Note = form.Note.data
            event.Number_of_participants = form.Number_of_participants.data
            db_sess.commit()
            return redirect(f'/event_more/{event.id}')
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
        res_dict[stud.id] = [stud.FIO, stud.Date_of_birth, stud.Class, stud.Сertificate_DO, stud.Place_of_residence,
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
    for result in db_sess.query(Results).all():
        student_info = db_sess.query(Studies_it_cube).filter(Studies_it_cube.Id_student == result.Id_student).first()
        student = db_sess.query(Students).filter(Students.id == student_info.Id_student).first().FIO

        employeer = db_sess.query(Employees).filter(Employees.id == result.Id_employer).first().FIO

        direction = db_sess.query(Directions).filter(Directions.id == student_info.Direction).first().Direction

        id_event = db_sess.query(Stages_Events).filter(Stages_Events.id == result.Id_stage_event).first().Id_event
        event = db_sess.query(Event).filter(Event.id == id_event).first().Name_of_event

        id_stage = db_sess.query(Stages_Events).filter(Stages_Events.Id_event == id_event).first().Id_stage
        date = db_sess.query(Stages).filter(Stages.id == id_stage).first().Date_end

        status_id = db_sess.query(Event).filter(Event.id == id_event).first().Status
        status = db_sess.query(Status).filter(Status.id == status_id).first().Status_name

        res = db_sess.query(Achievement).filter(Achievement.id == result.Id_achievement).first().Achievement

        res_dict[result.id] = [student, employeer, direction, event, status, date, res]

    return render_template('reports.html', all_reports=res_dict)


@app.route('/export_students')
def export_students():
    list1 = []
    list2 = []
    list3 = []
    list4 = []
    list5 = []
    list6 = []
    list7 = []
    list8 = []
    list9 = []
    list10 = []
    list11 = []

    col1 = "№"
    col2 = "ФИО"
    col3 = "Дата рождения"
    col4 = "Класс"
    col5 = "Сертификат ДО"
    col6 = "Место жительства"
    col7 = "Школа"
    col8 = "Номер телефона"
    col9 = "Номер телефона родителя"
    col10 = "Пол"
    col11 = "Примечание"

    db_sess = db_session.create_session()

    res_dict = {}
    for stud in db_sess.query(Students).all():
        res_dict[stud.id] = [stud.FIO, stud.Date_of_birth, stud.Class, stud.Сertificate_DO, stud.Place_of_residence,
                             stud.School, stud.Number_phone_student, stud.Number_phone_parent,
                             stud.Gender, stud.Note]

        list1.append(stud.id)
        list2.append(stud.FIO)
        list3.append(stud.Date_of_birth)
        list4.append(stud.Class)
        list5.append(stud.Сertificate_DO)
        list6.append(stud.Place_of_residence)
        list7.append(stud.School)
        list8.append(stud.Number_phone_student)
        list9.append(stud.Number_phone_parent)
        list10.append(stud.Gender)
        list11.append(stud.Note)

    data = pd.DataFrame({col1: list1, col2: list2, col3: list3, col4: list4, col5: list5, col6: list6, col7: list7, col8: list8, col9: list9, col10: list10, col11: list11})

    data.to_excel('all_exports/students.xlsx', sheet_name='sheet1', index=False)

    return render_template('students.html', all_students=res_dict)


@app.route('/export_employees')
def export_employees():
    list1 = []
    list2 = []
    list3 = []
    list4 = []
    list5 = []
    list6 = []
    list7 = []
    list8 = []

    col1 = "№"
    col2 = "ФИО"
    col3 = "Дата рождения"
    col4 = "Место жительства"
    col5 = "Номер телефона"
    col6 = "Пол"
    col7 = "Статус"
    col8 = "Примечание"

    db_sess = db_session.create_session()
    res_dict = {}
    for empl in db_sess.query(Employees).all():
        status = db_sess.query(StatusEmployer).filter(StatusEmployer.id == empl.Status).first()
        res_dict[empl.id] = [empl.FIO, empl.Email, empl.Hashed_password, empl.Date_of_birth,
                             empl.Place_of_residence, empl.Number_phone, empl.Gender, status.Role,
                             empl.Note]

        list1.append(empl.id)
        list2.append(empl.FIO)
        list3.append(empl.Date_of_birth)
        list4.append(empl.Place_of_residence)
        list5.append(empl.Number_phone)
        list6.append(empl.Gender)
        list7.append(status.Role)
        list8.append(empl.Note)

    data = pd.DataFrame({col1: list1, col2: list2, col3: list3, col4: list4, col5: list5, col6: list6, col7: list7, col8: list8})

    data.to_excel('all_exports/employees.xlsx', sheet_name='sheet1', index=False)

    return render_template('employees.html', all_employees=res_dict)


@app.route('/export_reports')
def export_reports():
    list1 = []
    list2 = []
    list3 = []
    list4 = []
    list5 = []
    list6 = []
    list7 = []
    list8 = []

    col1 = "№"
    col2 = "Ученик"
    col3 = "Наставник"
    col4 = "Направление"
    col5 = "Мероприятие"
    col6 = "Статус"
    col7 = "Дата"
    col8 = "Результат"

    db_sess = db_session.create_session()
    res_dict = {}
    for result in db_sess.query(Results).all():
        student_info = db_sess.query(Studies_it_cube).filter(Studies_it_cube.Id_student == result.Id_student).first()
        student = db_sess.query(Students).filter(Students.id == student_info.Id_student).first().FIO

        employeer = db_sess.query(Employees).filter(Employees.id == result.Id_employer).first().FIO

        direction = db_sess.query(Directions).filter(Directions.id == student_info.Direction).first().Direction

        id_event = db_sess.query(Stages_Events).filter(Stages_Events.id == result.Id_stage_event).first().Id_event
        event = db_sess.query(Event).filter(Event.id == id_event).first().Name_of_event

        id_stage = db_sess.query(Stages_Events).filter(Stages_Events.Id_event == id_event).first().Id_stage
        date = db_sess.query(Stages).filter(Stages.id == id_stage).first().Date_end

        status_id = db_sess.query(Event).filter(Event.id == id_event).first().Status
        status = db_sess.query(Status).filter(Status.id == status_id).first().Status_name

        res = db_sess.query(Achievement).filter(Achievement.id == result.Id_achievement).first().Achievement


        res_dict[result.id] = [student, employeer, direction, event, status, date, res]

        list1.append(result.id)
        list2.append(student)
        list3.append(employeer)
        list4.append(direction)
        list5.append(event)
        list6.append(status)
        list7.append(date)
        list8.append(res)

    data = pd.DataFrame({col1: list1, col2: list2, col3: list3, col4: list4, col5: list5, col6: list6, col7: list7, col8: list8})

    data.to_excel('all_exports/reports.xlsx', sheet_name='sheet1', index=False)

    return render_template('reports.html', all_reports=res_dict)


def main():
    db_session.global_init("db/it-cube-data.db")
    app.run()


if __name__ == '__main__':
    main()
