import requests
import re
import time

from bs4 import BeautifulSoup, NavigableString, Tag   
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from typing import List, Dict, Tuple
from webdriver_manager.chrome import ChromeDriverManager


class Season20222023:
    def __init__(self):
        pass
    
    def generate_results_list(self, data: List) -> List:
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
    
    def extract_svg_data(self, link: str) -> Tuple[str, str, str]:
        content = ""
        substitute_table = ""
        team_statistics = ""
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless=new')
        
        options.page_load_strategy = 'none'
        # options.add_experimental_option("detach", True)
        
        chrome_path = ChromeDriverManager().install() 
        chrome_service = Service(chrome_path)
        
        driver = Chrome(options=options, service=chrome_service) 
        
        driver.get(link)
        
        driver.implicitly_wait(10)
        
        driver.switch_to.frame("sp_message_iframe_758392")
        try:
            # Assuming the "Accept" button has a CSS selector like ".accept-cookies"
            accept_button = driver.find_element(By.CSS_SELECTOR, ".sp_message-accept-button")
            accept_button.click()
            
        except NoSuchElementException as e:
            print(f"{e}", "------------>>> Closing connection")
            
        
        driver.switch_to.default_content()
        svg_container = driver.find_element(By.XPATH, "/html/body/div[8]/div[3]/div/div[1]/div[2]/div[6]")
        driver.execute_script("arguments[0].scrollIntoView();", svg_container)
        
        driver.implicitly_wait(10)
        
        statistics_container = driver.find_element(By.XPATH, "/html/body/div[8]/div[3]/div/div[1]/div[2]/div[14]")
        driver.execute_script("arguments[0].scrollIntoView();", statistics_container)
        
        # time.sleep(10)
        driver.implicitly_wait(5)
        
        try:
            team_statistics = driver.find_element(By.CSS_SELECTOR, ".Opta-TabbedContent").get_attribute("outerHTML")
        except NoSuchElementException as e:
            print(f"{e}", "------------>>> Closing connection")
            
            
        driver.implicitly_wait(10)
        try:
            substitute_table = driver.find_element(By.CSS_SELECTOR, ".Opta-Subs-Wrap").get_attribute("outerHTML")
            # driver.quit()
        except NoSuchElementException as e:
            print(f"{e}", "------------>>> Closing connection")
            
        driver.implicitly_wait(10)
        try:
            content = driver.find_element(By.CSS_SELECTOR, ".Opta-Responsive-Svg").get_attribute("outerHTML")
        except NoSuchElementException as e:
            print(f"{e}", "------------>>> Closing connection")
            
            
        driver.quit()
        return content, substitute_table, team_statistics        
    
    def get_match_details(self, link: str, fixture_data_dict: Dict) -> Dict:
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
        
        content, substitute_table, team_statistics = self.extract_svg_data(link=link)

        home_player_stats, away_player_stats = self.get_team_players(content=content, substitute_content=substitute_table)
        
        
        fixture_data_dict["AwayPlayersStatistics"] = away_player_stats
        fixture_data_dict["HomePlayersStatistics"] = home_player_stats
        
        home_team_statistics, away_team_statistics = self.get_team_statistics(team_statistics=team_statistics)
        
        fixture_data_dict["HomeTeamStatistics"] = home_team_statistics
        fixture_data_dict["AwayTeamStatistics"] = away_team_statistics
        
        # print(fixture_data_dict)
        
        return fixture_data_dict
    
    def get_team_statistics(self, team_statistics: Tag | NavigableString | None) -> Tuple[Dict, Dict]:
        home_team_statistics = {}
        away_team_statistics = {}
        
        
        team_statistics_data = BeautifulSoup(team_statistics, "html.parser")
        
        statisics_list = team_statistics_data.find_all("table", attrs={"class":"Opta-Stats-Bars"})
        # print(statisics_list)
        
        for statisics in statisics_list:
            statisics_row = statisics.find_all("tr")
            print(statisics_row)
            for i in range(0, len(statisics_row), 2):
                key_name = statisics_row[i].get_text().strip().replace(" ", "")
                target_class_names = ["Opta-Outer"]
                values = [td for td in statisics_row[i+1].find_all('td') if any(class_name in td.get('class', []) for class_name in target_class_names)]
                home_team_statistics[f"Home{key_name}"] = values[0].get_text().strip()
                away_team_statistics[f"Away{key_name}"] = values[1].get_text().strip()
                
        print(home_team_statistics)
        print("------------------------------------------->>> <<<----------------------------------------")
        print(away_team_statistics)
        print("------------------------------------------->>> <<<----------------------------------------")
        
        return home_team_statistics, away_team_statistics
    
    def get_match_major_events(self, events_ul: Tag | NavigableString | None) -> Dict:
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
                    event_time = []
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
    
    def get_team_players(self, content: str, substitute_content: str) -> Tuple[Dict, Dict]:
        home_starting_eleven = []
        away_starting_eleven = []
        home_substitutes = []
        away_substitutes = []
        
        svg_data = BeautifulSoup(content, "html.parser")
        substitutes = BeautifulSoup(substitute_content, "html.parser")
        
        home_starting_players = svg_data.find_all("g", attrs={"class": "Opta-Node Opta-Home Opta-Starter"})
        target_class_names = ["Opta-Sub", "Opta-Home"]
        home_susbstitutes_players = [div for div in substitutes.find_all('div') if any(class_name in div.get('class', []) for class_name in target_class_names)]
        
        away_starting_players = svg_data.find_all("g", attrs={"class": "Opta-Node Opta-Away Opta-Starter"})
        target_class_names = ["Opta-Sub", "Opta-Away"]
        away_substitutes_players = [div for div in substitutes.find_all('div') if any(class_name in div.get('class', []) for class_name in target_class_names)]
        
        for player in home_starting_players:
            player_info = self.extract_player_game_info(player=player)
            home_starting_eleven.append(player_info)
        
        for substitute in home_susbstitutes_players:
            player_info = self.extract_substitute_player_game_info(player=substitute)
            home_substitutes.append(player_info)
        
        for player in away_starting_players:
            player_info = self.extract_player_game_info(player=player)
            away_starting_eleven.append(player_info)
            
        for substitute in away_substitutes_players:
            player_info = self.extract_substitute_player_game_info(player=substitute)
            away_substitutes.append(player_info)
        
        home_player_statistics = {
            "StartingEleven": home_starting_eleven,
            "Substitutes": home_substitutes,
        }
        
        away_player_statistics = {
            "StartingEleven": away_starting_eleven,
            "Substitutes": away_substitutes
        }
        
        # print("Away ______________________________ \n", away_substitutes)
        # print("-----------------------------------------------------")
        # print("Home ________________________________\n", home_substitutes)
        
        return home_player_statistics, away_player_statistics
        
    def extract_player_game_info(self, player: Tag | NavigableString | None) -> Dict:
        player_name = player.find_all("text", attrs={"class": "Opta-PlayerName"})
        player_stats_tag = player.find_all("div", attrs={"class": "Opta-Stat"})
        
        target_class_names = ["Opta-MatchEvent", "Opta-Soft"]
        player_events_tag = [li for li in player.find_all('li') if any(class_name in li.get('class', []) for class_name in target_class_names)]
        # print(player_events_tag)
        player_game_info = {}
        
        
        player_info = ""
        for player in player_name:
            player_info = player_info + " " + player.get_text()
        
        player_game_info = {
            "PlayerName": player_info.strip(),
            "PlayerStats": [],
            "Events": []
        }
        
        for stat in player_stats_tag:
            player_game_stat = {
                "Label": stat.find("div", attrs={"class": "Opta-Label"}).get_text(),
                "Value": stat.find("div", attrs={"class": "Opta-Value Opta-JS-NumberAnimation"}).get_text(),
            }
            player_game_info["PlayerStats"].append(player_game_stat)
        
        for event in player_events_tag:
            player_event_info = {
                "EventType": event.find("span", attrs={"class": "Opta-Event-Text-Type"}).get_text(),
                "EventTime": event.find("span", attrs={"class": "Opta-Event-Time"}).get_text().replace("\u200e", "")
            }
            player_game_info["Events"].append(player_event_info)
        
        # player_events = 
        # print("----------------------------------------------->")
        # print(player_stats_tag)
        return player_game_info
    
    def extract_substitute_player_game_info(self, player: Tag | NavigableString | None) -> Dict:
        player_name = player.find_all("span", attrs={"class": "Opta-PlayerName"})
        player_stats_tag = player.find_all("div", attrs={"class": "Opta-Stat"})
        
        target_class_names = ["Opta-MatchEvent", "Opta-Soft"]
        player_events_tag = [li for li in player.find_all('li') if any(class_name in li.get('class', []) for class_name in target_class_names)]
        # print(player_events_tag)
        player_game_info = {}
        
        
        player_info = ""
        for player in player_name:
            player_info = player_info + " " + player.get_text()
        
        player_game_info = {
            "PlayerName": player_info.strip(),
            "PlayerStats": [],
            "Events": []
        }
        
        for stat in player_stats_tag:
            player_game_stat = {
                "Label": stat.find("div", attrs={"class": "Opta-Label"}).get_text(),
                "Value": stat.find("div", attrs={"class": "Opta-Value Opta-JS-NumberAnimation"}).get_text(),
            }
            player_game_info["PlayerStats"].append(player_game_stat)
        
        for event in player_events_tag:
            player_event_info = {
                "EventType": event.find("span", attrs={"class": "Opta-Event-Text-Type"}).get_text(),
                "EventTime": event.find("span", attrs={"class": "Opta-Event-Time"}).get_text().replace("\u200e", "")
            }
            player_game_info["Events"].append(player_event_info)
        
        # player_events = 
        # print("----------------------------------------------->")
        # print(player_stats_tag)
        return player_game_info
        
        

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
