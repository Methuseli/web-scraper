import requests
import re
import time

from bs4 import BeautifulSoup   
from selenium import webdriver
from selenium.webdriver import Chrome 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class Season20222023:
    def __init__(self):
        pass
    
    def generate_results_list(self, data):
        results = []
        for fixture in data:
            fixture_data = {}
            
            home_team = fixture.find("span", attrs={"class":"matches__item-col matches__participant matches__participant--side1"})
            home_team = home_team.find("span", attrs={"class":"swap-text__target"})
            fixture_data["HomeTeam"] = home_team.get_text().strip()
            
            away_team = fixture.find("span", attrs={"class":"matches__item-col matches__participant matches__participant--side2"})
            away_team = away_team.find("span", attrs={"class":"swap-text__target"})
            fixture_data["AwayTeam"] = away_team.get_text().strip()
            
            goals = fixture.find("span", attrs={"class":"matches__item-col matches__status"})
            goals = goals.find_all("span", attrs={"class":"matches__teamscores-side"})
            fixture_data["HomeGoals"] = goals[0].get_text().strip()
            fixture_data["AwayGoals"] = goals[1].get_text().strip()
            
            link = fixture.find("a", attrs={"class":"matches__item matches__link"})
            
            fixture_data = self.get_match_details(link=link.get("href"), fixture_data_dict=fixture_data)
            # print(fixture_data)
            
            results.append(fixture_data)
        return results
    
    def extract_svg_data(self, link):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        
        options.page_load_strategy = 'none'
        # options.add_experimental_option("detach", True)
        
        chrome_path = ChromeDriverManager().install() 
        chrome_service = Service(chrome_path)
        
        driver = Chrome(options=options, service=chrome_service) 
        
        driver.get(link)
        
        driver.implicitly_wait(10)
        
        driver.switch_to.frame("sp_message_iframe_758392")
        
        # Assuming the "Accept" button has a CSS selector like ".accept-cookies"
        accept_button = driver.find_element(By.CSS_SELECTOR, ".sp_message-accept-button")
        accept_button.click()
        
        driver.switch_to.default_content()
        svg_container = driver.find_element(By.CSS_SELECTOR, ".sdc-site-opta-widget")
        driver.execute_script("arguments[0].scrollIntoView();", svg_container)
  
        time.sleep(10)
        
        content = driver.find_element(By.CSS_SELECTOR, ".Opta-Normal")
        driver.quit()
        return content
    
    def get_match_details(self, link, fixture_data_dict):
        reponse = requests.get(link)
        text = reponse.text
        html_data = BeautifulSoup(text, "html.parser")
        fixture_data_dict["MatchDate"] = html_data.find("time", attrs={"class": "sdc-site-match-header__detail-time"}).get_text().strip()
        fixture_data_dict["Venue"] = html_data.find("span", attrs={"class": "sdc-site-match-header__detail-venue sdc-site-match-header__detail-venue--with-seperator"}).get_text().strip() if html_data.find("span", attrs={"class": "sdc-site-match-header__detail-venue sdc-site-match-header__detail-venue--with-seperator"}) is not None else None
        if fixture_data_dict["Venue"] is None:
            fixture_data_dict["Venue"] = html_data.find("span", attrs={"class": "sdc-site-match-header__detail-venue"}).get_text().strip() if html_data.find("span", attrs={"class": "sdc-site-match-header__detail-venue"}) is not None else None
        attendance = html_data.find("span", attrs={"class": "sdc-site-match-header__detail-attendance"}).get_text().strip().replace(",", "") if html_data.find("span", attrs={"class": "sdc-site-match-header__detail-attendance"}) is not None else None
        if attendance is not None:
            number = re.search(r'\d+', attendance).group()
        # print(number)
            if number is not None:
                fixture_data_dict["Attendance"] = number
            else:
                fixture_data_dict["Attendance"] = None
        else:
            fixture_data_dict["Attendance"] = None
            
        home_events_ul = html_data.find("ul", attrs={"class": "sdc-site-match-header__team-synopsis", "data-update": "synopsis-home"})
        away_events_ul = html_data.find("ul", attrs={"class": "sdc-site-match-header__team-synopsis", "data-update": "synopsis-away"})
        fixture_data_dict["HomeEvents"] = self.get_match_major_events(events_ul=home_events_ul)
        fixture_data_dict["AwayEvents"] = self.get_match_major_events(events_ul=away_events_ul)
        
        content = self.extract_svg_data(link=link)
        print(content)

        
        svg_data = html_data.find("svg", attrs={"class": "Opta-Responsive-Svg"})
        # print(html_data.prettify())
        
        home_starting_players = html_data.find_all("g", attrs={"class": "Opta-Node Opta-Home Opta-Starter"})
        home_susbstitutes = html_data.find_all("div", attrs={"class":"Opta-Sub Opta-Home"})
        # print(home_starting_players)
        # print(home_susbstitutes)
        
        # fixture_data_dict["HomePlayers"] = self.get_team_players(starting_eleven_list=home_starting_players)
        
        return fixture_data_dict
    
    def get_match_major_events(self, events_ul):
        major_events = {}
        list_elements = events_ul.find_all("li", attrs={"class": "sdc-site-match-header__team-synopsis-line"})
        
        goals_list = []
        red_card_list = []
        own_goals_list = []
        penalty_goals_list = []
        
        goal_event = {}
        red_card_event = {}
        own_goal_event = {}
        penalty_goal_event = {}
        
        pattern = r'\((.*?)\)'
        number_pattern = r'\b\d+\b'
        
        for event in list_elements:
            # print(event.get_text())
            event_string = event.get_text().strip()
            open_paren_index = event_string.index("(")
            if event_string:
                event_time = re.findall(pattern, event_string)
                if event_time:
                    event_time = event_time[0].split(",")
                else:
                    event_time = [  ]
            else:
                event_time = []
            # print(event_time)
            for element in event_time:
                player_name = event_string[:open_paren_index].replace("\xa0", "")
                event_minute = re.findall(number_pattern, element)
                if "pen" in element:
                    penalty_goal_event = {
                        "Player": player_name,
                        "Time": event_minute[0]
                    }
                    penalty_goals_list.append(penalty_goal_event)
                elif "own goal" in element or "og" in element:
                    own_goal_event = {
                        "Player": player_name,
                        "Time": event_minute[0]
                    }
                    own_goals_list.append(own_goal_event)
                elif "red card" in element:
                    red_card_event = {
                        "Player": player_name,
                        "Time": event_minute[0]
                    }
                    red_card_list.append(red_card_event)
                else:
                    goal_event = {
                        "Player": player_name,
                        "Time": event_minute[0]
                    }
                    goals_list.append(goal_event)
        
        major_events = {
            "Goals": goals_list,
            "RedCards": red_card_list,
            "OwnGoals": own_goals_list,
            "Penalties": penalty_goals_list
        }
        return major_events
    
    def get_team_players(self, starting_eleven_list, substitutes_list):
        starting_eleven = []
        substitutes = []
        replaced_player = []
        substituted_player = []
        
        player_statistics = {} 
        
        
        
        
        

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
            
        # print(league_results)
            

if __name__ == "__main__":
    season = Season20222023()
    season.get_league_results()
