import requests
from datetime  import date

def get_teams():
    url=('https://www.balldontlie.io/api/v1/teams')
    r = requests.get(url)
    full_team_info = r.json()['data']
    return full_team_info

def get_scores():
    today = date.today()
    d1 = today.strftime("%Y-%m-%d")
    url = ('https://www.balldontlie.io/api/v1/games?seasons[]=2021&start_date='+d1+'&end_date='+d1)
    r = requests.get(url)
    matches_today = r.json()['data']
    return matches_today

event_data = get_teams()
r = requests.post("http://broker_server1:5000/pub1/advertize", json=event_data)

event_data = get_scores()
r = requests.post("http://broker_server1:5000/pub1", json=event_data)