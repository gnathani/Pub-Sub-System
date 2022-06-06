import requests
from datetime  import date

def get_news():
    news_all = []
    today = date.today()
    d1 = today.strftime("%Y-%m-%d")
    teams_list = ["Atlanta Hawks","Boston Celtics","Brooklyn Nets","Charlotte Hornets","Chicago Bulls","Cleveland Cavaliers",
                "Dallas Mavericks","Denver Nuggets","Detroit Pistons","Golden State Warriors","Houston Rockets","Indiana Pacers",
                "LA Clippers","Los Angeles Lakers","Memphis Grizzlies","Miami Heat","Milwaukee Bucks","Minnesota Timberwolves",
                "New Orleans Pelicans","New York Knicks","Oklahoma City Thunder","Orlando Magic","Philadelphia 76ers","Phoenix Suns",
                "Portland Trail Blazers","Sacramento Kings","San Antonio Spurs","Toronto Raptors","Utah Jazz","Washington Wizards"]
    for team in teams_list:
        url = ('https://newsapi.org/v2/everything?apiKey=cee78f55da654809acd5931f6998d2bf&from='+d1+'&q='+team)
        r = requests.get(url)
        if r.json()['status']!="ok":
            print("Queries for the day used up! Please try tomorrow")
            return news_all
        news = r.json()['articles']
        for n in news:
            s =  {'team': team, 'title': n['title'],'link':n['url']}
            news_all.append(s)
    return news_all

event_data = get_news()
print(len(event_data))
r = requests.post("http://broker_server3:5002/pub", json=event_data)