from flask import Flask, render_template, make_response, session, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import redirect

from data import db_session
from data.user import User
from forms.user import RegisterForm, LoginForm
from data.jobs import Jobs
from forms.jobs import JobsForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/index")
@app.route("/")
def index():
    jobs = None
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        jobs = db_sess.query(Jobs)
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
        user = db_sess.query(User).filter(User.email == form.email.data).first()
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
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            surname=form.surname.data,
            age=form.age.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/addjob',  methods=['GET', 'POST'])
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
    return render_template('addjob.html', title='Добавление работы',
                           form=form)

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
    db_session.global_init("db/mars.db")
    app.run()


if __name__ == '__main__':
    main()