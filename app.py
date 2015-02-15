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

#
#
#   Database Models
#
#

class User(db.Model):
    __tablename__ = "users"
    id = db.Column('user_id',db.Integer , primary_key=True)
    password = db.Column('password' , db.String(250))
    email = db.Column('email',db.String(50),unique=True , index=True)
    user_type = db.Column('user_type',db.String(30))#cauta ce e index ?????!!!
    
    def __init__(self, email, password, user_type):
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
    #oras si liceu 
	club_id = db.Column(db.Integer, db.ForeignKey('clubs.club_id'))
	debaters = db.relationship('Debater', backref='team', lazy='dynamic')

	def __init__(self, name):
		self.name = name

class Club(db.Model):
	__tablename__ = "clubs"
	id = db.Column('club_id', db.Integer, primary_key=True)
	teams = db.relationship('Team', backref='club', lazy='dynamic')
	name = db.Column(db.String(30),unique=True )

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
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    mail = db.Column(db.String(50))

    def __init__(self, name):
        self.name = name


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


#
#
#   Functions
#
#

def create_user(email,role):
    user = User(email,"123sdasee123!",role)
    print user.id
    db.session.add(user)
    db.session.commit()

def create_team(name):
    team = Team(name)
    db.session.add(team)
    db.session.commit()

def create_club(name):
    club = Club(name)
    db.session.add(club)
    db.session.commit()


#
#
#   Tabmaster debaters
#
#

@app.route('/tabmaster/debaters', methods=['GET'])
@login_required
def debaters():
    
    debaters = Debater.query.all()
    _debaters = []
    
    for debater in debaters:
        
        _debater = {}
        
        user = User.query.get(debater.user_id)
        team = Team.query.get(debater.team_id)
        club = Club.query.get(team.club_id)

        _debater['id'] = debater.id
        _debater['name'] = debater.name
        _debater['email'] = user.email
        _debater['team'] = team.name
        _debater['club'] = club.name
        _debaters.append(_debater)
    return render_template('debaters.html',debaters=_debaters)

#
#   CREATE
#

@app.route('/tabmaster/debaters/create', methods=['POST', 'GET'])
@login_required
def create_debater():

    if request.method == 'POST':
        
        #
        #   POST
        #

        if not request.form['name']:
            flash('Name is required', 'error')
        else:
            if not request.form['email']:
                flash('Email is required', 'error')
            else:
                if not request.form['team']:
                    flash('Team is required', 'error')
                else:
                    if not request.form['club']:
                        flash('Club is required', 'error')
                    else:

                        name = request.form['name']
                        email = request.form['email']
                        team = request.form['team']
                        club = request.form['club']
                        
                        debater = Debater(name)
                        
                        if User.query.filter_by(email = email).count() == 0:
                            create_user(email,"debater")
                        user = User.query.filter_by(email = email).one()
                        debater.user_id = user.id
                        
                        if Team.query.filter_by(name = team).count() == 0:
                            create_team(team)
                        team = Team.query.filter_by(name = team).one()   
                        debater.team_id = team.id
                        
                        if Club.query.filter_by(name = club).count() == 0:
                            create_club(club)
                        club = Club.query.filter_by(name = club).one()
                        team.club_id = club.id
                        
                        db.session.add(debater)
                        db.session.commit()
                        flash(debater.name + ' was successfully created')
                        return redirect(url_for('debaters'))
    
    #
    #   GET
    #

    return render_template('create_debater.html')

#
#   UPDATE
#

@app.route('/tabmaster/debaters/update/<int:id>', methods=['POST', 'GET'])
@login_required
def update_debater(id):

    debater = Debater.query.get(id)
    user = User.query.get(debater.user_id)
    team = Team.query.get(debater.team_id)
    club = Club.query.get(team.club_id)
    
    if request.method == 'GET':
        
        #
        #   GET
        #

        _debater = {}
        _debater['id'] = debater.id
        _debater['name'] = debater.name
        _debater['email'] = user.email
        _debater['team'] = team.name
        _debater['club'] = club.name
        return render_template('update_debater.html',debater = _debater)

    #
    #   POST
    #

    name = request.form['name']
    email = request.form['email']
    team_name = request.form['team']
    club_name = request.form['club']
    
    debater.name = name
    if(user.email != email):
        try:
            user.email = email
        except:
            flash('A different user has this email', 'error')
            return render_template('update_debater.html',debater = _debater)
    if(team.name != team_name):
        club_id = team.club_id
        create_team(team_name)
        team = Team.query.filter_by(name = team_name).one()
        debater.team_id = team.id
        team.club_id = club_id
    if(club.name != club_name):
        create_club(club_name)
        club = Club.query.filter_by(name = club_name).one()
        team.club_id = club.id    
    db.session.commit()
    flash(debater.name+' was successfully updated')
    return redirect(url_for('debaters'))

#
#   DELETE
#

@app.route('/tabmaster/debaters/delete/<id>', methods=['GET'])
def delete_debater(id):
    debater = Debater.query.get(id)
    name = debater.name
    db.session.delete(debater)
    db.session.commit()
    flash(name +'was successfully deleted.')
    return redirect(url_for('debaters'))

#
#
#   Tabmaster judges
#
#

@app.route('/tabmaster/judges', methods=['GET'])
@login_required
def judges():
    judges = Judge.query.all()
    _judges = []
    for judge in judges:
        _judge = {}
        
        user = User.query.get(judge.user_id)
        club = Club.query.get(judge.club_id)
        _judge['id'] = judge.id
        _judge['name'] = judge.name
        _judge['email'] = user.email
        _judge['club'] = club.name
        _judges.append(_judge)

    return render_template('judges.html',judges=_judges)

