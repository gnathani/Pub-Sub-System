import requests
from datetime  import date
from kafka import KafkaProducer
import json
from bson import json_util
import time

def publish3_news2():
    time.sleep(60)
    n_count = 0
    today = date.today()
    d1 = today.strftime("%Y-%m-%d")
    teams_list = ["Atlanta Hawks","Boston Celtics","Brooklyn Nets","Charlotte Hornets","Chicago Bulls","Cleveland Cavaliers",
                "Dallas Mavericks","Denver Nuggets","Detroit Pistons","Golden State Warriors","Houston Rockets","Indiana Pacers",
                "LA Clippers","Los Angeles Lakers","Memphis Grizzlies","Miami Heat","Milwaukee Bucks","Minnesota Timberwolves",
                "New Orleans Pelicans","New York Knicks","Oklahoma City Thunder","Orlando Magic","Philadelphia 76ers","Phoenix Suns",
                "Portland Trail Blazers","Sacramento Kings","San Antonio Spurs","Toronto Raptors","Utah Jazz","Washington Wizards"]
    producer = KafkaProducer(bootstrap_servers="kafka1:19092,kafka2:19093,kafka3:19094",api_version=(0,11,5))
    for team in teams_list:
        url = ('https://newsapi.org/v2/everything?apiKey=0b0416ceaea845d2b7993b67442cda67&from='+d1+'&q='+team)
        r = requests.get(url)
        if r.json()['status']!="ok":
            print("Queries for the day used up! Please try tomorrow")
            return n_count
        news = r.json()['articles']
        for n in news:
            n_count = n_count + 1
            s =  {'team': team, 'title': n['title'],'link':n['url']}
            team = team.lower()
            team = team.replace(" ","")
            producer.send(team, json.dumps(s, default=json_util.default).encode('utf-8'))
            producer.flush()
    return n_count

event_data = publish3_news2()
print(event_data)
