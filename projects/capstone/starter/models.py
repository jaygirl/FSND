import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

db = SQLAlchemy()

database_name = "cast_agency"
database_password = os.getenv("DATABASE_PASSWORD")
database_path = "postgres://{}:{}@{}/{}".format('postgres', database_password,
                                                'localhost:5432', database_name)


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


class Movie(db.Model):
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    release_date = db.Column(db.DateTime, default=datetime.utcnow)
    movie_actor = db.relationship('MovActor', backref='movies', lazy=True)

    def __repr__(self):
        return f"<Movie id='{self.id}' title='{self.title}'>"

    def __init__(self, title, release):
        self.title = title
        self.release = release

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'title': self.title,
            'release': self.release,
        }

class Actor(db.Model):
    __tablename__ = 'actors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    movie_actor = db.relationship('MovActor', backref='actors', lazy=True)


    def __repr__(self):
        return f"<Actor id='{self.id}' name='{self.name}'>"

    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return{
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender
        }


class MovActor(db.Model):
  """docstring for Show"""
  __tablename__ = 'movactor'
  id = id = db.Column(db.Integer, primary_key=True)
  actor_id = db.Column(db.Integer, db.ForeignKey('actors.id'), nullable=False) 
  movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
