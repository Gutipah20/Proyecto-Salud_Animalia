import os
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db=SQLAlchemy()
ma=Marshmallow()

def configure_db(app):
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    namecontainer = os.getenv('DB_NAME_CONTAINER')
    namedb = os.getenv('DB_NAME')

    if not all([user, password, namecontainer, namedb]):
        raise ValueError("Faltan variables de entorno: DB_USER, DB_PASSWORD, DB_NAME_CONTAINER, DB_NAME")

    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user}:{password}@{namecontainer}/{namedb}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    db.init_app(app)
    ma.init_app(app)