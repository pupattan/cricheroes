"""
Modules
"""
import time
import re
import copy
import json
import datetime
from pathlib import Path

# External modules
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from dateutil.parser import parse
from selenium.webdriver.common.keys import Keys
import platform

class Player:
    """
    This class stores player details like name(title), sub title, profile url (for detailed info), profile pic url
    """

    def __init__(self, name, sub_title, profile_url, profile_pic_url):
        """
        Constructor for Player class

        :param name: name(title)
        :param sub_title: sub title
        :param profile_url: profile url (for detailed info)
        :param profile_pic_url: profile pic url
        """
        self.name = name
        self.sub_title = sub_title
        self.profile_url = profile_url
        self.profile_pic_url = profile_pic_url


class TeamStat:
    """
    This class contains overall team statistics like how many matches played, won, lost etc
    """

    def __init__(self, label, value):
        """
        Constructor for TeamStat

        :param label: Label like matches played, won and lost
        :param value: values like 10, 45% etc
        """

        self.label = label
        self.value = value


class Match:
    """
    This class contains information like tournament, scores, result, venue, date about a match
    """

    def __init__(self, tournament, info, score, result, url):
        """
        Constructor for Match class

        :param tournament: To which tournament the match belongs
        :param info: Information about the venue, date, overs
        :param score: Score of all the teams
        :param result: Result of the match
        :param url: Match url for detail info
        """
        self.tournament = tournament
        self.info = info
        self.score = score
        self.result = result
        self.url = url

    @property
    def match_date(self):
        """
        Parse and return match date from info
        :return: date time object

        """
        datastring = self.info
        if len(self.info) > 2:
            datastring = self.info.split(",")[2]
        return parse(datastring, fuzzy=True).date()

    @property
    def venue(self):
        """
        Parse and return venue from info
        :return: venue as str

        """
        try:
            return self.info.split(',')[0]
        except Exception as e:
            return ""

    def asdict(self):
        __dict = copy.deepcopy(self.__dict__)
        __dict.update({'date': self.match_date, 'venue': self.venue})
        return __dict


class LeaderboardStat:
    """
    This class contains all details of the leader board and best performances in batting bowling and fielding
    """

    BATTING = 'batting'
    BOWLING = 'bowling'
    FIELDING = 'fielding'

    def __init__(self, player_name, stat, profile=BATTING):
        """
        Constructor for Leaderboard

        :param player_name: Name of the player
        :param stat: Statistics
        :param profile: batting, bowling, fileding
        """

        self.player_name = player_name
        self.stat = stat
        self.profile = profile


class ChJsonEncoder(json.JSONEncoder):
    """
    Class to encode objects
    """
    def default(self, o):
        if isinstance(o, Match):
            return o.asdict()
        elif isinstance(o, (datetime.datetime, datetime.date, datetime.time)):
            return o.strftime('%d-%b-%y')
        else:
            return o.__dict__


