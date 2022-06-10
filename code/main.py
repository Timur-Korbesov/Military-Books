import os
import datetime
import sqlite3
import fitz
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
from forms.result import ResultsForm, EventForm, AddAchievement, AddPhoto
from forms.event import AddEventForm, AddStageForm, update_event, AddDirection
from forms.reports import FiltersForm, update_reports
from forms import result
from forms.students_forms import AddStudents, AddStudyItCube, update_studies_cube

from styles_py import styles_consts

consts = dict()
consts['carousel'] = [styles_consts.carousel_block_active, styles_consts.carousel_block, styles_consts.carousel_img,
                      styles_consts.carousel_text, styles_consts.carousel_block_not_ev]

app = Flask(__name__)
app.config['SECRET_KEY'] = 'it-cube-ol15'
login_manager = LoginManager()
login_manager.init_app(app)


# Функция возврата фотографии в бинарном виде для сохранения в бд
def download_photo(f):
    filename = secure_filename(f.filename)
    blob_data = None
    if filename:
        file_path = 'static/img/' + filename
        f.save(file_path)
        if '.pdf' in filename:
            file_path_photo = ''
            file_path = os.path.abspath('static/img/paris_1.pdf')
            pdf_file = fitz.open(file_path)
            location = os.path.abspath('static/img/')
            number_of_pages = len(pdf_file)
            for current_page_index in range(number_of_pages):
                for img_index, img in enumerate(pdf_file.getPageImageList(current_page_index)):
                    xref = img[0]
                    image = fitz.Pixmap(pdf_file, xref)
                    if image.n < 5:
                        image.writePNG("{}/photo{}-{}.jpeg".format(location, current_page_index, img_index))
                    else:
                        new_image = fitz.Pixmap(fitz.csRGB, image)
                        new_image.writePNG("{}/photo{}-{}.jpeg".format(location, current_page_index, img_index))
                    file_path_photo = "{}/photo{}-{}.jpeg".format(location, current_page_index, img_index)
            with open(file_path_photo, 'rb') as file:
                blob_data = file.read()
            os.remove(file_path_photo)
            pdf_file.close()
        else:
            with open(file_path, 'rb') as file:
                blob_data = file.read()
        os.remove(file_path)
    return blob_data


# Автовход
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(Employees).get(user_id)


# Выход
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# Вход
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


# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
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


# Главная
@app.route("/index")
@app.route("/")
def index():
    db_sess = db_session.create_session()
    even = db_sess.query(Event).all()
    events_actually = []
    now_date = datetime.date.today()
    for ev in even:
        # Беру все значения из связующей таблицы Stages_Events
        stages_id = db_sess.query(Stages_Events).filter(ev.id == Stages_Events.Id_event).all()
        # Прохожусь, нахожу этап по id, сравниваю даты, чтобы найти актуальную
        for stage_id in stages_id:
            st = db_sess.query(Stages).filter(stage_id.Id_stage == Stages.id).first()
            if st.Date_end >= now_date:
                path = 'static/img/' + 'photo_ev' + str(ev.id) + '.jpeg'
                if not (os.path.exists(path)):
                    if ev.Photo:
                        with open(path, 'wb') as file:
                            file.write(ev.Photo)
                        path = 'img/' + 'photo_ev' + str(ev.id) + '.jpeg'
                    else:
                        path = None
                events_actually.append([ev, path])
                break
    return render_template("index.html", title='Главная', events_actually=events_actually,
                           styles=consts['carousel'])


# Все мероприятия
@app.route("/events")
def events():
    db_sess = db_session.create_session()
    even = db_sess.query(Event).all()
    status = db_sess.query(Status).all()
    form_of_hold = db_sess.query(Form_of_Holding).all()
    direct = db_sess.query(Directions).all()
    return render_template("events.html", title='Мероприятия', events=even, status=status,
                           form_of_hold=form_of_hold, direct=direct)


