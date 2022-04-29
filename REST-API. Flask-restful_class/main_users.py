from flask import Flask
from flask_restful import Api

import users_resources
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)


def main():
    db_session.global_init("db/mars_explorer.sqlite")

    api.add_resource(users_resources.UsersListResource, '/api/v2/users')  # для списка объектов
    api.add_resource(users_resources.UsersResource,
                     '/api/v2/users/<int:user_id>')  # для одного объекта

    app.run()


if __name__ == '__main__':
    main()
