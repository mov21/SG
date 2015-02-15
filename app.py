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

    def is_admin(self):
        return (self.user_type == 'admin')

    def is_debater(self):
        return (self.user_type == 'debater')

    def is_judge(self):
        return (self.user_type == 'judge')

    def is_tabmaster(self):
        return (self.user_type == 'tabmaster')

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


class Tabmaster(db.Model):
    __tablename__="tabmasters"
    id = db.Column('tabmaster_id', db.Integer, primary_key=True)
    name = db.Column(db.String(30))

    def __init__(self, name):
        self.name = name



@app.route('/admin/new_tabmaster', methods=['POST', 'GET'])
@login_required
def new_tabmaster():
    if request.method == 'POST':
        if not request.form['name']:
            flash('Name is required', 'error')
        else:
            _tabmaster = Tabmaster(request.form['name'])
            db.session.add(_tabmaster)
            db.session.commit()
            flash(_tabmaster.name + ' was successfully created')
            return redirect(url_for('admin'))
    return render_template('new_tabmaster.html')

@app.route('/admin/del_tabmaster', methods=['POST', 'GET'])
@login_required
def del_tabmaster():
    print 'name'
    if request.method == 'POST':
        if not request.form['name']:
            flash('Name is required', 'error')
        else:
            _tabmaster = Tabmaster.query.filter_by(name=request.form['name']).one()
            db.session.delete(_tabmaster)
            db.session.commit()
            return redirect(url_for('admin'))
    return render_template('del_tabmaster.html')

@app.route('/admin/del_<id>_direct', methods=['POST', 'GET'])
@login_required
def del_tabmaster_direct(id):
    print id
    if request.method == 'GET':
            print id
            _tabmaster = Tabmaster.query.get(id)
            db.session.delete(_tabmaster)
            db.session.commit()
            flash('Tab Master Successfully deleted.')
    return redirect(url_for('admin'))


@app.route('/admin/update_<id>tabmaster', methods=['POST', 'GET'])
@login_required
def update_tabmaster(id):
    tabmaster_item = Tabmaster.query.get(id)
    tabmaster_id = tabmaster_item.id
    if request.method == 'GET':
        print "get"
        return render_template('view_tabmaster.html')
    print "post"
    tabmaster_item.name = request.form['name']
    db.session.commit()
    flash(tabmaster_item.name+' was successfully updated')
    return redirect(url_for('admin'))


@app.route('/admin')
def admin():
    return render_template('admin.html', tabmasters = Tabmaster.query.order_by(Tabmaster.id))    


class Game(db.Model):
    __tablename__= "games"
    id = db.Column('game_id', db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    goverment_id= db.Column(db.Integer, db.ForeignKey('teams.team_id'))
    oposition_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'))
    round = db.Column(db.String(30))
    time = db.Column(db.DateTime)

    def __init__(self, name):
        self.name = name


@app.route('/')
@login_required
def home():
    if current_user.user_type == 'admin':
        return render_template('admin.html')
	return render_template('home.html')


@app.route('/program')
@login_required
def program():
    return render_template('program.html')

@app.route('/about')
@login_required
def about_sfantu_gheorghe():
    return render_template('about_sfantu_gheorghe.html')


@app.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    user = User( request.form['password'],request.form['email'],request.form['user_type'])
    db.session.add(user)
    db.session.commit()
    flash('User successfully registered')
    return redirect(url_for('login'))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    email = request.form['email']
    password = request.form['password']
    remember_me = False
    if 'remember_me' in request.form:
        remember_me = True
    registered_user = User.query.filter_by(email=email).first()
    if registered_user is None:
        flash('Username is invalid' , 'error')
        return redirect(url_for('login'))
    if not registered_user.check_password(password):
        flash('Password is invalid','error')
        return redirect(url_for('login'))
    login_user(registered_user, remember = remember_me)

    if registered_user.user_type == 'admin':
        print "Admin"
        return redirect(url_for('admin'))
    if registered_user.user_type == 'tabmaster':
        print "Tabmaster"
        return redirect(url_for('tabmaster'))
    return redirect(url_for('home'))



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home')) 

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