# Подробности о мероприятии
@app.route("/event_more/<int:id>")
@login_required
def event_more(id):
    db_sess = db_session.create_session()
    ev = db_sess.query(Event).filter(Event.id == id).first()
    empls_partic = db_sess.query(Participation_employees).filter(ev.id == Participation_employees.Id_event).all()
    employes = []
    for empl in empls_partic:
        empls = db_sess.query(Employees).filter(Employees.id == empl.Id_employer).first()
        employes.append(empls.FIO)
    status = db_sess.query(Status).filter(ev.Status == Status.id).first()
    form_hold = db_sess.query(Form_of_Holding).filter(ev.Form_of_holding == Form_of_Holding.id).first()
    direction = db_sess.query(Directions).filter(ev.Direction == Directions.id).first()
    stages_id = db_sess.query(Stages_Events).filter(ev.id == Stages_Events.Id_event).all()
    stages = []
    for stage_id in stages_id:
        stag = db_sess.query(Stages).filter(stage_id.Id_stage == Stages.id).first()
        stages.append(stag)

    data_blob = ev.Photo
    path = 'static/img/' + 'photo_ev' + str(id) + '.jpeg'
    if not (os.path.exists(path)):
        with open(path, 'wb') as file:
            file.write(data_blob)

    return render_template('event_more.html', title='Подробности мероприятия',
                           event=ev, empl_partic=empls_partic, status=status,
                           form_hold=form_hold, direction=direction, employees=employes,
                           stages=stages, path=path)


# Добавление мероприятия
@app.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    form = AddEventForm()
    # Обновляю поля выбора в форме SelectField
    update_event(form.Form_of_holding, form.Status, form.Direction, form.Employer)
    if form.is_submitted():
        db_sess = db_session.create_session()
        # Получаю фото
        f = request.files['Photo']
        blob_data = None
        if secure_filename(f.filename):
            path = 'static/img/' + secure_filename(f.filename)
            f.save(path)
            with open(path, 'rb') as file:
                blob_data = file.read()
            os.remove(path)
        # Сохраняю класс Event в бд
        ev = Event(
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
            Number_of_participants=form.Number_of_participants.data,
            Photo=blob_data
        )
        db_sess.add(ev)
        db_sess.commit()
        # Заполняю связующую таблицу Participation_employees
        event_id = db_sess.query(Event).all()[-1]
        partic_empl = Participation_employees(
            Id_event=event_id.id,
            Id_employer=form.Employer.data,
            Note=None
        )
        db_sess.add(partic_empl)
        db_sess.commit()
        ev = db_sess.query(Event).filter(Event.Name_of_event == event.Name_of_event).first()
        return redirect(f'/event_more/{ev.id}')
    return render_template('event.html', title='Добавление мероприятия', photo='Фото мероприятия',
                           name='добавления', form=form)


