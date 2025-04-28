import json

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
        self.add_teams = {'win': 0, 'lose': 0, 'tie': 0, 'pf': 0, 'pa': 0, 'd_win': 0, 'd_lose': 0, 'd_tie': 0, 'c_win': 0, 'c_lose': 0, 'c_tie': 0}
        self.team_info = self._get_team_info()
        self.standings = self._get_standings()
        self.divisions = self._populate_divisions()
        
    


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
    


    def _populate_divisions(self):
        divisions = {"AFC": {"EAST": [], "NORTH": [], "SOUTH": [], "WEST": []}, "NFC": {"EAST": [], "NORTH": [], "SOUTH": [], "WEST": []}}
        for conf in divisions:
            for div in divisions[conf]:
                for team in self.standings:
                    if self.team_info[team]["division"] == div and self.team_info[team]["conference"] == conf:
                        values = list(self.standings[team].values())
                        values.insert(3, values[0] / sum(values[:3]))
                        values.insert(0, team)
                        divisions[conf][div].append(values)
        return divisions



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



    def _head_to_head(self, team1: str, team2: str) -> bool:
        t1_wins = 0
        t2_wins = 0
        for game, stats in self.games.items():
            team_id = game[0]
            opp_id = stats['opp_id']
            
            if (team_id == team1 and opp_id == team2) or (team_id == team2 and opp_id == team1):
                winner = team_id if stats["pf"] > stats["pa"] else opp_id if stats["pf"] < stats["pa"] else None
                
                if winner == team1:
                    t1_wins += 1
                elif winner == team2:
                    t2_wins += 1
                
        return True if t1_wins > t2_wins else False if t1_wins < t2_wins else None
    


    def _div_pct(self, team1: str, team2: str):
        t1_pct = self.standings[team1]["d_win"] / (self.standings[team1]["d_win"] + self.standings[team1]["d_lose"] + self.standings[team1]["d_tie"])
        t2_pct = self.standings[team2]["d_win"] / (self.standings[team2]["d_win"] + self.standings[team2]["d_lose"] + self.standings[team2]["d_tie"])
        return True if t1_pct > t2_pct else False if t1_pct < t2_pct else None
    


    def _get_opps(self, team: str) -> list:
        opps = {}
        for game, stats in self.games.items():
            if game[0] == team:
                point = 1 if stats['pf'] > stats['pa'] else 0 if stats['pf'] < stats['pa'] else 0.5
                if stats['opp_id'] not in opps:
                    opps[stats['opp_id']] = point
                else:
                    opps[stats['opp_id']] += point
        return opps
    


    def _common_pct(self, team1: str, team2: str):
        t1_opps = self._get_opps(team1)
        t2_opps = self._get_opps(team2)
        common_opps = set(set(t1_opps) & set(t2_opps))
        
        t1_points = sum([t1_opps[opp] for opp in common_opps])
        t2_points = sum([t2_opps[opp] for opp in common_opps])
        return True if t1_points > t2_points else False if t1_points < t2_points else None
    


    def _conf_pct(self, team1: str, team2: str):
        t1_pct = self.standings[team1]["c_win"] / (self.standings[team1]["c_win"] + self.standings[team1]["c_lose"] + self.standings[team1]["c_tie"])
        t2_pct = self.standings[team2]["c_win"] / (self.standings[team2]["c_win"] + self.standings[team2]["c_lose"] + self.standings[team2]["c_tie"])
        return True if t1_pct > t2_pct else False if t1_pct < t2_pct else None
    


    def _sov(self, team: str):
        opps = self._get_opps(team)
        sov = {'wins': 0, 'losses': 0, 'tie': 0}
        for opp, points in opps.items():
            if points == 1:
                sov['wins'] += self.standings[opp]['win']
                sov['losses'] += self.standings[opp]['lose']
                sov['tie'] += self.standings[opp]['tie']
        
        return sov['wins'] / (sov['wins'] + sov['losses'] + sov['tie'])
    


    def _sov_diff(self, team1: str, team2: str):
        t1_sov = self._sov(team1)
        t2_sov = self._sov(team2)
        return True if t1_sov > t2_sov else False if t1_sov < t2_sov else None
    



    def _div_tie_breaker(self, team1: str, team2: str):
        # Head to head
        head_to_head = self._head_to_head(team1, team2)
        if head_to_head is not None:
            return (team1, team2) if head_to_head else (team2, team1)
        # Div %
        div_pct = self._div_pct(team1, team2)
        if div_pct is not None:
            return (team1, team2) if div_pct else (team2, team1)
        # Common %
        common_pct = self._common_pct(team1, team2)
        if common_pct is not None:
            return (team1, team2) if common_pct else (team2, team1)
        # Conf %
        conf_pct = self._conf_pct(team1, team2)
        if conf_pct is not None:
            return (team1, team2) if conf_pct else (team2, team1)
        # SoV
        sov_diff = self._sov_diff(team1, team2)
        if sov_diff is not None:
            return (team1, team2) if sov_diff else (team2, team1)
        # SoS
        # avg pf + pa in conf
        # avg pf + pa in league
        # diff common
        # diff all
        # tds
        # coin flip
        return (None, None)



    def division_standings(self):
        for conf in self.divisions:
            for div in self.divisions[conf]:
                new_order = []
                sorted_div = sorted(self.divisions[conf][div], key=lambda x: x[4], reverse=True)
                for team in range(len(sorted_div)):
                    if len(new_order) >= len(sorted_div):
                        break

                    if team < len(sorted_div) - 1 and sorted_div[team][4] == sorted_div[team + 1][4]:
                        better, worse = self._div_tie_breaker(sorted_div[team][0], sorted_div[team + 1][0])
                        if better is None and worse is None:
                            a = 5
                        new_order.append(better)
                        new_order.append(worse)
                    else:
                        new_order.append(sorted_div[team])
            
                self.divisions[conf][div] = new_order
                    
        return self.divisions



if __name__ == "__main__":
    for year in range(2006, 2025):
        get_ranks = GetRanks(year, "0.0")
        division_standings = get_ranks.division_standings()