
import math
import random

from typing import Any
from dataclasses import dataclass, field

from bracket import Bracket
from const import STAT_TYPES
from get_stats import GetStats
from converter import Converter

ALL = False
TEAM = False
PRINT = True
SINGLE = True
OFFENSE = True
STARTUP = True
DEFENSE = False
PER_GAME = True
STATS = {"passing": True, "rushing": True, "receiving": True, "pass_blocking" : True, "run_blocking" : True, "pass_rush" : False, "run_defense" : False, "coverage" : False}

@dataclass(slots=True)
class Bin:
    """Represents a single bin in a histogram.
    
    Attributes:
        values: List of float values that fall into this bin
        pct: Cumulative percentage up to and including this bin
    """
    values: list[float] = field(default_factory=list)
    pct: float = 0.0



@dataclass(frozen=True, slots=True)
class Histogram:
    """Represents a histogram of values with bins and percentage mappings.
    
    Attributes:
        bins: Dictionary mapping bin start values (float keys) to Bin objects
        pct_to_bin: Dictionary mapping cumulative percentages to bin start values,
                    used for random sampling based on probability distribution
    """
    bins: dict[float, Bin]
    pct_to_bin: dict[float, float]



@dataclass(slots=True)
class Team:
    """Represents a football team with its statistics and metadata.
    
    Automatically fetches offense and defense stats upon initialization.
    
    Attributes:
        team_abr: Team abbreviation (e.g., 'CAR', 'ATL')
        year: Season year
        version: Version identifier for the data
        get_stats: GetStats instance for fetching statistics
        converter: Converter instance for data conversion
        stats: Dictionary containing 'offense' and 'defense' statistics
        team_key: Unique identifier combining team_abr, year, and version
    """
    team_abr: str
    year: int
    version: str
    get_stats: GetStats = field(default_factory=GetStats, repr=False)
    converter: Converter = field(default_factory=Converter, repr=False)
    stats: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {"offense": {}, "defense": {}}, repr=False
    )
    team_key: str = field(init=False)

    def __post_init__(self) -> None:
        self.team_key = f"{self.team_abr}_{self.year}_{self.version}"
        self._get_stats()


    def __repr__(self):
        return self.team_key



    def _get_stats(self):
        args = {
            "start_week": None,
            "end_week": None,
            "start_year": self.year,
            "end_year": self.year,
            "stat_type": None,
            "league": 'NFL',
            "version": self.version,
            "pos": None,
            "limit": None,
            "team": self.team_abr
        }
        self.stats['offense'] = self.get_stats.get_total_stats(args, OFFENSE)
        self.stats['defense'] = self.get_stats.get_total_stats(args, DEFENSE)
        self.stats['offense']['FP'] = {}
        self.stats['defense']['FP'] = {}

        off_scoring = self.stats["offense"]["scoring"]
        def_scoring = self.stats["defense"]["scoring"]
        for week, off_stats in off_scoring.items():
            # Keep only weeks that exist for both sides.
            if week not in def_scoring:
                continue
            self.stats["offense"]["FP"][off_stats["FP"]] = week
            self.stats["defense"]["FP"][def_scoring[week]["FP"]] = week