#
#   CREATE
#

@app.route('/tabmaster/judges/create', methods=['POST', 'GET'])
@login_required
def create_judge():
    if request.method == 'POST':
        #
        #   POST
        #
        if not request.form['name']:
            flash('Name is required', 'error')
        else:
            if not request.form['email']:
                flash('Email is required', 'error')
            else:
                if not request.form['club']:
                    flash('Club is required', 'error')
                else:
                    name = request.form['name']
                    email = request.form['email']
                    club = request.form['club']
                    
                    judge = Judge(name)
                        
                    if User.query.filter_by(email = email).count() == 0:
                        create_user(email,"judge")
                    user = User.query.filter_by(email = email).one()
                    judge.user_id = user.id
                           
                    if Club.query.filter_by(name = club).count() == 0:
                        create_club(club)
                    club = Club.query.filter_by(name = club).one()
                    judge.club_id = club.id
                        
                    db.session.add(judge)
                    db.session.commit()
                    flash(judge.name + ' was successfully created')
                    return redirect(url_for('judges'))
    #
    #   GET
    #
    return render_template('create_judge.html')

#
#   Update
#

@app.route('/tabmaster/judges/update/<int:id>', methods=['POST', 'GET'])
@login_required
def update_judge(id):
    judge = Judge.query.get(id)
    user = User.query.get(judge.user_id)
    club = Club.query.get(judge.club_id)
    if request.method == 'GET':
        
        #
        #   GET
        #

        _judge = {}
        _judge['id'] = judge.id
        _judge['name'] = judge.name
        _judge['email'] = user.email
        _judge['club'] = club.name
        return render_template('update_judge.html', judge = _judge)

    #
    #   POST
    #

    name = request.form['name']
    email = request.form['email']
    club_name = request.form['club']
    
    judge.name = name
    
    if(user.email != email):
        try:
            user.email = email
        except:
            flash('A different user has this email', 'error')
            return render_template('update_judge.html',judge = _judge)
    if(club.name != club_name):
        create_club(club)
        club = Club.query.filter_by(name = club).one()
        judge.club_id = club.id
        
    db.session.commit()
    flash(judge.name+' was successfully updated')
    return redirect(url_for('judges'))

#
#   DELETE
#

@app.route('/tabmaster/judges/delete/<id>', methods=['GET'])
def delete_judge(id):
    judge = Judge.query.get(id)
    name = judge.name
    db.session.delete(judge)
    db.session.commit()
    flash(name +'was successfully deleted.')
    return redirect(url_for('judges'))

#
#
#   Admin tabmasters
#
#


#
#   CREATE
#



@app.route('/admin/create_tabmaster', methods=['POST', 'GET'])
def create_tabmaster():
    if request.method == 'POST':
        #
        #   POST
        #
        if not request.form['name']:
            flash('Name is required', 'error')
        else:
            if not request.form['email']:
                flash('Email is required', 'error')
            else:
                name = request.form['name']
                email = request.form['email']
                
                tabmaster = Tabmaster(name)
                    
                if User.query.filter_by(email = email).count() == 0:
                    create_user(email,"tambaster")
                user = User.query.filter_by(email = email).one()
                tabmaster.user_id = user.id
                tabmaster.mail = email
                        
                db.session.add(tabmaster)
                db.session.commit()
                flash(tabmaster.name + ' was successfully created')
                return redirect(url_for('admin'))
    #
    #   GET
    #
    return render_template('create_tabmaster.html')

#
#   DELETE
#

@app.route('/admin/del_tabmaster', methods=['POST', 'GET'])
@login_required
def del_tabmaster():
    if request.method == 'POST':
        if not request.form['email']:
            flash('Name is required', 'error')
        else:
            user = User.query.filter_by(email = email).one()
            _tabmaster = Tabmaster.query.filter_by(user_id=user.id).one()
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


#
#   Update
#

@app.route('/admin/update_<id>tabmaster', methods=['POST', 'GET'])
@login_required
def update_tabmaster(id):
    tabmaster = Tabmaster.query.get(id)
    prev_tabmaster_name = tabmaster.name
    user = User.query.get(tabmaster.user_id)
    if request.method == 'GET':
        
        #
        #   GET
        #

        _tabmaster = {}
        _tabmaster['id'] = tabmaster.id
        _tabmaster['name'] = tabmaster.name
        _tabmaster['email'] = user.email
        return render_template('update_tabmaster.html', tabmaster = _tabmaster)

    #
    #   POST
    #

    name = request.form['name']
    email = request.form['email']
    
    tabmaster.name = name
    tabmaster.mail = email
    
    if(user.email != email):
        try:
            user.email = email
        except:
            flash('A different user has this email', 'error')
            return render_template('update_tabmaster.html',tabmaster = _tabmaster)
        
    db.session.commit()
    flash(prev_tabmaster_name+' was successfully updated')
    return redirect(url_for('admin'))



@app.route('/admin')
def admin():
    return render_template('admin.html', tabmasters = Tabmaster.query.order_by(Tabmaster.id))    

#
#
#   Interfata debater / judge
#
#

@app.route('/')
def home():
    if current_user.is_authenticated() == False:
        return render_template('home.html')
    else:
        if current_user.user_type == 'admin':
            return redirect(url_for('admin'))
        if current_user.user_type == 'tabmaster':
            return redirect(url_for('debaters'))
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
    user = User(request.form['email'],  request.form['password'], request.form['user_type'])
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
        return redirect(url_for('admin'))
    if registered_user.user_type == 'tabmaster':
        return redirect(url_for('debaters'))
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

