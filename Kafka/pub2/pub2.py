import requests
from kafka import KafkaProducer
import json
from bson import json_util
import time

def publish2_news1():
    time.sleep(60)
    n_count = 0
    teams_list = ["Atlanta Hawks","Boston Celtics","Brooklyn Nets","Charlotte Hornets","Chicago Bulls","Cleveland Cavaliers",
                "Dallas Mavericks","Denver Nuggets","Detroit Pistons","Golden State Warriors","Houston Rockets","Indiana Pacers",
                "LA Clippers","Los Angeles Lakers","Memphis Grizzlies","Miami Heat","Milwaukee Bucks","Minnesota Timberwolves",
                "New Orleans Pelicans","New York Knicks","Oklahoma City Thunder","Orlando Magic","Philadelphia 76ers","Phoenix Suns",
                "Portland Trail Blazers","Sacramento Kings","San Antonio Spurs","Toronto Raptors","Utah Jazz","Washington Wizards"]
    producer = KafkaProducer(bootstrap_servers="kafka1:19092,kafka2:19093,kafka3:19094",api_version=(0,11,5))
    for team in teams_list:
        url = ('https://newsdata.io/api/1/news?apikey=pub_2157e367e3fe353f7dc6aea66c639fa5c9e6&category=sports&language=en&q='+team)
        r = requests.get(url)
        if r.json()['status']=="error":
            print("Queries for the day used up! Please try tomorrow")
            return n_count
        news = r.json()['results']
        for n in news:
            n_count = n_count + 1
            s =  {'team': team, 'title': n['title'],'link':n['link']}
            team = team.lower()
            team = team.replace(" ","")
            producer.send(team, json.dumps(s, default=json_util.default).encode('utf-8'))
            producer.flush()
    return n_count

event_data = publish2_news1()
print(event_data)
