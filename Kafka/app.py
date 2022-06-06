from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_wtf import FlaskForm
from wtforms import SelectField
from pymongo import MongoClient
#from pykafka import KafkaClient
from kafka import KafkaConsumer
from kafka import TopicPartition
import json

app = Flask(__name__)
app.secret_key = 'adgn'


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
    teams_list = ["Atlanta Hawks","Boston Celtics","Brooklyn Nets","Charlotte Hornets","Chicago Bulls","Cleveland Cavaliers",
                "Dallas Mavericks","Denver Nuggets","Detroit Pistons","Golden State Warriors","Houston Rockets","Indiana Pacers",
                "LA Clippers","Los Angeles Lakers","Memphis Grizzlies","Miami Heat","Milwaukee Bucks","Minnesota Timberwolves",
                "New Orleans Pelicans","New York Knicks","Oklahoma City Thunder","Orlando Magic","Philadelphia 76ers","Phoenix Suns",
                "Portland Trail Blazers","Sacramento Kings","San Antonio Spurs","Toronto Raptors","Utah Jazz","Washington Wizards"]
    team = SelectField('team', choices=teams_list)

@app.route('/home', methods=['GET','POST'])
def home():
    if 'loggedin' in session:
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
                db.subscr_tb.insert_one({"username": usr, "topic": new_sub})
                flash('subscribed')
            else:
                flash("already Subscribed")
        news_list = []
        score_list = []
        consumer = KafkaConsumer(
            bootstrap_servers="kafka1:19092,kafka2:19093,kafka3:19094",
            api_version=(0,11,5),
            auto_offset_reset='latest',
            consumer_timeout_ms=1000,
            group_id=None,
            enable_auto_commit=True,
            auto_commit_interval_ms=1000
        )
        curr_subs = db.subscr_tb.find({"username": usr}, {"topic": 1})
        if curr_subs==None: redirect(url_for('home'))
        print('found subs')
        for x in curr_subs:
            TOPIC = x["topic"]
            TOPIC = TOPIC.lower()
            TOPIC = TOPIC.replace(" ","")
            partitions = consumer.partitions_for_topic(TOPIC)
            if partitions != None:
                topic_partition = [TopicPartition(TOPIC, p) for p in partitions]
                assigned_topic = topic_partition
                print('got topic in kafka')
                consumer.assign(assigned_topic)
                for i in topic_partition:
                    consumer.seek_to_beginning(i)
                for message in consumer:
                    news_list.append(json.loads(message.value.decode()))
            SC_TOPIC = 'sc'+TOPIC
            partitions = consumer.partitions_for_topic(SC_TOPIC)
            if partitions == None:
                continue
            topic_partition = [TopicPartition(SC_TOPIC, p) for p in partitions]
            assigned_topic = topic_partition
            print('got sctopic in kafka')
            consumer.assign(assigned_topic)
            for i in topic_partition:
                consumer.seek_to_beginning(i)
            for message in consumer:
                score_list.append(json.loads(message.value.decode()))
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
            db.subscr_tb.delete_one({"username":usr,"topic":form.team.data})
            flash("UnSubscribed")
            return redirect(url_for('profile'))

        return render_template('profile.html',form=form,dropdown_list=t_list)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

if __name__=='__main__':
    app.run(host="0.0.0.0", port=5000)
