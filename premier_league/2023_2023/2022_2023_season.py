import requests
from bs4 import BeautifulSoup

# from keep_alive import keep_alive


class Season20222023:
    def __init__(self):
        pass

    def get_league_results(self):
        # response = requests.get("https://optaplayerstats.statsperform.com/en_GB/soccer/premier-league-2022-2023/80foo89mm28qjvyhjzlpwj28k/opta-player-stats")
        response = requests.get(
            "https://www.skysports.com/premier-league-results/2022-23")
        # response = requests.get("https://www.google.com/search?q=epl+2022-2023&oq=epl+2022-2023&aqs=chrome.0.69i59j0i22i30l9.3182j0j7&sourceid=chrome&ie=UTF-8#sie=lg;/g/11pz7zbpnb;2;/m/02_tc;mt;fp;1;;;")
        # response = requests.get("https://www.google.com/search?q=epl+2022-2023&sca_esv=558130159&sxsrf=AB5stBgbHW1FfdG9TdmK0rlVa9uXNo04MQ%3A1692370980455&ei=JIjfZPCuG4mCxc8PtKmPaA&ved=0ahUKEwjw0PiYveaAAxUJQfEDHbTUAw0Q4dUDCA8&oq=epl+2022-2023&gs_lp=Egxnd3Mtd2l6LXNlcnAiDWVwbCAyMDIyLTIwMjMyBhAAGAgYHjIGEAAYCBgeMgYQABgIGB4yBhAAGAgYHjIGEAAYCBgeMgYQABgIGB4yBhAAGAgYHjIGEAAYCBgeMgYQABgIGB4yBhAAGAgYHkiuZ1D4A1jZWHABeAGQAQCYAY8DoAHJHaoBBTItOS40uAEMyAEA-AEBwgIKEAAYRxjWBBiwA8ICChAAGIoFGLADGEPCAhAQLhiKBRjIAxiwAxhD2AEBwgINEAAYigUYsQMYgwEYQ8ICChAAGIoFGLEDGEPCAgcQABiKBRhDwgINEC4YigUYsQMYgwEYQ8ICBxAuGIoFGEPCAhYQLhiKBRhDGJcFGNwEGN4EGOAE2AECwgIFEAAYgATCAgYQABgWGB7CAggQABiKBRiGA8ICCBAhGBYYHhgdwgIFEAAYogTiAwQYACBBiAYBkAYUugYGCAEQARgIugYGCAIQARgU&sclient=gws-wiz-serp#cobssid=s&sie=lg;/g/11pz7zbpnb;2;/m/02_tc;mt;fp;1;;;")
        text = response.text
        html_data = BeautifulSoup(text, "html.parser")

        # print(html_data.prettify())
        data = html_data.find_all("div", class_="fixres__item")
        # print(html_data)
        
        league_results = []
        
        for fixture in data:
            fixture_data = {}
            
            home_team = fixture.find("span", attrs={"class":"matches__item-col matches__participant matches__participant--side1"})
            home_team = home_team.find("span", attrs={"class":"swap-text__target"})
            fixture_data["HomeTeam"] = home_team.get_text()
            
            away_team = fixture.find("span", attrs={"class":"matches__item-col matches__participant matches__participant--side2"})
            away_team = away_team.find("span", attrs={"class":"swap-text__target"})
            fixture_data["AwayTeam"] = away_team.get_text()
            
            goals = fixture.find("span", attrs={"class":"matches__item-col matches__status"})
            goals = goals.find_all("span", attrs={"class":"matches__teamscores-side"})
            fixture_data["HomeGoals"] = goals[0].get_text().strip()
            fixture_data["AwayGoals"] = goals[1].get_text().strip()
            
            league_results.append(fixture_data)
            
        print(len(league_results))
        hidden_data = html_data.find("script", attrs={"type": "text/show-more","data-role": "load-more-content"})
        print(hidden_data)
        hidden_data = hidden_data.find_all("div", attr={"class": "fixres__item"})
        print(len(hidden_data))
        for fixture in hidden_data:
            fixture_data = {}
            
            home_team = fixture.find("span", attrs={"class":"matches__item-col matches__participant matches__participant--side1"})
            home_team = home_team.find("span", attrs={"class":"swap-text__target"})
            fixture_data["HomeTeam"] = home_team.get_text()
            
            away_team = fixture.find("span", attrs={"class":"matches__item-col matches__participant matches__participant--side2"})
            away_team = away_team.find("span", attrs={"class":"swap-text__target"})
            fixture_data["AwayTeam"] = away_team.get_text()
            
            goals = fixture.find("span", attrs={"class":"matches__item-col matches__status"})
            goals = goals.find_all("span", attrs={"class":"matches__teamscores-side"})
            fixture_data["HomeGoals"] = goals[0].get_text().strip()
            fixture_data["AwayGoals"] = goals[1].get_text().strip()
            
            league_results.append(fixture_data)
        # print(hidden_data)
            
        print(len(league_results))
            

if __name__ == "__main__":
    season = Season20222023()
    season.get_league_results()