# Редактирование мероприятия
@app.route("/event/<int:id>", methods=['GET', 'POST'])
@login_required
def event(id):
    form = AddEventForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        ev = db_sess.query(Event).filter(Event.id == id).first()
        employer_id = db_sess.query(Participation_employees).filter(
            Participation_employees.Id_event == ev.id).first().Id_employer
        if ev:
            form.Name_of_event.data = ev.Name_of_event
            form.Organizer.data = ev.Organizer
            form.Description.data = ev.Description
            form.Website.data = ev.Website
            form.Link_to_position.data = ev.Link_to_position
            form.Link_to_regestration.data = ev.Link_to_regestration
            # Заполнение формы выбора формы проведения
            f_of_holds = [0]
            for form_hold in db_sess.query(Form_of_Holding).all():
                if form_hold.id == ev.Form_of_holding:
                    f_of_holds[0] = [form_hold.id, form_hold.Form]
                else:
                    f_of_holds.append([form_hold.id, form_hold.Form])
            form.Form_of_holding.choices = f_of_holds
            # Заполнение формы выбора статуса мероприятия
            statuses = [0]
            for st in db_sess.query(Status).all():
                if st.id == ev.Status:
                    statuses[0] = [st.id, st.Status_name]
                else:
                    statuses.append([st.id, st.Status_name])
            form.Status.choices = statuses
            # Заполнение формы выбора направления мероприятия
            directions = [0]
            for direct in db_sess.query(Directions).all():
                if direct.id == ev.Direction:
                    directions[0] = [direct.id, direct.Direction]
                else:
                    directions.append([direct.id, direct.Direction])
            form.Direction.choices = directions
            # Заполнение формы добавления наставника
            empls = [0]
            for empl in db_sess.query(Employees).all():
                if empl.id == employer_id:
                    empls[0] = [empl.id, empl.FIO]
                else:
                    empls.append([empl.id, empl.FIO])
            form.Employer.choices = empls
            form.Age.data = ev.Age
            form.Class.data = ev.Class
            form.Note.data = ev.Note
            form.Number_of_participants.data = ev.Number_of_participants
        else:
            abort(404)
    if form.is_submitted():
        db_sess = db_session.create_session()
        ev = db_sess.query(Event).filter(Event.id == id).first()
        if ev:
            f = request.files['Photo']
            blob_data = None
            if secure_filename(f.filename):
                path = 'static/img/' + secure_filename(f.filename)
                f.save(path)
                with open(path, 'rb') as file:
                    blob_data = file.read()
                os.remove(path)
            ev.Name_of_event = form.Name_of_event.data
            ev.Organizer = form.Organizer.data
            ev.Description = form.Description.data
            ev.Website = form.Website.data
            ev.Link_to_position = form.Link_to_position.data
            ev.Link_to_regestration = form.Link_to_regestration.data
            ev.Form_of_holding = form.Form_of_holding.data
            ev.Status = form.Status.data
            ev.Direction = form.Direction.data
            ev.Age = form.Age.data
            ev.Class = form.Class.data
            ev.Note = form.Note.data
            ev.Number_of_participants = form.Number_of_participants.data
            if blob_data:
                ev.Photo = blob_data
            db_sess.commit()
            return redirect(f'/event_more/{ev.id}')
        else:
            abort(404)
    return render_template('event.html',
                           title='Редактирование мероприятия',
                           name='редактирования',
                           photo='Выбрать другое фото',
                           form=form
                           )


# Добавление нового направления
@app.route('/add_direction/<string:tp>/<int:page>', methods=['GET', 'POST'])
@login_required
def add_direction(tp, page):
    form = AddDirection()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        direction = Directions(
            Direction=form.direction.data
        )
        db_sess.add(direction)
        db_sess.commit()
        if tp == 'event':
            return redirect('/add_event')
        return redirect(f'/add_studies_it_cube/{page}')
    return render_template('add_direction.html', title='Добавление направления',
                           form=form)


# Добавлнеие нового этапа для мероприятия
@app.route('/add_event_stage/<int:id>', methods=['GET', 'POST'])
@login_required
def add_event_stage(id):
    form = AddStageForm()
    db_sess = db_session.create_session()
    ev = db_sess.query(Event).filter(Event.id == id).first()
    if form.validate_on_submit():
        st = Stages(
            Stage=form.Stage.data,
            Date_begin=form.Date_begin.data,
            Date_end=form.Date_end.data
        )
        db_sess.add(st)
        db_sess.commit()
        stage_id = db_sess.query(Stages).all()[-1]
        stage_event = Stages_Events(
            Id_event=id,
            Id_stage=stage_id.id
        )
        db_sess.add(stage_event)
        db_sess.commit()
        return redirect(f'/event_more/{id}')
    return render_template('event_stage.html', title='Добавление этапа', event=ev,
                           form=form, edit_or_add='добавления')


# Редактирование этапа
@app.route("/stage/<int:id>", methods=['GET', 'POST'])
@login_required
def stage(id):
    form = AddStageForm()
    db_sess = db_session.create_session()
    event_id = db_sess.query(Stages_Events).filter(Stages_Events.Id_stage == id).first().Id_event
    ev = db_sess.query(Event).filter(Event.id == event_id).first()
    if request.method == "GET":
        st = db_sess.query(Stages).filter(Stages.id == id).first()
        if st:
            form.Stage.data = st.Stage
            form.Date_begin.data = st.Date_begin
            form.Date_end.data = st.Date_end
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        st = db_sess.query(Stages).filter(Stages.id == id).first()
        if st:
            st.Stage = form.Stage.data
            st.Date_begin = form.Date_begin.data
            st.Date_end = form.Date_end.data
            db_sess.commit()
            return redirect(f'/event_more/{ev.id}')
        else:
            abort(404)
    return render_template('event_stage.html',
                           title='Редактирование этапа', event=ev,
                           form=form, edit_or_add='редактирования'
                           )


