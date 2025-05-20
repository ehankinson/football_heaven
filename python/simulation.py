from get_stats import GetStats
from converter import Converter
from collections import Counter


TEAM = False
OFFENSE = True
DEFENSE = False
PER_GAME = True
STATS = {"passing": True, "rushing": True, "receiving": True, "pass_blocking" : True, "run_blocking" : True, "pass_rush" : False, "run_defense" : False, "coverage" : False}


class Team():

    def __init__(self, team_abr: str, year: int, version: str):
        self.team_abr = team_abr
        self.year = year
        self.version = version
        self.db = GetStats()
        self.converter = Converter()
        self.stats = {'offense': {}, 'defense': {}}
        self._get_stats()
    


    def _get_stats(self):
        args = {"start_week": None, "end_week": None, "start_year": self.year, "end_year": self.year, "stat_type": None, "league": 'NFL', "version": self.version, "pos": None, "limit": None, "team": self.team_abr}
        for stat in STATS:
            args["stat_type"] = stat
            off_results = self.db.season_stats(args, stat, TEAM, by_game=PER_GAME)
            off_results = self.converter.convert_results(off_results, TEAM, stat)

            def_results = self.db.season_stats(args, stat, TEAM, opp=True, by_game=PER_GAME)
            def_results = self.converter.convert_results(def_results, TEAM, stat)
            
            assert len(off_results) == len(def_results), f"Offense and defense stats for {stat} are different lengths"
            assert off_results != def_results, f"Offense and defense stats for {stat} are the same"

            self.stats['offense'][stat] = off_results
            self.stats['defense'][stat] = def_results
        
        # orginizing the stats so we have a full offense and defense for each week
        # offense_stats = {'scoring': {}}
        # for stat in self.stats['offense']:
        #     stat_key = 'offense' if STATS[stat] else 'defense'
        #     offense_stats[stat] = {}
        #     for week in self.stats[stat_key][stat]:
        #         offense_stats[stat][week] = {}
        #         offense_stats[stat][week] = self.stats[stat_key][stat][week]
        #         if week not in offense_stats['scoring']:
        #             offense_stats['scoring'][week] = {}
        #         for key, value in self.stats[stat_key][stat][week].items():
        #             if key.isupper():
        #                 if key not in offense_stats['scoring'][week]:
        #                     offense_stats['scoring'][week][key] = 0
        #                 if value is None:
        #                     value = 0
        #                 add_value = -1 * value if key == 'FP' and not STATS[stat] else value
        #                 offense_stats['scoring'][week][key] += add_value
                    
        # self._calcuate_team_sprs(offense_stats)
    

    def _calcuate_team_sprs(self, team_stats: dict) -> None:
        for week in team_stats['scoring']:
            sc = team_stats['scoring'][week]
            passing = sc['PASS'] * 0.35 + sc['RECV'] * 0.25 + sc['ROUTE'] * 0.11 + sc['PASS_BLOCK'] * 0.24 + sc['T_PASS_BLOCK'] * 0.05
            running = sc['RUN'] * 0.3 + sc['FUM'] * 0.1 + sc['RUN_BLOCK'] * 0.5 + sc['GAP_GRADES'] * 0.05 + sc['ZONE_GRADES'] * 0.05
            presure = sc['RUSH'] * 0.85 + sc['T_RUSH'] * 0.15
            cov = sc['COV']
            run_def = sc['RUN_DEF'] * 0.8 + sc['TACK'] * 0.2

            offense = passing * 0.6 + running * 0.4
            defense = cov * 0.35 + run_def * 0.2 + presure * 0.45
            team_ovr = (offense * 0.55 + (100 - defense) * 0.45)

            sc['SPRS'] = team_ovr * 0.7 + sc['FP'] * 0.3



class Simulation:

    def __init__(self):
        self.histograms = {}
        pass



    def sim_game(self, team1: Team, team2: Team):
        self.team1 = team1
        self.team2 = team2
        self._create_histogram(self.team1)
        self._create_histogram(self.team2)
        pass



    def _create_histogram(self, team: Team):
        stats = {}
        for side_of_ball in team.stats:
            stats[side_of_ball] = {}
            for stat in team.stats[side_of_ball]:
                stats[side_of_ball][stat] = {}
                data_list = []
                for week in team.stats[side_of_ball][stat]:
                    data_list.append(list(team.stats[side_of_ball][stat][week].values()))
                last_values = [item[-1] for item in data_list]
                bins = self._bin_math(last_values)
    


    def _bin_math(self, values: list[int]) -> list[int]:
        # finding the min and max values of the list
        min_val, max_val = float('inf'), float('-inf')
        for val in values:
            min_val = min(min_val, val)
            max_val = max(max_val, val)
        # calculating the range of the list
        range_val = max_val - min_val
        # finding out the number of bins in the list
        bins = round(len(values) ** 0.5)
        # calculating the bin width
        bin_width = range_val / bins
        bins = []
        add = min_val
        for _ in range(bins):
            bins.append(add)
            add += bin_width
        return bins
        



if __name__ == "__main__":
    version = "0.0"
    team1 = Team("KC", 2024, version)
    team2 = Team("PHI", 2024, version)
    simulation = Simulation()
    simulation.sim_game(team1, team2)