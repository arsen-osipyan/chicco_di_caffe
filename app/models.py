from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    recipes = db.relationship('Recipe', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {} {}>'.format(self.username, self.email)


class Sort(db.Model):  # SearchableMixin, db.Model):
    __searchable__ = ['title', 'bouquet']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60), index=True, unique=True)
    bouquet = db.Column(db.String(120))
    description = db.Column(db.Text())
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '{}'.format(self.title)


class Recipe(db.Model):
    title = db.Column(db.String(200), index=True, unique=True)
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sort_id = db.Column(db.Integer, db.ForeignKey('sort.id'))

    coffee_mass = db.Column(db.Float)
    water_mass = db.Column(db.Integer)
    water_temp = db.Column(db.Integer)
    grinding = db.Column(db.Float)

    acidity = db.Column(db.Integer)
    tds = db.Column(db.Integer)

    body = db.Column(db.Text())

    def __repr__(self):
        return '<Recipe {} {}>'.format(self.id, Sort.query.filter_by(id=self.sort_id).first().title)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
