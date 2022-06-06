import requests
from datetime  import date
from kafka import KafkaProducer
import json
from bson import json_util
import time

def publish1_scores():
    time.sleep(60)
    m_count = 0
    producer = KafkaProducer(bootstrap_servers="kafka1:19092,kafka2:19093,kafka3:19094",api_version=(0,11,5))
    today = date.today()
    d1 = today.strftime("%Y-%m-%d")
    url = ('https://www.balldontlie.io/api/v1/games?seasons[]=2021&start_date='+d1+'&end_date='+d1)
    r = requests.get(url)
    matches_today = r.json()['data']
    for x in matches_today:
        m_count = m_count + 2
        title = ''+x['visitor_team']['abbreviation']+'@'+x['home_team']['abbreviation']
        score = ''+str(x['visitor_team_score'])+'-'+str(x['home_team_score'])+' '+str(x['time'])
        topic1 = x['visitor_team']['full_name']
        topic2 = x['home_team']['full_name']
        s1 = {"topic": topic1, "title": title, "score": score}
        s2 = {"topic": topic2, "title": title, "score": score}
        topic1 = topic1.lower()
        topic1 = topic1.replace(" ","")
        topic1 = 'sc'+topic1
        producer.send(topic1, json.dumps(s1, default=json_util.default).encode('utf-8'))
        producer.flush()
        topic2 = topic2.lower()
        topic2 = topic2.replace(" ","")
        topic2 = 'sc'+topic2
        producer.send(topic2, json.dumps(s2, default=json_util.default).encode('utf-8'))
        producer.flush()
    return m_count

event_data = publish1_scores()
print(event_data)
