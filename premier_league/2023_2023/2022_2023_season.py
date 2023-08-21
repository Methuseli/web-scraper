import requests
from bs4 import BeautifulSoup

class Season20222023:
    def __init__(self):
        pass
    
    def generate_results_list(self, data):
        results = []
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
            
            results.append(fixture_data)
        return results
    
    def get_match_details(self, link):
        reponse = requests.get(link)
        text = reponse.text
        html_data = BeautifulSoup(text, "html.parser")
        

    def get_league_results(self):
        response = requests.get(
            "https://www.skysports.com/premier-league-results/2022-23")
        text = response.text
        html_data = BeautifulSoup(text, "html.parser")

        data = html_data.find_all("div", class_="fixres__item")
        
        league_results = []
        league_results += self.generate_results_list(data=data)
        
        
            
        script_data = html_data.find("script", attrs={"type": "text/show-more","data-role": "load-more-content"})
        script_text = script_data.string
        script_parsed = BeautifulSoup(script_text, "html.parser")
        fixture_list = script_parsed.find_all("div", class_="fixres__item")
        league_results += self.generate_results_list(data=fixture_list)
            
        print(league_results)
            

if __name__ == "__main__":
    season = Season20222023()
    season.get_league_results()
