import time
import random

from bracket import Bracket
from get_stats import GetStats
from converter import Converter


TEAM = False
PRINT = True
OFFENSE = True
STARTUP = True
DEFENSE = False
PER_GAME = True
STATS = {"passing": True, "rushing": True, "receiving": True, "pass_blocking" : True, "run_blocking" : True, "pass_rush" : False, "run_defense" : False, "coverage" : False}


class Team():

    def __init__(self, team_abr: str, year: int, version: str):
        self.year = year
        self.version = version
        self.team_abr = team_abr
        self.get_stats = GetStats()
        self.converter = Converter()
        self.stats = {'offense': {}, 'defense': {}}
        self.team_key = f"{team_abr}_{year}_{version}"

        # Function Calls
        self._get_stats()



    def __repr__(self):
        return self.team_key
    


    def _get_stats(self):
        args = {"start_week": None, "end_week": None, "start_year": self.year, "end_year": self.year, "stat_type": None, "league": 'NFL', "version": self.version, "pos": None, "limit": None, "team": self.team_abr}
        self.stats['offense'] = self.get_stats.get_total_stats(args, OFFENSE)
        self.stats['defense'] = self.get_stats.get_total_stats(args, DEFENSE)



class Stats():

    def __init__(self):
        pass



    def bin_values(self, values: list[int]) -> dict:
        # finding the min and max values of the list
        min_val, max_val = float('inf'), float('-inf')
        for val in values:
            min_val = min(min_val, val)
            max_val = max(max_val, val)
        # calculating the range of the list
        range_val = max_val - min_val
        # finding out the number of bins in the list
        amount_bins = round(len(values) ** 0.5)
        # calculating the bin width
        bin_width = range_val / amount_bins
        bins = {}
        add = min_val
        for _ in range(amount_bins):
            bins[add] = {'values': [], 'pct': 0}
            add += bin_width
        return bins
    


    def find_bin(self, score: int, bins: list) -> int | None:
        if score >= bins[-1]:
            return bins[-1]

        for key in bins:
            if score <= key:
                return key
            
        return None
    


    def get_histogram(self, team: Team, side_of_ball: str):
        values = [team.stats[side_of_ball]['scoring'][week]['FP'] for week in team.stats[side_of_ball]['scoring']]
        bins = self.bin_values(values)

        for week in team.stats[side_of_ball]['scoring']:
            bin_key = self.find_bin(team.stats[side_of_ball]['scoring'][week]['FP'], list(bins.keys()))
            bins[bin_key]['values'].append(week)

        del_keys = []
        total_pct = 0
        pct_dict = {}
        for bin_key in bins:
            if len(bins[bin_key]['values']) == 0:
                del_keys.append(bin_key)
                continue
            
            pct = len(bins[bin_key]['values']) / len(team.stats[side_of_ball]['scoring'])
            bins[bin_key]['pct'] = pct + total_pct
            pct_dict[pct + total_pct] = bin_key
            total_pct += pct

        for bin_key in del_keys:
            del bins[bin_key]

        return bins, pct_dict