class Team:
    """
    Class to fetch team data from cricheroes.in
    """
    BASE_URL = 'https://cricheroes.in/team-profile'
    URL_PREFIX = 'team-profile'

    def __init__(self, url):
        """
        Constructor Team

        :param name: Team name to be given
        :param url: Team url

        """
        self.url = url
        self.page_texts = self.get_page_texts()
        self.name = ""
        self.logo = ""
        self.team_profile()

    def __get_full_url(self) -> str:
        return self.BASE_URL + "/" + self.url.lstrip()

    def get_players(self) -> list:
        soup = self.__get_soup(self.page_texts['members'])
        players_div_parent = soup.find(attrs={"class": "membersDiv"})  # membersDiv
        regex = re.compile(r'player\d+')
        players = []
        for player_div in players_div_parent.find_all("div", {"class": regex}):
            player = Player(name=player_div.select_one(".team-profile-player").get_text().strip(),
                            sub_title=player_div.select_one(".pmd-card-subtitle-text").get_text().strip(),
                            profile_url=player_div.find('a').get('href').strip(),
                            profile_pic_url=player_div.find('img').get('src').strip()
                            )
            players.append(player)
        return players

    def __click_and_fetch(self, driver, tab, text_div_class_or_id="", match_text="", by=By.ID, more_div_id="",
                          wait_for_item=""):
        driver.find_element(value=tab).click()
        time.sleep(5)
        if wait_for_item:
            start_time = time.time()
            while not driver.find_element(By.CLASS_NAME, wait_for_item) \
                    and time.time() - start_time < 60:
                print("Clicking tab {}.".format(tab))
                driver.find_element(value=tab).click()
                time.sleep(5)
                print("Checking for element to appear {}. {}".format(wait_for_item, time.time() - start_time))

        start_time = time.time()
        if more_div_id:
            while 'load more' in driver.find_element(value=more_div_id).text.lower() and time.time() - start_time < 60:
                driver.find_element(value=more_div_id).click()
                time.sleep(5)
                print("Checking load more for element to appear. {}".format(time.time() - start_time))

            driver.find_element(value='body', by=By.TAG_NAME).send_keys(Keys.CONTROL + Keys.HOME)
            time.sleep(5)
        start_time = time.time()
        if match_text:
            while match_text not in driver.find_element(value=text_div_class_or_id, by=by).text.lower() and \
                    time.time() - start_time < 30:
                time.sleep(5)
                print("Checking for matching element to appear . {}".format(time.time() - start_time))
        time.sleep(5)
        return copy.deepcopy(driver.page_source)

    def get_page_texts(self):
        data = {}
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        if 'win' not in platform.system().lower():
            options.add_argument('headless')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--remote-debugging-port=9222')
        driver = webdriver.Chrome(options=options)
        driver.get(self.__get_full_url())

        # Matches tab
        data['members'] = copy.deepcopy(driver.page_source)

        # Matches tab
        data['matches'] = self.__click_and_fetch(driver,
                                                 tab='matchesTab',
                                                 match_text="result",
                                                 text_div_class_or_id='tournamentmatches'
                                                 )
        data['stats'] = self.__click_and_fetch(driver,
                                               tab='statTab',
                                               match_text="matches",
                                               text_div_class_or_id='statsDiv',
                                               by=By.CLASS_NAME
                                               )

        # leaderboard tab
        data['leaderboard'] = dict()
        data['leaderboard'][LeaderboardStat.BATTING] = self.__click_and_fetch(driver,
                                                                              tab='leaderboardTab',
                                                                              match_text="batting stat",
                                                                              text_div_class_or_id=
                                                                              'leaderboard-section-title',
                                                                              by=By.CLASS_NAME,
                                                                              #more_div_id="loadMoreLeaderBoardBatting",
                                                                              wait_for_item="list-group-item-heading"
                                                                              )

        data['leaderboard'][LeaderboardStat.BOWLING] = self.__click_and_fetch(driver,
                                                                              tab='bowlingTab',
                                                                              by=By.CLASS_NAME,
                                                                              #more_div_id="loadMoreLeaderBoardBowling",
                                                                              wait_for_item="list-group-item-heading"
                                                                              )

        data['leaderboard'][LeaderboardStat.FIELDING] = self.__click_and_fetch(driver,
                                                                               tab='fieldingTab',
                                                                               by=By.CLASS_NAME,
                                                                               #more_div_id="loadMoreLeaderBoardFielding",
                                                                               wait_for_item="list-group-item-heading"
                                                                               )
        driver.quit()
        return data

    def __get_soup(self, text):
        return BeautifulSoup(text, 'html.parser')

    def team_profile(self):
        """
        Fetch and set team name and logo

        :return: None
        """
        soup = self.__get_soup(self.page_texts['members'])
        div_parent = soup.find(attrs={"id": "player-banner"})
        logo_div = div_parent.find(attrs={"class": "tournament-logo"})
        self.logo = logo_div.get('src').strip()
        self.name = logo_div.parent.parent.findNext(attrs={"class": 'pmd-card-title-text'}).get_text().strip()

    def get_matches(self):
        """
        Get match details recently  played by the team

        :return: list of Match objects

        """
        soup = self.__get_soup(self.page_texts['matches'])
        matches_div_parent = soup.find(attrs={"class": "matchesDiv"})
        matches = []
        regex = re.compile(r'section\d+')
        for match_div in matches_div_parent.find_all("div", {"class": "custom-card-matches"}):  # custom-card-matches
            score_body_div = match_div.find(attrs={"class": 'pmd-card-body'})
            score_list = []
            for score in score_body_div.find_all("div", {"class": regex}):
                score_text = " ".join(score.get_text().split('\n')).strip()
                score_list.append(score_text)
            match = Match(tournament=match_div.select_one('.matchtournamentDetail').get_text().strip(),
                          info=match_div.select_one('.test-match-card-title').get_text().strip(),
                          score=score_list,
                          url=match_div.find('a').get('href').strip(),
                          result=match_div.select_one('.test-result').get_text().strip()
                          )
            matches.append(match)
        return matches

    def get_team_stats(self):
        """
        Get over all team statistics from Stats tab

        :return: list of TeamStat objects

        """
        soup = self.__get_soup(self.page_texts['stats'])
        stats_div_parent = soup.find(attrs={"class": "statsDiv"})
        stats = []
        for stat_div in stats_div_parent.find_all("div", {"class": "stat-item"}):
            stats.append(TeamStat(value=stat_div.select_one('.stat-item-value').get_text().strip(),
                                  label=stat_div.select_one('.stat-item-name').get_text().strip()))
        return stats

    def __parse_leader_data(self, text_data, div_id, profile):
        soup = self.__get_soup(text_data)
        lead_div_parent = soup.find(attrs={"id": div_id})
        leaders = []
        for player_div in lead_div_parent.find_all("li", {"class": "list-group-item"}):
            leaders.append(
                LeaderboardStat(player_name=player_div.select_one('.list-group-item-heading').get_text().strip(),
                                stat=player_div.select_one('.list-group-item-text').get_text().strip(),
                                profile=profile))
        return leaders

    def get_leaderboard(self):
        """
        Get leaderboard details in dictionary

        :return: dict containing batting, bowling, fielding leaders
        """
        data = {
            LeaderboardStat.BATTING: self.__parse_leader_data(self.page_texts['leaderboard'][LeaderboardStat.BATTING],
                                                              div_id='battingLeaderboardList',
                                                              profile=LeaderboardStat.BATTING),
            LeaderboardStat.BOWLING: self.__parse_leader_data(self.page_texts['leaderboard'][LeaderboardStat.BOWLING],
                                                              div_id='bowlingLeaderboardList',
                                                              profile=LeaderboardStat.BOWLING),
            LeaderboardStat.FIELDING: self.__parse_leader_data(self.page_texts['leaderboard'][LeaderboardStat.BATTING],
                                                               div_id='fieldingLeaderboardList',
                                                               profile=LeaderboardStat.FIELDING)
        }
        return data

    def fetch_all_data(self):
        return {'team_name': self.name,
                'team_logo': self.logo,
                'players': self.get_players(),
                'matches': self.get_matches(),
                'stats': self.get_team_stats(),
                'leaderboard': self.get_leaderboard()
                }

    def dump_all(self):
        base_dir = Path("")
        out_path = base_dir / Path('out.json')
        with open(str(out_path.absolute()), 'w') as f:
            json.dump(self.fetch_all_data(), f, indent=4, cls=ChJsonEncoder)
        print("Json file created : " + str(out_path.absolute()))


if __name__ == '__main__':
    team = Team(url="345698/Spartans-CC---RED")
    team.dump_all()