# Вкладка с получением id выбранного мероприятия для показа результатов
@app.route('/results_event', methods=['GET', 'POST'])
def results_event():
    form_event = EventForm()
    con = sqlite3.connect('./db/it-cube-data.db')
    cur = con.cursor()
    results_events = cur.execute(result.quare_event).fetchall()
    form_event.event.choices = [(ev[0], ev[1]) for ev in results_events]
    if form_event.is_submitted():
        event_id = form_event.event.data
        return redirect(f'/results/{event_id}')
    return render_template('results_event.html', title='Выбор мероприятия',
                           form=form_event)


# Результаты
@app.route('/results/<int:id>', methods=['GET', 'POST'])
def results(id):
    db_sess = db_session.create_session()
    ev = db_sess.query(Event).filter(id == Event.id).first()

    stages_id = db_sess.query(Stages_Events).filter(id == Stages_Events.Id_event).all()
    results_stages = []
    for stage_id in stages_id:
        st = db_sess.query(Stages).filter(stage_id.Id_stage == Stages.id).first()
        resultss = db_sess.query(Results).filter(stage_id.id == Results.Id_stage_event).all()
        res = []
        for r in resultss:
            stud = db_sess.query(Students).filter(r.Id_student == Students.id).first()
            employer = db_sess.query(Employees).filter(r.Id_employer == Employees.id).first()
            achievement = db_sess.query(Achievement).filter(r.Id_achievement == Achievement.id).first()
            photoo = r.Diploms
            res_id = r.id
            res.append([stud, employer, achievement, photoo, res_id])
        results_stages.append([st, res])
    return render_template('results.html', title='Просмотр резульата',
                           event=ev, res_stages=results_stages, event_id=id)


# Добавление результатов
@app.route('/add_results/<int:id>', methods=['GET', 'POST'])
@login_required
def add_results(id):
    form_result = ResultsForm()
    db_sess = db_session.create_session()
    con = sqlite3.connect('./db/it-cube-data.db')
    cur = con.cursor()
    ev = db_sess.query(Event).filter(id == Event.id).first().Name_of_event
    stages_id = db_sess.query(Stages_Events).filter(id == Stages_Events.Id_event).all()
    results_stages = []
    for stage_id in stages_id:
        st = db_sess.query(Stages).filter(stage_id.Id_stage == Stages.id).first()
        results_stages.append(st)
    form_result.stage.choices = [(st.id, st.Stage) for st in results_stages]

    results_employer = cur.execute(result.quare_employer).fetchall()
    form_result.FIO_employer.choices = [(employer[0], employer[1]) for employer in results_employer]

    results_student = cur.execute(result.quare_student).fetchall()
    form_result.FIO.choices = [(stud[0], stud[1]) for stud in results_student]

    results_achievement = cur.execute(result.quare_achievement).fetchall()
    form_result.achievement.choices = [(achiev[0], achiev[1]) for achiev in results_achievement]

    quare_stages_events = f"""
                    SELECT id FROM Stages_Events
                    WHERE id_event == ? AND id_stage == ?
                    """
    result_stage_id = cur.execute(quare_stages_events, (id, form_result.stage.data)).fetchall()
    if form_result.is_submitted():
        f = request.files['achievement_photo']
        blob_data = download_photo(f)
        res = Results(
            Id_stage_event=result_stage_id[0][0],
            Id_student=form_result.FIO.data,
            Id_achievement=form_result.achievement.data,
            Id_employer=form_result.FIO_employer.data,
            Diploms=blob_data
        )
        db_sess.add(res)
        db_sess.commit()
        return redirect(f'/results/{id}')
    return render_template('add_results.html', title='Добавление результата',
                           edit_or_add='добавления', form=form_result, event=ev,
                           file_label='Выбрать файл достижения')


