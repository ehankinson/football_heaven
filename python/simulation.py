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
        self.stats = Stats()
        self.histograms = {}
        pass



    def sim_game(self, team1: Team, team2: Team, startup: bool = True, print_score: bool = True) -> int | None:
        if startup:
            self._sim_startup(team1, team2)

        # team1 offense & defense
        team1_offense_game = self._get_game(self.team1, 'offense')
        team1_defense_game = self._get_game(self.team1, 'defense')

        # team2 offense & defense
        team2_offense_game = self._get_game(self.team2, 'offense')
        team2_defense_game = self._get_game(self.team2, 'defense')

        # Calculate final scores
        team1_final_score = round((team1_offense_game + team2_defense_game) / 2, 2)
        team2_final_score = round((team2_offense_game + team1_defense_game) / 2, 2)

        # Determine winner (1 for team1, 2 for team2, 0 for tie)
        winner = (team1_final_score > team2_final_score) - (team1_final_score < team2_final_score)

        if print_score:
            self._print_results({
                'team1_score': team1_final_score,
                'team2_score': team2_final_score
            })
            return None

        return winner
    


    def best_of(self, team1: Team, team2: Team, series_length: int) -> None:
        self._sim_startup(team1, team2)

        first_to = series_length // 2 + 1
        wins = {'t1': 0, 't2': 0}
        while wins['t1'] < first_to and wins['t2'] < first_to:
            score = self.sim_game(team1, team2, startup=False, print_score=False)
            if score == 1:
                wins['t1'] += 1
            elif score == -1:
                wins['t2'] += 1

        self._print_results(wins)



    def sim_bracket(self, teams: list[Team], series_length: int) -> None:
        bracket = Bracket(teams)
        pass



    def _print_results(self, wins: dict) -> None:
        if 't1' in wins and 't2' in wins:
            # This is a series result
            print(f"\nSeries Results:")
            print(f"{self.team1.team_key}: {wins['t1']} wins")
            print(f"{self.team2.team_key}: {wins['t2']} wins")
            t1_win_pct = f"{(wins['t1'] / (wins['t1'] + wins['t2'])) * 100:.2f}%"
            t2_win_pct = f"{(wins['t2'] / (wins['t1'] + wins['t2'])) * 100:.2f}%"
            print(f"Win Percentage: {t1_win_pct} {t2_win_pct}")
            if wins['t1'] > wins['t2']:
                print(f"Series Winner: {self.team1.team_key}")
            elif wins['t2'] > wins['t1']:
                print(f"Series Winner: {self.team2.team_key}")
            else:
                print("Series ended in a tie")
        else:
            # This is a single game result
            team1_score = wins.get('team1_score', 0)
            team2_score = wins.get('team2_score', 0)
            if team1_score > team2_score:
                print(f"Winner: {self.team1.team_key} {team1_score} - Loser: {self.team2.team_key} {team2_score}")
            elif team2_score > team1_score:
                print(f"Winner: {self.team2.team_key} {team2_score} - Loser: {self.team1.team_key} {team1_score}")
            else:
                print(f"Tie: {self.team1.team_key} {team1_score} - {self.team2.team_key} {team2_score}")
    


    def _sim_startup(self, team1: Team, team2: Team) -> None:
        self.team1 = team1
        self.team2 = team2
        self._create_histogram(self.team1)
        self._create_histogram(self.team2)
    


    def _create_histogram(self, team: Team):
        team_key = team.team_key
        self.histograms[team_key] = {}
        for side_of_ball in team.stats:
            bins, pct_dict = self.stats.get_histogram(team, side_of_ball)
            self.histograms[team_key][side_of_ball] = {'bins': bins, 'pct_dict': pct_dict}

    

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
        score = team.stats[side_of_ball]['scoring'][week]['FP']
        return score






if __name__ == "__main__":
    year = 2006
    games = 70_000
    version = "0.0"

    start_time = time.time()
    teams = [
        Team("SD", year, version),
        Team("BLT", year, version),
        Team("IND", year, version),
        Team("NE", year, version),
        Team("NYJ", year, version),
        Team("KAN", year, version)
    ]
    end_time = time.time()
    print(f"Time taken to load data: {end_time - start_time} seconds\n")

    print(f"Simulating Bracket... (Each series is a best of {games})")
    start_time = time.time()
    simulation = Simulation()
    simulation.sim_bracket(teams, games)
    end_time = time.time()
    print(f"\nTime taken: {end_time - start_time} seconds")
    print("Simulation complete")
    