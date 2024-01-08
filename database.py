from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()


class Countries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(255), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


def configure_database(app):
    dialect_driver = os.getenv('DIALECT_DRIVER')
    username = os.getenv('DBUSER')
    password = os.getenv('PASSWORD')
    host = os.getenv('HOST')
    dbname = os.getenv('DBNAME')

    db_credentials = (
        f"{dialect_driver}://{username}:{password}@{host}/{dbname}"
    )

    app.config['SQLALCHEMY_DATABASE_URI'] = db_credentials
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)


def create_table():
    db.create_all()


def send_to_db(df):
    for index, row in df.iterrows():
        new_entry = Countries(country=row['country'],
                              capacity=row['capacity'],
                              date=row['date'])
        db.session.add(new_entry)
    db.session.commit()
