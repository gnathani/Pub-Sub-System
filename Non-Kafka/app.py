from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_wtf import FlaskForm
from wtforms import SelectField
from pymongo import MongoClient
import requests

app = Flask(__name__)
app.secret_key = 'adgn'

def get_my_topics():
    teams_list = ["Atlanta Hawks","Boston Celtics","Brooklyn Nets","Charlotte Hornets","Chicago Bulls","Cleveland Cavaliers","Dallas Mavericks","Denver Nuggets","Detroit Pistons","Golden State Warriors"]
    return teams_list

def get_my_neighbour():
    return 'broker_server2'

@app.route('/', methods=['GET', 'POST'])
def login():
    msg = 'Input Username/Password'
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        client1 = MongoClient(host='test_mongodb', port=27017, username='root', password='pass', authSource="admin")
        db1 = client1["user_db"]
        user_found = db1.user_login_tb.find_one({"username": username})
        if user_found:
            if password == user_found["password"]:
                session['loggedin'] = True
                session['username'] = username
                print("validated")
                return redirect(url_for('home'))
            else:
                msg = 'Incorrect password!'
        else:
            msg = 'Incorrect username'
    return render_template('index.html', msg=msg)

@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('username', None)
   return redirect(url_for('login'))

class Form(FlaskForm):
    client = MongoClient(host='test_mongodb', port=27017, username='root', password='pass', authSource="admin")
    db = client["user_db"]
    teams_list = db.teams_tb.distinct("full_name")
    team = SelectField('team', choices=teams_list)

@app.route('/home', methods=['GET','POST'])
def home():
    if 'loggedin' in session:
        to_send = []
        news_list = []
        form=Form()
        client = MongoClient(host='test_mongodb', port=27017, username='root', password='pass', authSource="admin")
        db = client["user_db"]
        usr = session['username']
        if request.method == 'POST':
            new_sub = form.team.data
            curr_subs = db.subscr_tb.find({"username": usr},{"topic":1})
            t_list = []
            for x in curr_subs:
                t_list.append(x["topic"])
            if new_sub not in t_list:
                my_teams = get_my_topics()
                my_nbr = get_my_neighbour()
                if new_sub not in my_teams: 
                    to_send.append(usr)
                    to_send.append(new_sub)
                    r = requests.post("http://"+my_nbr+":5001/sub",json=to_send)
                else: db.subscr_tb.insert_one({"username": usr, "topic": new_sub})
                flash('subscribed')
            else:
                flash("already Subscribed")
        news_list = []
        score_list = []
        c_games = None
        curr_subs = db.subscr_tb.find({"username": usr}, {"topic": 1})
        if curr_subs==None: redirect(url_for('home'))
        for x in curr_subs:
            t_news = db.news_tb.find({"topic": x["topic"]})
            c_games = db.score_tb.find({"topic": x["topic"]})
            for y in t_news:
                news_list.append({"topic": y["topic"],"title":y["title"],"link":y["link"]})
            if c_games == None: return render_template('home.html', form=form, news_list=news_list, username=usr,score_list=score_list)
            for z in c_games:
                score_list.append({"topic": z["topic"],"title": z["title"],"score": z["score"]})
        return render_template('home.html', form=form, news_list=news_list, username=usr, score_list=score_list)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = 'Please give input'
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            msg = 'Please fill full form!'
        else:
            client1 = MongoClient(host='test_mongodb', port=27017, username='root', password='pass', authSource="admin")
            db1 = client1["user_db"]
            user_found = db1.user_login_tb.find_one({"username": username})
            if user_found:
                msg = 'username already exists'
            else:
                db1.user_login_tb.insert_one({"username": username, "password": password})
                msg = 'Registration done!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

class Form1(FlaskForm):
    team = SelectField('team', choices=[])

@app.route('/profile', methods=['GET','POST'])
def profile():
    form = Form1()
    client = MongoClient(host='test_mongodb', port=27017, username='root', password='pass', authSource="admin")
    db = client["user_db"]
    usr = session['username']
    curr_subs = db.subscr_tb.find({"username": usr}, {"topic": 1})
    t_list = []
    for x in curr_subs:
        t_list.append(x["topic"])
    form.team.choices=t_list

    # Check if user is loggedin
    if 'loggedin' in session:
        if request.method == 'POST':
            db.subscr_tb.remove({"username":usr,"topic":form.team.data})
            flash("UnSubscribed")
            return redirect(url_for('profile'))

        return render_template('profile.html',form=form,dropdown_list=t_list)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/pub1/advertize',methods=['POST'])
def return_message1_1():
    data = request.json
    advertize(data)
    return "got teams from pub1 - advertize"

def advertize(full_team_info):
    client = MongoClient(host='test_mongodb', port=27017, username='root', password='pass', authSource="admin")
    db = client["user_db"]
    for x in full_team_info:
        db.teams_tb.insert_one({"team_id":x['id'],"full_name":x['full_name'],"name":x['name'],"abbr":x['abbreviation']})
    return 0

@app.route('/pub1',methods=['POST'])
def return_message1_2():
    data = request.json
    publish_score(data)
    return "got events from pub1 - publish1"

def publish_score(matches_today):
    client = MongoClient(host='test_mongodb', port=27017, username='root', password='pass', authSource="admin")
    db = client["user_db"]
    for x in matches_today:
        title = ''+x['visitor_team']['abbreviation']+'@'+x['home_team']['abbreviation']
        score = ''+str(x['visitor_team_score'])+'-'+str(x['home_team_score'])+' '+str(x['time'])
        topic1 = x['visitor_team']['full_name']
        db.score_tb.insert_one({"topic": topic1, "title": title, "score": score})
        topic2 = x['home_team']['full_name']
        db.score_tb.insert_one({"topic": topic2, "title": title, "score": score})
    return 0

@app.route('/pub',methods=['POST'])
def return_message2():
    data = request.json
    publish_news(data)
    return "got events from pub2/pub3 - publish"

def publish_news(news_all):
    my_teams = get_my_topics()
    my_nbr = get_my_neighbour()
    to_send = []
    client = MongoClient(host='test_mongodb', port=27017, username='root', password='pass', authSource="admin")
    db = client["user_db"]
    for news in news_all:
        if news['team'] in my_teams: db.news_tb.insert_one({"topic": news['team'],"title": news['title'],"link": news['link']})
        else: to_send.append(news)
    if to_send != []: r = requests.post("http://"+my_nbr+":5001/pub",json=to_send)
    return 0

@app.route('/sub',methods=['POST'])
def subscribe():
    my_teams = get_my_topics()
    my_nbr = get_my_neighbour()
    client = MongoClient(host='test_mongodb', port=27017, username='root', password='pass', authSource="admin")
    db = client["user_db"]
    data=request.json
    if data[1] not in my_teams: r = requests.post("http://"+my_nbr+":5001/sub",json=data)
    else: db.subscr_tb.insert_one({"username": data[0], "topic": data[1]})
    return "sub done"

if __name__=='__main__':
    app.run(host="0.0.0.0", port=5000)