class Simulation:

    def __init__(self):
        self.teams = set()
        self.stats = Stats()
        self.histograms = {}
        self.team_stats = {}
        pass



    def sim_game(self, team1: Team, team2: Team, startup: bool = True, print_score: bool = True) -> int | None:
        if startup:
            self._sim_startup(team1)
            self._sim_startup(team2)

        # team1 offense & defense
        team1_offense_game = self._get_game(team1, 'offense')
        team1_defense_game = self._get_game(team1, 'defense')

        # team2 offense & defense
        team2_offense_game = self._get_game(team2, 'offense')
        team2_defense_game = self._get_game(team2, 'defense')

        # Calculate final scores
        team1_final_score = round((team1_offense_game + team2_defense_game) / 2, 2)
        team2_final_score = round((team2_offense_game + team1_defense_game) / 2, 2)

        # Determine winner (1 for team1, -1 for team2, 0 for tie)
        winner = (team1_final_score > team2_final_score) - (team1_final_score < team2_final_score)

        self.team_stats[team1.team_key]['offense']['score'] += team1_offense_game
        self.team_stats[team2.team_key]['offense']['score'] += team2_offense_game
        self.team_stats[team1.team_key]['defense']['score'] += team1_defense_game
        self.team_stats[team2.team_key]['defense']['score'] += team2_defense_game

        if winner == 1:
            self.team_stats[team1.team_key]['score']['wins'] += 1
            self.team_stats[team2.team_key]['score']['losses'] += 1
        elif winner == -1:
            self.team_stats[team2.team_key]['score']['wins'] += 1
            self.team_stats[team1.team_key]['score']['losses'] += 1
        else:
            self.team_stats[team1.team_key]['score']['ties'] += 1
            self.team_stats[team2.team_key]['score']['ties'] += 1

        if print_score:
            self._print_results({
                'team1_score': team1_final_score,
                'team2_score': team2_final_score
            })
            return None

        return winner
    


    def best_of(self, team1: Team, team2: Team, series_length: int, print_result: bool = True) -> int | None:
        self._sim_startup(team1)
        self._sim_startup(team2)

        first_to = series_length // 2 + 1
        wins = {'t1': 0, 't2': 0}
        while wins['t1'] < first_to and wins['t2'] < first_to:
            score = self.sim_game(team1, team2, startup=False, print_score=False)
            if score == 1:
                wins['t1'] += 1
            elif score == -1:
                wins['t2'] += 1

        if print_result:
            self._print_results(wins)

        return 1 if wins['t1'] > wins['t2'] else -1




    def sim_bracket(self, teams: list[Team], series_length: int) -> None:
        bracket = Bracket(teams)
        playoff_bracket = bracket.generate_bracket()

        winners = []
        losers = []        
        for i, rd in enumerate(playoff_bracket):
            round_id = len(playoff_bracket) - i
            for match in rd:
                team1, team2 = match
                print(f"Simulating {team1[1].team_key} vs {team2[1].team_key} in round {round_id}")
                result = self.best_of(team1[1], team2[1], series_length, print_result=False)

                if result == 1: # team1 won the series
                    winner = team1
                    loser = team2
                elif result == -1: # team2 won the series
                    winner = team2
                    loser = team1
                
                print(f"Winner: {winner[1].team_key} Loser: {loser[1].team_key}\n")
                winners.append(winner)
                losers.append(loser)
                if round_id == 1:
                    self.team_stats[winner[1].team_key]['score']['best_round'] = round_id - 1
                    self.team_stats[loser[1].team_key]['score']['best_round'] = round_id
                else:
                    self.team_stats[loser[1].team_key]['score']['best_round'] = round_id

            if i != len(playoff_bracket) - 1:
                bracket.add_winners(winners, i + 1)

        return winners[-1]
    


    def _sim_startup(self, team: Team) -> None:
        if team.team_key not in self.teams:
            self.teams.add(team.team_key)
            self._create_histogram(team)
    


    def _create_histogram(self, team: Team):
        team_key = team.team_key
        self.histograms[team_key] = {}
        for side_of_ball in team.stats:
            bins, pct_dict = self.stats.get_histogram(team, side_of_ball)
            self.histograms[team_key][side_of_ball] = {'bins': bins, 'pct_dict': pct_dict}
        
        self.team_stats[team_key] = {'score': {'wins': 0, 'losses': 0, 'ties': 0, 'best_round': None}, 'offense': {'score': 0}, 'defense': {'score': 0}}

    

    def _get_game(self, team: Team, side_of_ball: str) -> int:
        team_key = team.team_key
        pcts = self.histograms[team_key][side_of_ball]['pct_dict']
        pct = random.random()
        games = None
        for pct_key in pcts:
            if pct <= pct_key:
                games = self.histograms[team_key][side_of_ball]['bins'][pcts[pct_key]]['values']
                break
        
        if games is None:
            raise ValueError(f"No games found for {team_key} {side_of_ball}")
        
        week = random.choice(games)
        key = 'pts_for' if side_of_ball == 'offense' else 'pts_against'
        score = team.stats[side_of_ball]['game_data'][week][key]
        return score






