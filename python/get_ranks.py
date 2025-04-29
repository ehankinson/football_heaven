import json

from db import DB
from converter import Converter

TEAM = False
TEAM_ID = 0
WIN_PCT = 4
ASC = True
DESC = False

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
            info[team[0]] = {"abbr": team[1], "league": team[2], "name": team[3], "division": team[WIN_PCT], "conference": team[5]}
        return info



    def _fast_games(self, games: list):
        return {(game["team_id"], game["week"]): game for game in games}



    def get_games(self):
        # getting regular season games
        return self._fast_games(self.converter.convert_results(self.db.get_games(year=self.year, start_week=1, end_week=18, version=self.version), TEAM, "game_data"))
    


    def _get_div_pct(self, team: str):
        return self.standings[team]["d_win"] / (self.standings[team]["d_win"] + self.standings[team]["d_lose"] + self.standings[team]["d_tie"])



    def _get_conf_pct(self, team: str):
        return self.standings[team]["c_win"] / (self.standings[team]["c_win"] + self.standings[team]["c_lose"] + self.standings[team]["c_tie"])



    def _net_points(self, team: str):
        return self.standings[team]['pf'] - self.standings[team]['pa']



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



    def _return_teams(self, teams: list, sorted_teams: list, check_id: int):
        val = 0
        while val < len(sorted_teams) - 1:
            if sorted_teams[val][check_id] == sorted_teams[val + 1][check_id]:
                val += 1
            else:
                return (True, [team[0] for team in sorted_teams])
        
        return (False, teams)
    


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
    


    def _strenght_loop(self, _type: str, team: str):
        opps = self._get_opps(team)
        strength = {'wins': 0, 'losses': 0, 'tie': 0}
        for opp, points in opps.items():
            add = True if (_type == "sov" and points == 1) or (_type == "sos") else False
            
            if add:
                strength['wins'] += self.standings[opp]['win']
                strength['losses'] += self.standings[opp]['lose']
                strength['tie'] += self.standings[opp]['tie']
    

    def _sov(self, team: str):
        sov = self._strenght_loop("sov", team)
        return sov['wins'] / (sov['wins'] + sov['losses'] + sov['tie'])



    def _sos(self, team: str):
        sos = self._strenght_loop("sos", team)
        return sos['wins'] / (sos['wins'] + sos['losses'] + sos['tie'])
    

    
    def _get_common_opps(self, teams: list) -> tuple[dict, set]:
        opps = {}
        set_opps = []
        for team in teams:
            opps[team] = self._get_opps(team)
            set_opps.append(set(opps[team]))

        common_opps = set.intersection(*set_opps) if set_opps else set()
        return opps, common_opps



    def _is_same(self, sorted_list: list, teams: list) -> list:
        is_same = {}
        for team in sorted_list:
            weight = team[1]
            if weight not in is_same:
                is_same[weight] = []
            is_same[weight].append(team[0])
        
        ranked_teams = []
        for weight in is_same:
            if len(is_same[weight]) == 1:
                ranked_teams.append(is_same[weight][0])
        
        if len(ranked_teams) > 0:
            return True, ranked_teams
        else:
            return False, teams



    def _head_to_head(self, teams: list) -> tuple[bool, list]:
        h2h = {}
        for team in teams:
            h2h[team] = {'team': team, 'wins': 0, 'losses': 0, 'ties': 0}
        
        for game, stats in self.games.items():
            if game[0] in teams and stats['opp_id'] in teams:
                key = 'wins' if stats['pf'] > stats['pa'] else 'losses' if stats['pf'] < stats['pa'] else 'ties'
                h2h[game[0]][key] += 1
                
        values = [list(h2h[team].values()) for team in teams]
        sorted_values = sorted(values, key=lambda x: x[1], reverse=True)
        return self._is_same(sorted_values, teams)
    


    def _div_pct(self, teams: list):
        div_pct = []
        for team in teams:
            new_pct = self._get_div_pct(team)
            div_pct.append([team, new_pct])

        sorted_div_pct = sorted(div_pct, key=lambda x: x[1], reverse=True)
        return self._is_same(sorted_div_pct, teams)

    


    def _common_pct(self, teams: list):
        opps, common_opps = self._get_common_opps(teams)

        points = []
        for team in teams:
            sum_array = sum([opps[team][opp] for opp in common_opps])
            points.append([team, sum_array])

        sorted_points = sorted(points, key=lambda x: x[1], reverse=True)
        return self._is_same(sorted_points, teams)
    


    def _conf_pct(self, teams: list):
        conf_pct = {}
        for team in teams:
            conf_pct[team] = self._get_conf_pct(team)

        sorted_conf_pct = sorted(conf_pct.items(), key=lambda x: x[1], reverse=True)
        return self._is_same(sorted_conf_pct, teams)
    


    def _sov_diff(self, teams: list):
        sov = {}
        for team in teams:
            sov[team] = self._sov(team)

        sorted_sov = sorted(sov.items(), key=lambda x: x[1], reverse=True)
        return self._is_same(sorted_sov, teams)
    


    def _sos_diff(self, teams: list):
        sos = {}
        for team in teams:
            sos[team] = self._sos(team)

        sorted_sov = sorted(sos.items(), key=lambda x: x[1], reverse=True)
        return self._is_same(sorted_sov, teams)



    def _net_points_diff(self, teams: list):
        opps, common_opps = self._get_common_opps(teams)
        a = 5
        return True if t1_net > t2_net else False if t1_net < t2_net else None
    



    def _div_tie_breaker(self, teams: list):
        # Head to head
        status, teams = self._head_to_head(teams)
        if status:
            return teams
        # Div %
        status, teams = self._div_pct(teams)
        if status:
            return teams
        # Common %
        status, teams = self._common_pct(teams)
        if status:
            return teams
        # Conf %
        status, teams = self._conf_pct(teams)
        if status:
            return teams
        # SoV
        status, teams = self._sov_diff(teams)
        if status:
            return teams
        # SoS
        status, teams = self._sos_diff(teams)
        if status:
            return teams
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
                sorted_div = sorted(self.divisions[conf][div], key=lambda x: x[WIN_PCT], reverse=True)
                while len(sorted_div) > 0:
                    team = 0
                    
                    index = team + 1
                    checks = [sorted_div[team][TEAM_ID]]
                    while index < len(sorted_div) and sorted_div[team][WIN_PCT] == sorted_div[index][WIN_PCT]:
                        checks.append(sorted_div[index][TEAM_ID])
                        index += 1
                    
                    if len(checks) > 1:
                        if len(checks) == 3:
                            a = 5
                        sorted_teams = self._div_tie_breaker(checks)
                        total_stats = []
                        for team_id in sorted_teams:
                            team_values = list(self.standings[team_id].values())
                            team_values.insert(3, team_values[0] / sum(team_values[:3]))
                            team_values.insert(0, team_id)
                            total_stats.append(team_values)

                            sort_index = next(i for i, team in enumerate(sorted_div) if team[TEAM_ID] == team_id)
                            sorted_div.pop(sort_index)

                        new_order.extend(total_stats)
                    else:
                        new_order.append(sorted_div[team])
                        sorted_div.pop(team)
            
                self.divisions[conf][div] = new_order
                    
        return self.divisions



if __name__ == "__main__":
    for year in range(2006, 2025):
        get_ranks = GetRanks(year, "0.0")
        division_standings = get_ranks.division_standings()