from flaskapp import db, login_manager, create_app
from flask import current_app,  url_for
from datetime import datetime
from flask_login import UserMixin
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import pandas as pd

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60),nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    active_for_tournament = db.Column(db.Integer, nullable=True, default=0)
    venmo = db.Column(db.String(120))
    paypal = db.Column(db.String(120))

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"User('{self.title}', '{self.date_posted}')"

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    players = db.relationship('DraftedPlayer', backref='team', lazy=True)
    current_score = db.Column(db.String(5))
    current_score_int = db.Column(db.Integer)
    today_score = db.Column(db.String(5))
    today_score_int = db.Column(db.Integer)
    holes_remaining = db.Column(db.Integer)
    cut_players = db.Column(db.Integer)
    fourth_score = db.Column(db.String(200))


class DraftedPlayer(db.Model):
    __tablename__ = 'DraftedPlayer'
    id = db.Column("id", db.Integer, primary_key=True)
    pos = db.Column(db.String(5))
    player = db.Column(db.String(100))
    to_par = db.Column(db.String(100))
    to_par_int = db.Column(db.Integer)
    today = db.Column(db.String(50))
    today_int = db.Column(db.Integer)
    thru = db.Column(db.String(5))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    tee_time = db.Column(db.String(40))
    db.relationship('available_player', backref='player_info', lazy=True)

    def __repr__(self):
        return f"Drafted ({self.player})"

class AvailablePlayer(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    player = db.Column(db.String(100), nullable=False)
    flag_image = db.Column(db.String(20), nullable=False, default='default.jpg')
    player_image = db.Column(db.String(20), nullable=False, default='static/images/default_headshot.jpg')
    world_rank = db.Column(db.Integer, nullable=True, default="N/A")
    odds = db.Column(db.String(20), nullable=False, default='N/A')
    odds_int = db.Column(db.Integer, default=999999)
    country = db.Column(db.String(50))
    active = db.Column(db.Integer, default=0)
    tee_time = db.Column(db.String(40))
    pos = db.Column(db.String(5))
    to_par = db.Column(db.String(100))
    to_par_int = db.Column(db.Integer)
    today = db.Column(db.String(50))
    today_int = db.Column(db.Integer)
    thru = db.Column(db.String(5))
    holes_remaining = db.Column(db.Integer)
    r1 = db.Column(db.Integer)
    r2 = db.Column(db.Integer)
    r3 = db.Column(db.Integer)
    r4 = db.Column(db.Integer)
    cut_projected = db.Column(db.Integer)
    cut_final = db.Column(db.Integer)
    drafted_flag = db.Column(db.Integer, default=0)
    drafted_player = db.Column(db.Integer, db.ForeignKey('DraftedPlayer.id'), nullable=True)