if __name__ == "__main__":
    year = 2010
    games = 70_000
    version = "0.0"

    print("Grabbing team stats...")
    start_time = time.time()
    teams = [
        # (1, Team("SD" if year < 2017 else 'LAC', year, version)),
        # (2, Team("BLT", year, version)),
        # (3, Team("CHI", year, version)),
        # (4, Team("NE", year, version)),
        # (5, Team("IND", year, version)),
        # (6, Team("NO", year, version)),
        # (7, Team("PHI", year, version)),
        # (8, Team("NYJ", year, version)),
        # (9, Team("DAL", year, version)),
        # (10, Team("DEN", year, version)),
        # (11, Team("KC", year, version)),
        # (12, Team("SEA", year, version)),
        # (13, Team("JAX", year, version)),
        # (14, Team("CIN", year, version)),
        # (15, Team("PIT", year, version)),
        # (16, Team("NYG", year, version)),
        # (17, Team("TEN", year, version)),
        # (18, Team("CAR", year, version)),
        # (19, Team("SL" if year < 2016 else 'LA', year, version)),
        # (20, Team("GB", year, version)),
        # (21, Team("BUF", year, version)),
        # (22, Team("ATL", year, version)),
        # (23, Team("SF", year, version)),
        # (24, Team("MIA", year, version)),
        # (25, Team("MIN", year, version)),
        # (26, Team("HST", year, version)),
        # (27, Team("WAS", year, version)),
        # (28, Team("ARZ", year, version)),
        # (29, Team("CLV", year, version)),
        # (30, Team("TB", year, version)),
        # (31, Team("DET", year, version)),
        # (32, Team("OAK" if year < 2020 else 'LV', year, version))
(0, Team('NE', 2007, 0.0)),
(1, Team('SEA', 2013, 0.0)),
(2, Team('NE', 2012, 0.0)),
(3, Team('BLT', 2019, 0.0)),
(4, Team('NE', 2016, 0.0)),
(5, Team('NE', 2010, 0.0)),
(6, Team('BUF', 2021, 0.0)),
(7, Team('DET', 2024, 0.0)),
(8, Team('BLT', 2023, 0.0)),
(9, Team('GB', 2011, 0.0)),
(10, Team('DEN', 2013, 0.0)),
(11, Team('NE', 2011, 0.0)),
(12, Team('DAL', 2023, 0.0)),
(13, Team('TB', 2020, 0.0)),
(14, Team('SF', 2019, 0.0)),
(15, Team('IND', 2007, 0.0)),
(16, Team('SF', 2023, 0.0)),
(17, Team('SF', 2022, 0.0)),
(18, Team('NO', 2009, 0.0)),
(19, Team('SD', 2006, 0.0)),
(20, Team('NE', 2015, 0.0)),
(21, Team('NE', 2014, 0.0)),
(22, Team('GB', 2009, 0.0)),
(23, Team('NE', 2019, 0.0)),
(24, Team('PHI', 2022, 0.0)),
(25, Team('DEN', 2012, 0.0)),
(26, Team('NO', 2018, 0.0)),
(27, Team('CAR', 2015, 0.0)),
(28, Team('BLT', 2008, 0.0)),
(29, Team('CHI', 2018, 0.0)),
(30, Team('NE', 2013, 0.0)),
(31, Team('SEA', 2015, 0.0)),
(32, Team('KC', 2015, 0.0)),
(33, Team('NO', 2011, 0.0)),
(34, Team('PHI', 2017, 0.0)),
(35, Team('PHI', 2024, 0.0)),
(36, Team('NE', 2006, 0.0)),
(37, Team('GB', 2014, 0.0)),
(38, Team('MIN', 2009, 0.0)),
(39, Team('NE', 2018, 0.0)),
(40, Team('SF', 2011, 0.0)),
(41, Team('BUF', 2022, 0.0)),
(42, Team('GB', 2021, 0.0)),
(43, Team('SEA', 2012, 0.0)),
(44, Team('BUF', 2020, 0.0)),
(45, Team('LA', 2017, 0.0)),
(46, Team('PIT', 2010, 0.0)),
(47, Team('GB', 2010, 0.0)),
(48, Team('LA', 2018, 0.0)),
(49, Team('TB', 2021, 0.0)),
(50, Team('SF', 2013, 0.0)),
(51, Team('ATL', 2016, 0.0)),
(52, Team('CIN', 2022, 0.0)),
(53, Team('KC', 2022, 0.0)),
(54, Team('GB', 2007, 0.0)),
(55, Team('DAL', 2019, 0.0)),
(56, Team('HST', 2011, 0.0)),
(57, Team('TEN', 2008, 0.0)),
(58, Team('DAL', 2007, 0.0)),
(59, Team('NE', 2009, 0.0)),
(60, Team('TB', 2024, 0.0)),
(61, Team('GB', 2016, 0.0)),
(62, Team('GB', 2015, 0.0)),
(63, Team('BUF', 2024, 0.0)),
    ]

    end_time = time.time()
    print(f"Time taken to load data: {end_time - start_time} seconds\n")

    sorted_teams = []
    for i, team in enumerate(teams):
        off_score = sum([team[1].stats['offense']['scoring'][week]['FP'] for week in team[1].stats['offense']['scoring']])
        def_score = sum([team[1].stats['defense']['scoring'][week]['FP'] for week in team[1].stats['defense']['scoring']])
        diff = off_score - def_score
        sorted_teams.append((i, diff))
    sorted_teams = sorted(sorted_teams, key=lambda x: x[1], reverse=True)
    
    new_teams = []
    for i, (index, diff) in enumerate(sorted_teams):
        team = teams[index]
        adder = (i, team[1])
        new_teams.append(adder)
    teams = new_teams

    print(f"Simulating Bracket... (Each series is a best of {games})")
    start_time = time.time()
    simulation = Simulation()
    simulation.sim_bracket(teams, games)
    end_time = time.time()
    print(f"\nTime taken: {end_time - start_time} seconds")
    print("Simulation complete")
    
    # Sort team_stats by best_round, wins, and offense-defense score difference
    sorted_teams = []
    for team_key, stats in simulation.team_stats.items():
        # For sorting, convert None to a high number
        best_round = stats['score']['best_round'] if stats['score']['best_round'] is not None else 999
        wins = stats['score']['wins']
        score_diff = stats['offense']['score'] - stats['defense']['score']
        sorted_teams.append((team_key, stats, best_round, wins, score_diff))
    
    # Sort by best_round (ascending), wins (descending), score_diff (descending)
    sorted_teams.sort(key=lambda x: (x[2], -x[3], -x[4]))
    
    # Create a new sorted dictionary
    sorted_team_stats = {}
    for team_key, stats, _, _, _ in sorted_teams:
        sorted_team_stats[team_key] = stats

    for i, team in enumerate(sorted_teams):
        team_win_pct = team[1]['score']['wins'] / (team[1]['score']['wins'] + team[1]['score']['losses'] + team[1]['score']['ties'] * 0.5) * 100
        team_score_diff = team[1]['offense']['score'] - team[1]['defense']['score']
        team_best_round = team[1]['score']['best_round']
        print(f"{i + 1}. {team[0]} {team_win_pct:.2f}% {team_score_diff} {team_best_round}")
    