class Stats:
    """Utility class for creating histograms from team or league statistics.
    
    Provides methods to bin values, find appropriate bins, and generate
    histograms for simulation purposes.
    """



    def bin_values(self, values: list[float]) -> dict[float, Bin]:
        """Create bins for histogram by dividing the value range into equal-width intervals.
        
        The number of bins is determined by the square root of the number of values.
        Each bin is initialized with an empty values list and a percentage of 0.
        
        Args:
            values: List of float values to bin
            
        Returns:
            Dictionary mapping bin start values (float keys) to Bin objects.
        """
        if not values:
            raise ValueError("values must not be empty")

        # finding the min and max values of the list
        min_val, max_val = float('inf'), float('-inf')
        for val in values:
            min_val = min(min_val, val)
            max_val = max(max_val, val)

        # calculating the range of the list
        range_val = max_val - min_val
        # finding out the number of bins in the list
        amount_bins = math.ceil(math.sqrt(len(values)))

        # calculating the bin width
        bins: dict[float, Bin] = {}
        add = min_val
        bin_width = range_val / amount_bins
        for _ in range(amount_bins):
            bins[add] = Bin()
            add += bin_width
        return bins



    def find_bin(self, score: float, bins: list[float]) -> float | None:
        """Return the bin key a score falls into.

        Args:
            score: Value to place into a bin.
            bins: Sorted list of bin keys (bin upper boundaries / start keys used here).

        Returns:
            The selected bin key, or None if no bin matches.
        """
        if score >= bins[-1]:
            return bins[-1]

        for key in bins:
            if score <= key:
                return key

        return None



    def get_histogram(
        self,
        team: Team,
        side_of_ball: str,
        single: bool = True,
        stats: dict | None = None
    ) -> Histogram:
        """Generate a histogram of values by binning data and calculating cumulative percentages.
        
        Args:
            team: Team object to get values from
            side_of_ball: 'offense' or 'defense' side of the ball
            single: If True, use single team stats; if False, use league-wide stats
            stats: Dictionary of stats to use when single=False
            
        Returns:
            tuple: (bins dict, pct_dict) where bins contains bin data with values and percentages,
                   and pct_dict maps cumulative percentages to bin keys
        """
        values = self._get_values(single=single, team=team, side_of_ball=side_of_ball, stats=stats)
        bins: dict[float, Bin] = self.bin_values(values)

        for val in values:
            bin_key = self.find_bin(val, list(bins.keys()))
            if bin_key is None:
                continue
            bins[bin_key].values.append(val)

        del_keys = []
        pct_to_bin: dict[float, float] = {}
        total_pct = 0.0
        for bin_key, bin_data in bins.items():
            if len(bin_data.values) == 0:
                del_keys.append(bin_key)
                continue

            pct = len(bin_data.values) / len(values)
            bin_data.pct = pct + total_pct
            pct_to_bin[pct + total_pct] = bin_key
            total_pct += pct

        for bin_key in del_keys:
            del bins[bin_key]

        return Histogram(bins=bins, pct_to_bin=pct_to_bin)



    def _get_values(
        self,
        single: bool = True,
        team: Team | None = None,
        side_of_ball: str | None = None,
        stats: dict | None = None,
    ) -> list[float]:
        """Return the scoring FP values used to build a histogram.

        When `single=True`, values are pulled from `team.stats[side_of_ball]`.
        When `single=False`, values are aggregated across all teams in `stats`.
        """
        if single:
            if team is None:
                raise ValueError("team must be provided when single=True")
            if side_of_ball is None:
                raise ValueError("side_of_ball must be provided when single=True")

            scoring = team.stats[side_of_ball]["scoring"]
            return [scoring[week]["FP"] for week in scoring]

        if stats is None:
            raise ValueError("stats must be provided when single=False")

        results: list[float] = []
        for team_stats in stats.values():
            scoring = team_stats["scoring"]
            for week in scoring:
                results.append(scoring[week]["FP"])

        return results