# Редактирование результата
@app.route('/redact_results/<int:id_event>/<int:id_result>', methods=['GET', 'POST'])
@login_required
def redact_results(id_event, id_result):
    form = ResultsForm()
    db_sess = db_session.create_session()
    res = db_sess.query(Results).filter(Results.id == id_result).first()
    st_ev = db_sess.query(Stages_Events).filter(Stages_Events.id == res.Id_stage_event).first()
    ev = db_sess.query(Event).filter(Event.id == id_event).first()
    if request.method == "GET":
        st = db_sess.query(Stages).filter(Stages.id == st_ev.Id_stage).first()
        if res:
            stages = [[st.id, st.Stage]]
            for st_id in db_sess.query(Stages_Events).filter(Stages_Events.Id_event == id_event).all():
                s = db_sess.query(Stages).filter(Stages.id == st_id.Id_stage).first()
                if s not in stages:
                    stages.append([s.id, s.Stage])
            form.stage.choices = stages
            stud = [0]
            for stude in db_sess.query(Students).all():
                if stude.id == res.Id_student:
                    stud[0] = [stude.id, stude.FIO]
                else:
                    stud.append([stude.id, stude.FIO])
            form.FIO.choices = stud
            achiev = [0]
            for ach in db_sess.query(Achievement).all():
                if ach.id == res.Id_achievement:
                    achiev[0] = [ach.id, ach.Achievement]
                else:
                    achiev.append([ach.id, ach.Achievement])
            form.achievement.choices = achiev
            empls = [0]
            for empl in db_sess.query(Employees).all():
                if empl.id == res.Id_employer:
                    empls[0] = [empl.id, empl.FIO]
                else:
                    empls.append([empl.id, empl.FIO])
            form.FIO_employer.choices = empls
        else:
            abort(404)
    if form.validate_on_submit():
        if res:
            f = request.files['achievement_photo']
            blob_data = download_photo(f)
            res.Id_student = form.FIO.data
            res.Id_achievement = form.achievement.data
            res.Id_employer = form.FIO_employer.data
            if blob_data:
                path = 'static/img/' + 'photo' + str(id_result) + '.jpeg'
                if os.path.exists(path):
                    os.remove(path)
                res.Diploms = blob_data
            db_sess.commit()
            return redirect(f'/results/{id_event}')
        else:
            abort(404)
    return render_template('add_results.html',
                           title='Редактирование результата', event=ev.Name_of_event,
                           form=form, edit_or_add='редактирования',
                           file_label='Выбрать другой файл достижения'
                           )


# Добавление нового вида достижения
@app.route('/add_achievement', methods=['GET', 'POST'])
@login_required
def add_achievement():
    form = AddAchievement()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        achievement = Achievement(
            Achievement=form.name_of_achievement.data
        )
        db_sess.add(achievement)
        db_sess.commit()
        return redirect('/results_event')
    return render_template('add_achievement.html', title='Добавление достижения',
                           form=form)


