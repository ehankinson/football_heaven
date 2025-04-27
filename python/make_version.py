import json
import time

from db import DB
from get_stats import GetStats
from converter import Converter

TEAM = False
PLAYER = True
OFFENSE = False
DEFENSE = True
STATS = ["passing"]
VERSIONS = ["0.1", "1.0", "1.1", "2.0", "2.1", "3.0", "3.1", "4.0", "5.0"]
YEARS = {
    "NFL": {"start": 2006, "end": 2024},
    "NCAA": {"start": 2014, "end": 2024}
}



class MakeVersion():

    def __init__(self) -> None:
        self.db = DB()
        self.stats = GetStats(self.db)
        self.converter = Converter()
        self.passing_types = ["passing", "behind_los_central", "behind_los_left", "behind_los_right", "deep_central", "deep_left", "deep_right", "intermediate_central", "intermediate_left", "intermediate_right", "short_central", "short_left", "short_right", "no_pressure", "pressure", "blitz", "no_blitz"]
        self.passing_countables = {"snaps": min, "db": min, "cmp": max, "aim": min, "att": min, "yds": max, "adot": max, "td": max, "int": min, "1d": max, "btt": max, "twp": min, "drp": min, "bat": min, "hat": min, "ta": min, "spk": min, "sk": min, "scrm": min, "pen": min, "grade_pass": max}
        
        with open("json/ranks0.0.json", "r") as f:
            self.ranks00 = json.load(f)


    
    def _find_game(self, game: int, stats: list, year: int) -> int:
        for i, game_stats in enumerate(stats):
            if game_stats["week"] == game and game_stats["year"] == year:
                return i
        return -1



    def _get_games(self, player_stats: dict):
        dict_games = self.converter.convert_results(self.db.get_games(player_stats["team_id"], "0.0"), False, "game_data")
        games = {}
        for game in dict_games:
            games[f"{game['year']}_{game['week']}"] = game
        return games



    def _get_stats_zero_one(self, year: int, args: dict, stat: str):
        team = args["team"]

        year_stats = self.ranks00[str(year)]
        team_name = self.db.call_query(f"SELECT Team_Name FROM TEAMS WHERE Team_Abbr = '{team}'")[0][0]
        
        key = "AFC" if team_name in year_stats["AFC"] else "NFC"
        opp_team = list(year_stats[key].keys())[16 - year_stats[key][team_name]]
        opp_team_abr = self.db.call_query(f"SELECT Team_Abbr FROM TEAMS WHERE Team_Name = '{opp_team}'")[0][0]

        # getting regular season stats for the team
        offense_stats = self.converter.convert_results(self.stats.season_passing_game(TEAM, args, side_of_ball=OFFENSE), TEAM, stat)
        defense_stats = self.converter.convert_results(self.stats.season_passing_game(TEAM, args, side_of_ball=DEFENSE), TEAM, stat)
        passing_stats = self.converter.convert_results(self.stats.season_passing_game(PLAYER, args), PLAYER, stat)

        # updating the args to get the inverse team stats in the playoffs
        args["start_week"], args["end_week"], args["team"] = 29, 32, opp_team_abr
        playoff_off = self.converter.convert_results(self.stats.season_passing_game(TEAM, args, side_of_ball=OFFENSE), TEAM, stat)
        playoff_def = self.converter.convert_results(self.stats.season_passing_game(TEAM, args, side_of_ball=DEFENSE), TEAM, stat)

        offense_stats += playoff_off
        defense_stats += playoff_def

        args["start_week"], args["end_week"], args["team"] = 18 - len(playoff_off) + 1, 18, team
        reuse_player = self.converter.convert_results(self.stats.season_passing_game(PLAYER, args), PLAYER, stat)

        passing_stats += reuse_player

        return offense_stats, defense_stats, passing_stats


    
    def _get_stats(self, year: int, version: str, args: dict, stat: str):
        offense_stats, defense_stats, player_stats = None, None, None
        match version:
            case "0.1":
                offense_stats, defense_stats, player_stats = self._get_stats_zero_one(year, args, stat)

        return offense_stats, defense_stats, player_stats



    def _alter_games(self, offense: list, defense: list, best: bool, stat: str):
        countables = None
        match stat:
            case "passing":
                countables = self.passing_countables
        
        new_offense = {}
        new_defense = {}
        for key in countables:
            function = countables[key]
            offense[key] = 0 if offense[key] is None else offense[key]
            defense[key] = 0 if defense[key] is None else defense[key]
            
            if key == "adot":
                offense[key] = int(round(offense[key] * offense["att"], 0))
                defense[key] = int(round(defense[key] * defense["att"], 0))

            if best:
                new_offense[key] = function(offense[key], defense[key])
                new_defense[key] = (offense[key] + defense[key]) - new_offense[key]
            else:
                new_defense[key] = function(offense[key], defense[key])
                new_offense[key] = (offense[key] + defense[key]) - new_defense[key]
        
        if stat == "passing":
            # we need to make sure that the min attempts are still larger than cmp + int
            better = new_offense if best else new_defense
            worse = new_defense if best else new_offense
            keys_to_check = ["aim", "att", "db", "snaps"]
            check = better["cmp"] + better["int"]
            switch = False
            for key in keys_to_check:
                if not switch and better[key] < check:
                    switch = True

                if switch:
                    temp = better[key]
                    better[key] = worse[key]
                    worse[key] = temp

        return new_offense, new_defense
    


    def _switch_stats(self, off_game: list, def_game: list, week_stats: list, stats: dict) -> None:
        if off_game["db"] == 0:
            for key in self.passing_countables:
                stats[key] = 0
            return

        dp_pct = week_stats["db"] / off_game["db"]

        for key in self.passing_countables:
            if key == "grade_pass":
                stats[key] = round(dp_pct * def_game[key] if def_game[key] is not None else 0, 1)
                continue

            if key == "adot":
                if week_stats[key] is None or off_game[key] is None or stats["att"] == 0:
                    stats[key] = 0
                    continue

                pct = (week_stats[key] * week_stats["att"]) / (off_game[key] * off_game["att"]) if off_game[key] != 0 else dp_pct
                stats[key] = int(round(pct * def_game[key] * def_game["att"], 0)) if def_game[key] is not None else 0
                continue
            
            pct = week_stats[key] / off_game[key] if off_game[key] != 0 else dp_pct
            result = pct * def_game[key]
            
            stats[key] = int(round(result, 0))
        
        return



    def _convert_zero_one(self, offense: list, defense: list, player_stats: list):
        new_player_stats = []

        for week_stats in player_stats:
            week = week_stats["week"]
            off_game = offense[self._find_game(week, offense, week_stats["year"])]
            def_game = defense[self._find_game(week, defense, week_stats["year"])]

            stats = {}
            for key in week_stats:
                if key in self.passing_countables:
                    break

                stats[key] = week_stats[key]

            stats["version"] = "0.1"
            del stats["week"]
            stats["game_id"] = self.db.get_game_id(week_stats["year"], week_stats["week"], week_stats["team_id"], stats["version"])

            self._switch_stats(off_game, def_game, week_stats, stats)
            new_player_stats.append(stats)
        
        return new_player_stats



    def _convert_one_zero(self, version: str, offense: list, defense: list, player_stats: list, stat: str):
        games = self._get_games(player_stats[0])

        best = None
        new_player_stats = []
        for week_stats in player_stats:
            week = week_stats["week"]
            off_game = offense[self._find_game(week, offense, week_stats["year"])]
            def_game = defense[self._find_game(week, defense, week_stats["year"])]
            game = games[f"{week_stats['year']}_{week}"]
            
            best = None if game["diff"] == 0 else True if game["diff"] > 0 else False

            new_off_game, new_def_game = self._alter_games(off_game, def_game, best, stat)
            stats = {}
            for key in week_stats:
                if key in self.passing_countables:
                    break

                stats[key] = week_stats[key]
            
            stats["version"] = version
            del stats["week"]
            if version.endswith(".1"):
                self._switch_stats(off_game, new_def_game, week_stats, stats)
            else:
                self._switch_stats(off_game, new_off_game, week_stats, stats)

            new_player_stats.append(stats)
        
        return new_player_stats



    def create_version(self, args: list, stat: str, to_be_version: str):
        final_results = []
        for _type in self.passing_types:
            for year in range(args["start_year"], args["end_year"] + 1):
                args["type"] = _type
                offense_stats, defense_stats, passing_stats = self._get_stats(year, to_be_version, args, stat)

            new_player_stats = None
            if to_be_version.startswith("0"):
                new_player_stats = self._convert_zero_one(offense_stats, defense_stats, passing_stats)
            elif to_be_version.startswith("1"):
                new_player_stats = self._convert_one_zero(to_be_version, offense_stats, defense_stats, passing_stats, stat)

            final_results += new_player_stats
        return final_results



    def insert_into_db(self, results: list, stat: str):
        count = 0
        amount = self.db.cache

        for result in results:
            match stat:
                case "passing":
                    formatted_result = self.converter.convert_to_insert(result, stat)
                    self.db.quick_add_passing(formatted_result)
            
            count += 1
            if count % amount == 0:
                self.db.commit()

        self.db.commit()



    def convert_stats(self, league: str, is_player: bool) -> None:
        start_time = time.time()
        for version in VERSIONS:
            if version not in ["0.1", "1.0", "1.1"]:
                break

            teams = self.db.get_teams(league)
            teams = ["CAR"]
            for team in teams:
                data = {
                    "start_week": 1,
                    "end_week": 18 if version.endswith(".1") else 32,
                    "start_year": 2023, #YEARS[league]["start"],
                    "end_year": 2023, #YEARS[league]["end"],
                    "type": None,
                    "league": league,
                    "version": '0.0',
                    "position": None,
                    "limit": None,
                    "team": team
                }

                for stat in STATS:
                    print(f"Converting {stat} for {team} in {league} version {version}")
                    results = self.create_version(data, stat, version)
                    self.insert_into_db(results, stat)
                    
        end_time = time.time()
        print(f"Time taken: {end_time - start_time} seconds")

            




if __name__ == "__main__":
    make_version = MakeVersion()
    make_version.convert_stats("NFL", False)
    

        
