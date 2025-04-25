import time

from db import DB
from get_stats import GetStats

VERSIONS = ["0.1", "1.0", "1.1", "2.0", "2.1", "3.0", "3.1", "4.0", "5.0"]
STATS = ["passing"]
OFFENSE = False
DEFENSE = True
YEARS = {
    "NFL": {"start": 2006, "end": 2024},
    "NCAA": {"start": 2014, "end": 2024}
}



class Converter():

    def __init__(self) -> None:
        self.player_passing_keys = ["player_id", "game_id", "team_id", "type", "year", "league", "version", "week", "snaps", "db", "cmp", "aim", "att", "yds", "adot", "td", "int", "1d", "btt", "twp", "drp", "bat", "hat", "ta", "spk", "sk", "scrm", "pen", "grade_pass"]
        self.team_passing_keys = ["team_id", "game_id", "type", "year", "league", "version", "week", "snaps", "db", "cmp", "aim", "att", "yds", "adot", "td", "int", "1d", "btt", "twp", "drp", "bat", "hat", "ta", "spk", "sk", "scrm", "pen", "grade_pass"]
        self.passing_insert = ["player_id", "game_id", "team_id", "type", "year", "league", "version", "aim", "att", "adot", "bat", "btt", "cmp", "db", "drp", "1d", "hat", "int", "snaps", "pen", "sk", "scrm", "spk", "ta", "td", "twp", "yds", "grade_pass"]
        self.game_data = ["game_id", "version", "team_id", "year", "week", "opp_id", "pf", "pa", "diff", "td", "xpa", "xpm", "fga", "fgm", "2pa", "2pm", "sfty", "krtd", "prtd", "intd", "frtd", "opp_krtd", "opp_prtd", "opp_intd", "opp_frtd"]
        self.map = {
            True: {
                "passing": self.player_passing_keys,
            },
            False: {
                "passing": self.team_passing_keys,
                "game_data": self.game_data
            }
        }



    def convert_results(self, results: tuple[tuple], is_player: bool, stat: str) -> list[dict]:
        final_results = []
        for result in results:
            result = dict(zip(self.map[is_player][stat], result))
            final_results.append(result)
        return final_results
    


    def convert_to_insert(self, result: dict, stat: str) -> list:
        match stat:
            case "passing":
                keys = self.passing_insert

        new_result = []
        for key in keys:
            if key not in result:
                raise ValueError(f"Key {key} not found in result")
            new_result.append(result[key])

        return new_result


class MakeVersion():

    def __init__(self) -> None:
        self.db = DB()
        self.stats = GetStats(self.db)
        self.converter = Converter()
        self.passing_types = ["passing", "behind_los_central", "behind_los_left", "behind_los_right", "deep_central", "deep_left", "deep_right", "intermediate_central", "intermediate_left", "intermediate_right", "short_central", "short_left", "short_right", "no_pressure", "pressure", "blitz", "no_blitz"]
        self.passing_countables = {"snaps": min, "db": min, "cmp": max, "aim": min, "att": min, "yds": max, "adot": max, "td": max, "int": min, "1d": max, "btt": max, "twp": min, "drp": min, "bat": min, "hat": min, "ta": min, "spk": min, "sk": min, "scrm": min, "pen": min, "grade_pass": max}


    
    def _find_game(self, game: int, stats: list, year: int) -> int:
        for i, game_stats in enumerate(stats):
            if game_stats["week"] == game and game_stats["year"] == year:
                return i
        return -1



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



    def _convert_one_zero(self, offense: list, defense: list, player_stats: list, stat: str):
        dict_games = self.converter.convert_results(self.db.get_games(player_stats[0]["team_id"], "0.0"), False, "game_data")
        games = {}
        for game in dict_games:
            games[f"{game['year']}_{game['week']}"] = game

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
            
            stats["version"] = "1.0"
            del stats["week"]
            self._switch_stats(off_game, new_off_game, week_stats, stats)
            new_player_stats.append(stats)
        
        return new_player_stats



    def create_version(self, is_player: bool, args: list, stat: str, to_be_version: str):
        final_results = []
        for _type in self.passing_types:
            args["type"] = _type
            offense_stats = self.converter.convert_results(self.stats.season_passing_game(is_player, args, side_of_ball=OFFENSE), is_player, stat)
            defense_stats = self.converter.convert_results(self.stats.season_passing_game(is_player, args, side_of_ball=DEFENSE), is_player, stat)
            passing_stats = self.converter.convert_results(self.stats.season_passing_game(not is_player, args), not is_player, stat)

            new_player_stats = None
            match to_be_version:
                case "0.1":
                    new_player_stats = self._convert_zero_one(offense_stats, defense_stats, passing_stats)
                case "1.0":
                    new_player_stats = self._convert_one_zero(offense_stats, defense_stats, passing_stats, stat)

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
            if version not in ["0.1", "1.0"]:
                break

            teams = self.db.get_teams(league)
            for team in teams:
                data = {
                    "start_week": 1,
                    "end_week": 18 if version == "0.1" else 32,
                    "start_year": YEARS[league]["start"],
                    "end_year": YEARS[league]["end"],
                    "type": None,
                    "league": league,
                    "version": '0.0',
                    "position": None,
                    "limit": None,
                    "team": team
                }

                for stat in STATS:
                    print(f"Converting {stat} for {team} in {league} version {version}")
                    results = self.create_version(is_player, data, stat, version)
                    self.insert_into_db(results, stat)
                    
        end_time = time.time()
        print(f"Time taken: {end_time - start_time} seconds")

            




if __name__ == "__main__":
    make_version = MakeVersion()
    make_version.convert_stats("NFL", False)
    

        