# Отчёты
@app.route('/reports', methods=['GET', 'POST'])
def reports():
    form = FiltersForm()
    db_sess = db_session.create_session()
    res_dict = {}
    update_reports(form.student, form.employer, form.direction, form.event, form.status, form.achievement)
    if form.is_submitted():
        student_id = form.student.data
        employer_id = form.employer.data
        event_id = form.event.data
        direction_id = form.direction.data
        status_id = form.status.data
        data_begin = form.data_begin.data
        data_end = form.data_end.data
        achievement_id = form.achievement.data
        for res in db_sess.query(Results).all():
            if (student_id != -1 and res.Id_student != student_id) or (
                    employer_id != -1 and res.Id_employer != employer_id) or (
                    achievement_id != -1 and res.Id_achievement != achievement_id):
                continue

            student_info = db_sess.query(Studies_it_cube).filter(
                Studies_it_cube.Id_student == res.Id_student).first()
            stud = db_sess.query(Students).filter(Students.id == student_info.Id_student).first().FIO

            employeer = db_sess.query(Employees).filter(Employees.id == res.Id_employer).first().FIO

            id_event_stage = db_sess.query(Stages_Events).filter(Stages_Events.id == res.Id_stage_event).first()
            ev = db_sess.query(Event).filter(Event.id == id_event_stage.Id_event).first()
            if (event_id != -1 and ev.id != event_id) or (
                    direction_id != -1 and ev.Direction != direction_id) or (status_id != -1 and status_id != ev.Status):
                continue
            stagee = db_sess.query(Stages).filter(Stages.id == id_event_stage.Id_stage).first()

            direction = db_sess.query(Directions).filter(Directions.id == ev.Direction).first().Direction

            if status_id == -1:
                status = db_sess.query(Status).filter(Status.id == ev.Status).first().Status_name
            else:
                status = db_sess.query(Status).filter(Status.id == status_id).first().Status_name

            date = stagee.Date_end
            if data_begin and date < data_begin:
                continue
            if data_end and date > data_end:
                continue

            achievement = db_sess.query(Achievement).filter(Achievement.id == res.Id_achievement).first().Achievement

            photoo = res.Diploms
            res_dict[res.id] = [stud, employeer, direction, ev.Name_of_event, stagee.Stage, status, date,
                                achievement, photoo]

    else:
        for res in db_sess.query(Results).all():
            student_info = db_sess.query(Studies_it_cube).filter(
                Studies_it_cube.Id_student == res.Id_student).first()
            stud = db_sess.query(Students).filter(Students.id == student_info.Id_student).first().FIO

            employeer = db_sess.query(Employees).filter(Employees.id == res.Id_employer).first().FIO

            id_event_stage = db_sess.query(Stages_Events).filter(Stages_Events.id == res.Id_stage_event).first()
            ev = db_sess.query(Event).filter(Event.id == id_event_stage.Id_event).first()
            st = db_sess.query(Stages).filter(Stages.id == id_event_stage.Id_stage).first()

            direction = db_sess.query(Directions).filter(Directions.id == ev.Direction).first().Direction

            status = db_sess.query(Status).filter(Status.id == ev.Status).first().Status_name

            date = db_sess.query(Stages).filter(Stages.id == st.id).first().Date_end

            achievement = db_sess.query(Achievement).filter(Achievement.id == res.Id_achievement).first().Achievement

            photoo = res.Diploms
            res_dict[res.id] = [stud, employeer, direction, ev.Name_of_event, st.Stage, status, date,
                                achievement, photoo]

    return render_template('reports.html', title='Отчёты',
                           all_reports=res_dict, form=form)


# Показ учеников
@app.route('/students')
def students():
    db_sess = db_session.create_session()

    res_dict = {}
    for stud in db_sess.query(Students).all():
        res_dict[stud.id] = [stud.FIO, stud.Date_of_birth, stud.Class, stud.Сertificate_DO, stud.Place_of_residence,
                             stud.School, stud.Number_phone_student, stud.Number_phone_parent,
                             stud.Gender, stud.Note]
    return render_template('students.html', title='Ученики', all_students=res_dict)


# Подробности об ученике
@app.route('/more_student/<int:id>')
def more_students(id):
    db_sess = db_session.create_session()
    stude = db_sess.query(Students).filter(Students.id == id).first()
    studies_it_cub = db_sess.query(Studies_it_cube).filter(Studies_it_cube.Id_student == stude.id).all()
    all_studies_it_cube = []
    for stud in studies_it_cub:
        direction = db_sess.query(Directions).filter(Directions.id == stud.Direction).first()
        employer = db_sess.query(Employees).filter(Employees.id == stud.Id_employer).first()
        all_studies_it_cube.append([stud, direction, employer])
    return render_template('students_more.html', title='Подробности об ученике',
                           student=stude, studies_it_cube=all_studies_it_cube)


# Редактирование учеников
@app.route("/student/<int:id>", methods=['GET', 'POST'])
@login_required
def student(id):
    form = AddStudents()
    if request.method == "GET":
        db_sess = db_session.create_session()
        stud = db_sess.query(Students).filter(Students.id == id).first()
        if stud:
            form.FIO.data = stud.FIO
            form.date_of_birth.data = stud.Date_of_birth
            form.class_number.data = stud.Class
            form.certificate_do.data = stud.Сertificate_DO
            form.place_of_residence.data = stud.Place_of_residence
            form.school.data = stud.School
            form.number_phone.data = stud.Number_phone_student
            form.number_phone_parent.data = stud.Number_phone_parent
            form.gender.data = stud.Gender
            form.note.data = stud.Note
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        stud = db_sess.query(Students).filter(Students.id == id).first()
        if stud:
            stud.FIO = form.FIO.data
            stud.Date_of_birth = form.date_of_birth.data
            stud.Class = form.class_number.data
            stud.Сertificate_DO = form.certificate_do.data
            stud.Place_of_residence = form.place_of_residence.data
            stud.School = form.school.data
            stud.Number_phone_student = form.number_phone.data
            stud.Number_phone_parent = form.number_phone_parent.data
            stud.Gender = form.gender.data
            stud.Note = form.note.data
            db_sess.commit()
            return redirect(f'/more_student/{stud.id}')
        else:
            abort(404)
    return render_template('add_student.html',
                           title='Редактирование информации об ученике',
                           form=form, title_h='редактирования')


