import requests

def get_news():
    news_all = []
    teams_list = ["Atlanta Hawks","Boston Celtics","Brooklyn Nets","Charlotte Hornets","Chicago Bulls","Cleveland Cavaliers",
                "Dallas Mavericks","Denver Nuggets","Detroit Pistons","Golden State Warriors","Houston Rockets","Indiana Pacers",
                "LA Clippers","Los Angeles Lakers","Memphis Grizzlies","Miami Heat","Milwaukee Bucks","Minnesota Timberwolves",
                "New Orleans Pelicans","New York Knicks","Oklahoma City Thunder","Orlando Magic","Philadelphia 76ers","Phoenix Suns",
                "Portland Trail Blazers","Sacramento Kings","San Antonio Spurs","Toronto Raptors","Utah Jazz","Washington Wizards"]
    for team in teams_list:
        url = ('https://newsdata.io/api/1/news?apikey=pub_19024fbacf174f5d32b33533ab9d2cfc2afa&category=sports&language=en&q='+team)
        r = requests.get(url)
        if r.json()['status']=="error":
            print("Queries for the day used up! Please try tomorrow")
            return news_all
        news = r.json()['results']
        for n in news:
            s =  {'team': team, 'title': n['title'],'link':n['link']}
            news_all.append(s)
    return news_all

event_data = get_news()
print(len(event_data))
r = requests.post("http://broker_server2:5001/pub", json=event_data)