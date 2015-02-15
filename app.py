from datetime import datetime
from flask import Flask,session, request, flash, url_for, redirect, render_template, abort ,g,request
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.login import login_user , logout_user , current_user , login_required
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc


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
    points = db.Column(db.Integer)
    __tablename__ = "teams"
    id = db.Column('team_id', db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    #oras si liceu 
    #points = db.Column(db.Integer)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.club_id'))
    debaters = db.relationship('Debater', backref='team', lazy='dynamic')
    #points = db.Column(db.Integer)
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

    def __init__(self, name):
        self.name = name


class Game(db.Model):
    __tablename__= "games"
    id = db.Column('game_id', db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    goverment_id= db.Column(db.Integer, db.ForeignKey('teams.team_id'))
    opposition_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'))
    round_number = db.Column(db.Integer)
    room = db.Column(db.String(30))
    decision = db.Column(db.String(30))
    judge_id = db.Column(db.Integer, db.ForeignKey('judges.judge_id'))
    goverment1_points = db.Column(db.Integer)
    goverment1_id = db.Column(db.Integer, db.ForeignKey('debaters.debater_id'))
    goverment2_points = db.Column(db.Integer)
    goverment2_id = db.Column(db.Integer, db.ForeignKey('debaters.debater_id'))
    goverment3_points = db.Column(db.Integer)
    goverment3_id = db.Column(db.Integer, db.ForeignKey('debaters.debater_id'))
    goverment4_points = db.Column(db.Integer)
    opposition1_points = db.Column(db.Integer)
    opposition1_id = db.Column(db.Integer, db.ForeignKey('debaters.debater_id'))
    opposition2_points = db.Column(db.Integer)
    opposition2_id = db.Column(db.Integer, db.ForeignKey('debaters.debater_id'))
    opposition3_points = db.Column(db.Integer)
    opposition3_id = db.Column(db.Integer, db.ForeignKey('debaters.debater_id'))
    opposition4_points = db.Column(db.Integer)
    time = db.Column(db.DateTime)
    #
    #   Judge feedback !?
    #
    def __init__(self, round_number, room):
        self.round_number = round_number
        self.room = room


#
#
#   Functions
#
#
def update_teams_points():
    teams = Team.query.all()
    for team in teams:
        points = 0
        oppositions = Game.query.filter_by(opposition_id=team.id)
        points += opposition_points(oppositions)
        goverments = Game.query.filter_by(goverment_id=team.id)
        points += goverment_points(goverments)
        team.points = points

def opposition_points(games):
    points = 0
    for game in games:
        points += game.opposition1_points
        points += game.opposition2_points
        points += game.opposition3_points
        points += game.opposition4_points
    return points
def goverment_points(games):
    points = 0
    for game in games:
        points += game.goverment1_points
        points += game.goverment2_points
        points += game.goverment3_points
        points += game.goverment4_points
    return points


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
    
    debater.name = name
    
    if(user.email != email):
        try:
            user.email = email
        except:
            flash('A different user has this email', 'error')
            return render_template('update_debater.html',debater = _debater)
    if(club.name != club_name):
        create_club(club)
        club = Club.query.filter_by(name = club).one()
        judge.club_id = club.id
        
    db.session.commit()
    flash(debater.name+' was successfully updated')
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
#
#   Tabmaster Create Round
#
#
@app.route('/tabmaster/round/', methods=['GET','POST'])
def round():
    if request.method == 'POST':
         return render_template("round.html")
    games = Game.query.order_by(desc(Game.round_number))
    round_number = games.first().round_number 
    games = Game.query.filter_by(round_number = round_number)
    _games = []
    for game in games:
        _game = {}
        _game['id'] = game.id
        goverment = Team.query.get(game.goverment_id)
        opposition = Team.query.get(game.opposition_id)
        _game['goverment'] = goverment.name
        _game['opposition'] = opposition.name
        _game['room'] = game.room
        judge = Judge.query.get(game.judge_id)
        _game['judge'] = judge.name
        _games.append(_game)
    return render_template("round.html", games = _games, round_number = round_number)




@app.route('/tabmaster/create_round', methods=['GET','POST'])
def create_round_pannel():
    return render_template("create_round.html")

@app.route('/tabmaster/create_round/<mod>', methods=['GET'])
def create_round(mod):
    print "intra"
    update_teams_points()
    teams = Team.query.order_by(desc(Team.points))
    games = Game.query.all()
    if len(games) == 0:
        round_number = 0 
    else:
        games = Game.query.order_by(Game.round)
        round_number = games.last().round_number + 1 
    if mod == "High_Low":
        odd = False
        if (teams.count() % 2 == 1):
            odd = True
        games = [] 
        i = 0 
        for team in teams:
            if odd and i == n:
                break;
            if i < n/2: 
                game = Game(round_number,i)
                game.goverment_id = team.id
                games.append(game)
            else:
                games[i-n/2].opposition_id = team.id
            i += 1
    if mod == "High_High":
        print "high"
        odd = False
        if (teams.count() % 2 == 1):
            odd = True
        games = [] 
        i = 0 
        for team in teams:
            if odd and i == n:
                break;
            if i % 2 == 0: 
                game = Game(round_number,i)
                game.goverment_id = team.id
                print "gov id "+str(team.id)
                games.append(game)
            else:
                print "op id "+str(team.id)
                game.opposition_id = team.id
            i += 1
    i = 1
    for game in games:
        print "game room "+str(game.room)
        judge = Judge.query.get(i)
        game.judge_id = judge.id
        i += 1
        db.session.add(game)
    db.session.commit()
    return redirect(url_for('round')) 

@app.route('/tabmaster/clasament', methods=['GET','POST'])
def ranking():
    update_teams_points()
    teams = Team.query.order_by(desc(Team.points))
    return render_template("ranking_teams.html",teams=teams)

@app.route('/tabmaster/break', methods=['GET','POST'])
def Break():
    update_teams_points()
    teams = Team.query.order_by(desc(Team.points)).limit(8)
    return render_template("ranking_teams.html",teams=teams)

@app.route('/tabmaster/upload', methods=['GET','POST'])
def upload():
    #update_teams_points()
    return render_template("ranking_teams.html")

#
#
#   Admin tabmasters
#
#

@app.route('/admin/tabmasters/create', methods=['POST', 'GET'])
@login_required
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
                    create_user(email,"tabmaster")
                user = User.query.filter_by(email = email).one()
                tabmaster.user_id = user.id
                        
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

@app.route('/admin/tabmasters/delete/<id>', methods=['POST', 'GET'])
@login_required
def delete_tabmaster(id):
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

@app.route('/admin/tabmasters/update/<id>', methods=['POST', 'GET'])
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
    tabmasters =Tabmaster.query.all()
    _tabmasters = []
    for tabmaster in tabmasters:
        _tabmaster = {}
        _tabmaster['id'] = tabmaster.id
        _tabmaster['name'] = tabmaster.name
        user = User.query.get(tabmaster.user_id)
        _tabmaster['email'] = user.email
        _tabmasters.append(_tabmaster)
    return render_template('admin.html', tabmasters = _tabmasters)    

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
        print "Admin"
        return redirect(url_for('admin'))
    if registered_user.user_type == 'tabmaster':
        print "Tabmaster"
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