class Simulation:
    """Main simulation engine for running football game and tournament simulations.
    
    Manages team statistics, histograms, and game outcomes. Supports both
    team-only simulations (fast) and league-aware simulations (more detailed).
    
    Attributes:
        teams: Set of team keys that have been initialized
        stats: Stats instance for histogram generation
        histograms: Dictionary mapping team keys to their histograms
        team_stats: Dictionary tracking wins, losses, ties, and scores per team
        league_histograms: Dictionary mapping years to league-wide histograms
        get_stats: GetStats instance for fetching statistics
    """

    def __init__(self):
        self.stats = Stats()
        self.histograms = {}
        self.team_stats = {}
        self.teams = set()
        self.league_histograms = {}
        self.get_stats = GetStats()



    def sim_game(
        self,
        team1: Team,
        team2: Team,
        startup: bool = True,
        print_score: bool = True,
        league_sim: bool = False,
    ) -> int | None:
        """Simulate a single game between two teams.

        Optionally performs startup initialization (histograms, and league histogram
        when `league_sim=True`), simulates a matchup, and updates win/loss/tie counts.

        Args:
            team1: First team
            team2: Second team
            startup: If True, initialize required histograms before simulating
            print_score: Reserved for future detailed score printing (currently unused)
            league_sim: If True, use league-aware simulation path; otherwise team-only

        Returns:
            1 if team1 wins, -1 if team2 wins, 0 for a tie.
        """
        if startup:
            self._sim_startup(team1, league_sim=league_sim)
            self._sim_startup(team2, league_sim=league_sim)

        winner = self._league_sim(team1, team2) if league_sim else self._team_sim(team1, team2)

        if winner == 1:
            self.team_stats[team1.team_key]['score']['wins'] += 1
            self.team_stats[team2.team_key]['score']['losses'] += 1
        elif winner == -1:
            self.team_stats[team2.team_key]['score']['wins'] += 1
            self.team_stats[team1.team_key]['score']['losses'] += 1
        else:
            self.team_stats[team1.team_key]['score']['ties'] += 1
            self.team_stats[team2.team_key]['score']['ties'] += 1

        return winner



    def best_of(
        self,
        team1: Team,
        team2: Team,
        series_length: int,
        print_result: bool = True,
        league_sim: bool = False,
    ) -> int | None:
        """Simulate a best-of series between two teams.
        
        Plays games until one team reaches the required number of wins
        (series_length // 2 + 1). Tracks wins for each team and optionally
        prints the final result.
        
        Args:
            team1: First team in the series
            team2: Second team in the series
            series_length: Total number of games in the series (e.g., 7 for best-of-7)
            print_result: If True, print the series result
            league_sim: If True, use league-aware simulation; if False, use team-only
            
        Returns:
            1 if team1 wins the series, -1 if team2 wins the series
        """
        self._sim_startup(team1, league_sim=league_sim)
        self._sim_startup(team2, league_sim=league_sim)

        first_to = series_length // 2 + 1
        wins = {'t1': 0, 't2': 0}
        while wins['t1'] < first_to and wins['t2'] < first_to:
            score = self.sim_game(
                team1,
                team2,
                startup=False,
                print_score=False,
                league_sim=league_sim
            )
            if score == 1:
                wins['t1'] += 1
            elif score == -1:
                wins['t2'] += 1

        if print_result:
            self._print_results(team1, team2, wins)

        return 1 if wins['t1'] > wins['t2'] else -1



    def sim_bracket(self, teams: list[Team], series_length: int) -> Team:
        """Simulate a playoff bracket tournament.
        
        Creates a bracket from the given teams and simulates each match as a best-of
        series. Tracks winners and losers through each round and updates team statistics
        with the best round reached.
        
        Args:
            teams: List of Team objects to participate in the tournament
            series_length: Number of games in each best-of series
            
        Returns:
            The winning team from the final round
        """
        bracket = Bracket(teams)
        playoff_bracket = bracket.generate_bracket()

        losers = []
        winners = []
        for i, rd in enumerate(playoff_bracket):
            round_id = len(playoff_bracket) - i
            for match in rd:
                team1, team2 = match
                print(f"Simulating {team1[1].team_key} vs {team2[1].team_key} in round {round_id}")
                result = self.best_of(team1[1], team2[1], series_length, print_result=False)

                winner, loser = (team1, team2) if result == 1 else (team2, team1)

                print(f"Winner: {winner[1].team_key} - {result} - Loser: {loser[1].team_key}\n")
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



    def _league_sim(self, team1: Team, team2: Team) -> int:
        """League simulation path.

        Note: The league-level simulation model isn't implemented yet; for now this
        delegates to the team-only simulation so `league_sim=True` remains safe.
        """
        self._sim_startup(team1, league_sim=True)
        self._sim_startup(team2, league_sim=True)
        return self._team_sim(team1, team2)



    def _team_sim(self, team1: Team, team2: Team) -> int:
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

        self.team_stats[team1.team_key]['offense']['score'] += team1_final_score
        self.team_stats[team2.team_key]['offense']['score'] += team2_final_score
        self.team_stats[team1.team_key]['defense']['score'] += team2_final_score
        self.team_stats[team2.team_key]['defense']['score'] += team1_final_score

        return winner



    def _get_games(self, team: Team) -> tuple[dict, dict]:
        offense_week = self._get_week(team, 'offense')
        defense_week = self._get_week(team, 'defense')
        off_stats, def_stats = {}, {}
        for stat_type in STAT_TYPES:
            off_stats[stat_type] = team.stats['offense'][stat_type][offense_week]
            def_stats[stat_type] = team.stats['defense'][stat_type][defense_week]

        return off_stats, def_stats



    def _print_results(self, team1: Team, team2: Team, result: dict[str, int]) -> None:
        if result['t1'] > result['t2']:
            winner, win_key = team1, 't1'
            loser, loser_key = team2, 't2'
        else:
            winner, win_key = team2, 't2'
            loser, loser_key = team1, 't1'
        print(
            f"Winner: {winner.team_key} - {result[win_key]} - "
            f"{loser.team_key} - {result[loser_key]}"
        )



    def _sim_startup(self, team: Team, league_sim: bool = False) -> None:
        if team.team_key not in self.teams:
            self.teams.add(team.team_key)
            self._create_histogram(team)
            if league_sim:
                self._create_league_histogram(team)



    def _create_histogram(self, team: Team):
        team_key = team.team_key
        self.histograms[team_key] = {}
        for side_of_ball in ['offense', 'defense']:
            histogram = self.stats.get_histogram(team, side_of_ball, SINGLE, None)
            self.histograms[team_key][side_of_ball] = histogram

        self.team_stats[team_key] = {
            'score': {
                'wins': 0,
                'losses': 0,
                'ties': 0,
                'best_round': None
            },
            'offense': {'score': 0},
            'defense': {'score': 0}
        }



    def _create_league_histogram(self, team: Team):
        if team.year not in self.league_histograms:
            args = {
                "start_week": None,
                "end_week": None,
                "start_year": team.year,
                "end_year": team.year,
                "stat_type": None,
                "league": 'NFL',
                "version": team.version,
                "pos": None,
                "limit": None,
                "team": None
            }
            stats = self.get_stats.get_total_stats(args, OFFENSE)
            histogram = self.stats.get_histogram(team, 'offense', ALL, stats)
            self.league_histograms[team.year] = histogram



    def _get_week(self, team: Team, side_of_ball: str) -> int:
        pct = random.random()
        candidate_weeks = None
        team_key = team.team_key
        histogram: Histogram = self.histograms[team_key][side_of_ball]
        pcts = histogram.pct_to_bin
        for pct_key in pcts:
            if pct <= pct_key:
                bin_key = pcts[pct_key]
                bin_values = histogram.bins[bin_key]
                candidate_weeks = bin_values.values
                break

        if candidate_weeks is None:
            raise ValueError(f"No games found for {team_key} {side_of_ball}")

        fp_week = random.choice(candidate_weeks)
        week = team.stats[side_of_ball]['FP'][fp_week]
        return week



    def _get_game(self, team: Team, side_of_ball: str) -> int:
        week = self._get_week(team, side_of_ball)
        key = 'pts_for' if side_of_ball == 'offense' else 'pts_against'
        score = team.stats[side_of_ball]['game_data'][week][key]
        return score