# Добавление учеников
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
        student_id = db_sess.query(Students).filter(Students.FIO == new_student.FIO).first().id
        return redirect(f'/more_student/{student_id}')
    return render_template('add_student.html', form=form, title_h='добавления', title='Добавление учеников')


# Добавление направления, на котором учится ученик
@app.route('/add_studies_it_cube/<int:id>', methods=['GET', 'POST'])
@login_required
def add_studies_it_cube(id):
    form = AddStudyItCube()
    update_studies_cube(form.Direction, form.Id_employer)
    db_sess = db_session.create_session()
    stud = db_sess.query(Students).filter(Students.id == id).first()
    if form.validate_on_submit():
        stud = Studies_it_cube(
            Direction=form.Direction.data,
            Date_of_admission=form.Date_of_admission.data,
            Date_of_deductions=form.Date_of_deductions.data,
            Id_employer=form.Id_employer.data,
            Id_student=stud.id

        )
        db_sess.add(stud)
        db_sess.commit()
        return redirect(f'/more_student/{id}')
    return render_template('add_studies_it_cube.html', title='Добавление направления',
                           form=form, student=stud)


# Редактирование направления, на котором учится ученик
@app.route("/studies_it_cube/<int:id>", methods=['GET', 'POST'])
@login_required
def studies_it_cube(id):
    form = AddStudyItCube()
    db_sess = db_session.create_session()
    stud = db_sess.query(Studies_it_cube).filter(Studies_it_cube.id == id).first()
    stude = db_sess.query(Students).filter(Students.id == stud.Id_student).first()
    if request.method == "GET":
        if stud:
            # Заполнение формы выбора направления
            directions = [0]
            for direct in db_sess.query(Directions).all():
                if direct.id == stud.Direction:
                    directions[0] = [direct.id, direct.Direction]
                else:
                    directions.append([direct.id, direct.Direction])
            form.Direction.choices = directions
            form.Date_of_admission.data = stud.Date_of_admission
            form.Date_of_deductions.data = stud.Date_of_deductions
            # Заполнение формы выбора наставника
            # Заполнение формы добавления наставника
            empls = [0]
            for empl in db_sess.query(Employees).all():
                if empl.id == stud.Id_employer:
                    empls[0] = [empl.id, empl.FIO]
                else:
                    empls.append([empl.id, empl.FIO])
            form.Id_employer.choices = empls
        else:
            abort(404)
    if form.validate_on_submit():
        if stud:
            stud.Direction = form.Direction.data
            stud.Date_of_admission = form.Date_of_admission.data
            stud.Date_of_deductions = form.Date_of_deductions.data
            stud.Id_employer = form.Id_employer.data
            db_sess.commit()
            return redirect(f'/more_student/{stude.id}')
        else:
            abort(404)
    return render_template('add_studies_it_cube.html',
                           title='Редактирование направления ученика',
                           form=form, student=stude
                           )


# Показ сотрудников
@app.route('/employees')
@login_required
def employees():
    db_sess = db_session.create_session()
    res_dict = {}
    for empl in db_sess.query(Employees).all():
        status = db_sess.query(StatusEmployer).filter(StatusEmployer.id == empl.Status).first()
        res_dict[empl.id] = [empl.FIO, empl.Email, empl.Hashed_password, empl.Date_of_birth,
                             empl.Place_of_residence, empl.Number_phone, empl.Gender, status.Role,
                             empl.Note]
    return render_template('employees.html', title='Сотрудники',
                           all_employees=res_dict)


