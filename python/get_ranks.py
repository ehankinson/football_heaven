from db import DB
from converter import Converter

TEAM = False

class GetRanks():

    def __init__(self, year: int, version: str) -> None:
        self.year = year
        self.version = version
        self.db = DB()
        self.converter = Converter()
        self.games = self.get_games()
        self.divisions = {"AFC": {"EAST": [], "NORTH": [], "SOUTH": [], "WEST": []}, "NFC": {"EAST": [], "NORTH": [], "SOUTH": [], "WEST": []}}
        self.add_teams = {'win': 0, 'lose': 0, 'tie': 0, 'pf': 0, 'pa': 0, 'd_win': 0, 'd_lose': 0, 'd_ties': 0, 'c_win': 0, 'c_lose': 0, 'c_ties': 0}
        self.team_info = self._get_team_info()
        self.standings = self._get_standings()
    


    def _get_team_info(self):
        teams = self.db.call_query("SELECT * FROM TEAMS WHERE League = 'NFL'")
        info = {}
        for team in teams:
            info[team[0]] = {"abbr": team[1], "league": team[2], "name": team[3], "division": team[4], "conference": team[5]}
        return info



    def _fast_games(self, games: list):
        return {(game["team_id"], game["week"]): game for game in games}



    def get_games(self):
        # getting regular season games
        return self._fast_games(self.converter.convert_results(self.db.get_games(year=self.year, start_week=1, end_week=18, version=self.version), TEAM, "game_data"))
    


    def _get_standings(self):
        standings = {}
        for key, value in self.games.items():
            team_id = key[0]
            opp_id = value["opp_id"]

            if team_id not in standings:
                standings[team_id] = self.add_teams.copy()

            pf = value["pf"]
            pa = value["pa"]
            standings[team_id]["pf"] += pf
            standings[team_id]["pa"] += pa

            same_div = self.team_info[team_id]["division"] == self.team_info[opp_id]["division"]
            same_conf = self.team_info[team_id]["conference"] == self.team_info[opp_id]["conference"]
            win = 1 if pf > pa else 0 if pf < pa else 0.5
            win_key = "win" if win == 1 else "lose" if win == 0 else "tie"
            standings[team_id][win_key] += 1

            if same_conf:
                conf_key = "c_" + win_key
                standings[team_id][conf_key] += 1

            if same_div and same_conf:
                div_key = "d_" + win_key
                standings[team_id][div_key] += 1  

        return standings



    def _div_tie_breaker(self):
        a = 5
        # Head to head
        # Div %
        # Common %
        # Conf %
        # SoV
        # SoS
        # avg pf + pa in conf
        # avg pf + pa in league
        # diff common
        # diff all
        # tds
        # coin flip



    def division_standings(self):
        division = {}
        for conf in self.divisions:
            for div in self.divisions[conf]:
                a = 5



if __name__ == "__main__":
    get_ranks = GetRanks(2024, "0.0")
    division_standings = get_ranks.division_standings()