import time
import random
import matplotlib.pyplot as plt

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
        
        # Function Calls
        self._get_stats()



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

        total_pct = 0
        for bin_key in bins:
            pct = len(bins[bin_key]['values']) / len(team.stats[side_of_ball]['scoring'])
            bins[bin_key]['pct'] = pct + total_pct
            total_pct += pct

        return bins



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
        t1_wins = [0]
        t2_wins = [0]
        wins = {'t1': 0, 't2': 0}
        while wins['t1'] < first_to and wins['t2'] < first_to:
            score = self.sim_game(team1, team2, startup=False, print_score=False)
            if score == 1:
                wins['t1'] += 1
                t1_wins.append(t1_wins[-1] + 1)
                t2_wins.append(t2_wins[-1])
            elif score == -1:
                wins['t2'] += 1
                t2_wins.append(t2_wins[-1] + 1)
                t1_wins.append(t1_wins[-1])

        self._print_results(wins)
        plt.plot(t1_wins, label=f"{team1.team_abr}")
        plt.plot(t2_wins, label=f"{team2.team_abr}")
        plt.legend()
        plt.show()



    def _print_results(self, wins: dict) -> None:
        if 't1' in wins and 't2' in wins:
            # This is a series result
            print(f"\nSeries Results:")
            print(f"{self.team1.team_abr}: {wins['t1']} wins")
            print(f"{self.team2.team_abr}: {wins['t2']} wins")
            if wins['t1'] > wins['t2']:
                print(f"Series Winner: {self.team1.team_abr}")
            elif wins['t2'] > wins['t1']:
                print(f"Series Winner: {self.team2.team_abr}")
            else:
                print("Series ended in a tie")
        else:
            # This is a single game result
            team1_score = wins.get('team1_score', 0)
            team2_score = wins.get('team2_score', 0)
            if team1_score > team2_score:
                print(f"Winner: {self.team1.team_abr} {team1_score} - Loser: {self.team2.team_abr} {team2_score}")
            elif team2_score > team1_score:
                print(f"Winner: {self.team2.team_abr} {team2_score} - Loser: {self.team1.team_abr} {team1_score}")
            else:
                print(f"Tie: {self.team1.team_abr} {team1_score} - {self.team2.team_abr} {team2_score}")
    


    def _sim_startup(self, team1: Team, team2: Team) -> None:
        self.team1 = team1
        self.team2 = team2
        self._create_histogram(self.team1)
        self._create_histogram(self.team2)
    


    def _create_histogram(self, team: Team):
        self.histograms[team.team_abr] = {}
        for side_of_ball in team.stats:
            self.histograms[team.team_abr][side_of_ball] = self.stats.get_histogram(team, side_of_ball)

    

    def _get_game(self, team: Team, side_of_ball: str) -> int:
        pcts = {self.histograms[team.team_abr][side_of_ball][bin_key]['pct']: bin_key for bin_key in self.histograms[team.team_abr][side_of_ball]}
        while True:
            pct = random.random()
            games = None
            for pct_key in pcts:
                if pct <= pct_key:
                    games = self.histograms[team.team_abr][side_of_ball][pcts[pct_key]]['values']
                    break
            
            if len(games) == 0:
                continue
            else:
                break
        
        week = random.choice(games)
        score = team.stats[side_of_ball]['scoring'][week]['FP']
        return score



if __name__ == "__main__":
    version = "0.0"
    year = 2022
    start_time = time.time()
    team1 = Team("NE", 2007, version)
    team2 = Team("CLV", 2017, version)
    simulation = Simulation()
    simulation.best_of(team1, team2, 7_000_000)

    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")