# Отображение фото
@app.route('/photo/<int:id>', methods=['GET', 'POST'])
@login_required
def photo(id):
    db_sess = db_session.create_session()
    data_blob = db_sess.query(Results).filter(Results.id == id).first().Diploms
    path = 'static/img/' + 'photo' + str(id) + '.jpeg'
    if not (os.path.exists(path)):
        with open(path, 'wb') as file:
            file.write(data_blob)
    return render_template('photo.html', path=path)


# Добавление фото
@app.route('/add_photo/<int:id_event>/<int:id_result>', methods=['GET', 'POST'])
@login_required
def add_photo(id_event, id_result):
    form = AddPhoto()
    db_sess = db_session.create_session()
    ev = db_sess.query(Event).filter(Event.id == id_event).first()
    res = db_sess.query(Results).filter(Results.id == id_result).first()
    st = db_sess.query(Stages).filter(Stages.id == db_sess.query(Stages_Events).filter(
        Stages_Events.id == res.Id_stage_event).first().Id_stage).first()
    if form.is_submitted():
        f = request.files['achievement_photo']
        blob_data = download_photo(f)
        print(blob_data)
        res.Diploms = blob_data
        db_sess.commit()
        return redirect(f'/results/{id_event}')
    return render_template('add_photo.html', event=ev, result=res, form=form, stage=st.Stage)


# Экспорты в xml
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

    data = pd.DataFrame(
        {col1: list1, col2: list2, col3: list3, col4: list4, col5: list5, col6: list6, col7: list7, col8: list8,
         col9: list9, col10: list10, col11: list11})

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

    data = pd.DataFrame(
        {col1: list1, col2: list2, col3: list3, col4: list4, col5: list5, col6: list6, col7: list7, col8: list8})

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
    list9 = []

    col1 = "№"
    col2 = "Ученик"
    col3 = "Наставник"
    col4 = "Направление"
    col5 = "Мероприятие"
    col6 = "Этап"
    col7 = "Статус"
    col8 = "Дата"
    col9 = "Результат"

    db_sess = db_session.create_session()
    for num, res in enumerate(db_sess.query(Results).all()):
        student_info = db_sess.query(Studies_it_cube).filter(Studies_it_cube.Id_student == res.Id_student).first()
        stud = db_sess.query(Students).filter(Students.id == student_info.Id_student).first().FIO

        employeer = db_sess.query(Employees).filter(Employees.id == res.Id_employer).first().FIO

        id_event = db_sess.query(Stages_Events).filter(Stages_Events.id == res.Id_stage_event).first().Id_event
        ev_ = db_sess.query(Event).filter(Event.id == id_event).first()
        ev = ev_.Name_of_event

        direction = db_sess.query(Directions).filter(Directions.id == ev_.Direction).first().Direction

        id_stage = db_sess.query(Stages_Events).filter(Stages_Events.Id_event == id_event).first().Id_stage
        stage_ = db_sess.query(Stages).filter(Stages.id == id_stage).first()
        dat = stage_.Date_end
        stag = stage_.Stage

        status_id = db_sess.query(Event).filter(Event.id == id_event).first().Status
        status = db_sess.query(Status).filter(Status.id == status_id).first().Status_name

        achiev = db_sess.query(Achievement).filter(Achievement.id == res.Id_achievement).first().Achievement

        list1.append(num+1)
        list2.append(stud)
        list3.append(employeer)
        list4.append(direction)
        list5.append(ev)
        list6.append(stag)
        list7.append(status)
        list8.append(dat)
        list9.append(achiev)

    data = pd.DataFrame(
        {col1: list1, col2: list2, col3: list3, col4: list4, col5: list5, col6: list6, col7: list7, col8: list8, col9: list9})
    num = 0
    while True:
        if not (os.path.exists(f'all_exports/reports{num}.xlsx')):
            data.to_excel(f'all_exports/reports{num}.xlsx', sheet_name='sheet1', index=False)
            return redirect('/reports')
        else:
            num += 1


def main():
    db_session.global_init("db/it-cube-data.db")
    app.run()


if __name__ == '__main__':
    main()
