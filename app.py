from datetime import datetime
from flask import Flask,session, request, flash, url_for, redirect, render_template, abort ,g,request
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.login import login_user , logout_user , current_user , login_required
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_pyfile('todoapp.cfg')
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'login'

class User(db.Model):
    __tablename__ = "users"
    id = db.Column('user_id',db.Integer , primary_key=True)
    password = db.Column('password' , db.String(250))
    email = db.Column('email',db.String(50),unique=True , index=True)
    user_type = db.Column('user_type',db.String(30))#cauta ce e index ?????!!!
    
    def __init__(self , password , email,user_type):
        self.set_password(password)
        self.email = email
        self.user_type = user_type
        self.registered_on = datetime.utcnow()

    def set_password(self , password):
        self.password = generate_password_hash(password)

    def check_password(self , password):
        return check_password_hash(self.password , password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r %r>' % (self.email,self.user_type)

class Debater(db.Model):
	__tablename__ = "debaters"
	id = db.Column('debater_id', db.Integer , primary_key=True)
	name = db.Column(db.String(30)) 
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
	team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'))

	def __init__(self, name):
		self.name = name 


class Team(db.Model):
	__tablename__ = "teams"
	id = db.Column('team_id', db.Integer, primary_key=True)
	name = db.Column(db.String(30)) 
	club_id = db.Column(db.Integer, db.ForeignKey('clubs.club_id'))
	debaters = db.relationship('Debater', backref='team', lazy='dynamic')

	def __init__(self, name):
		self.name = name

class Club(db.Model):
	__tablename__ = "clubs"
	id = db.Column('club_id', db.Integer, primary_key=True)
	teams = db.relationship('Team', backref='club', lazy='dynamic')
	name = db.Column(db.String(30))

	def __init__(self, name):
		self.name = name

class Judge(db.Model):
	__tablename__= "judges"
	id = db.Column('judge_id', db.Integer, primary_key=True)
	name = db.Column(db.String(30))
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
	club_id = db.Column(db.Integer, db.ForeignKey('clubs.club_id'))

	def __init__(self, name):
		self.name = name

@app.route('/')
@login_required
def home():
	return render_template('home.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index')) 

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)