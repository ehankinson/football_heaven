from db import DB
from get_stats import GetStats

VERSIONS = [0.0, 0.1, 1.0, 1.1, 2.0, 2.1, 3.0, 3.1, 4.0, 5.0]
OFFENSE = False
DEFENSE = True
VERSIONS = {
    "passing": "PASSING"
}



class Converter():

    def __init__(self) -> None:
        self.player_passing_keys = ["player_id", "game_id", "team_id", "type", "year", "league", "version", "week", "snaps", "db", "cmp", "aim", "att", "yds", "adot", "td", "int", "1d", "btt", "twp", "drp", "bat", "hat", "ta", "spk", "sk", "scrm", "pen", "grade_pass"]
        self.team_passing_keys = ["team_id", "game_id", "type", "year", "league", "version", "week", "snaps", "db", "cmp", "aim", "att", "yds", "adot", "td", "int", "1d", "btt", "twp", "drp", "bat", "hat", "ta", "spk", "sk", "scrm", "pen", "grade_pass"]
        self.passing_insert = ["player_id", "game_id", "team_id", "type", "year", "league", "version", "aim", "att", "adot", "bat", "btt", "cmp", "db", "drp", "1d", "hat", "int", "snaps", "pen", "sk", "scrm", "spk", "ta", "td", "twp", "yds", "grade_pass"]
        
        self.map = {
            True: {
                "passing": self.player_passing_keys,
            },
            False: {
                "passing": self.team_passing_keys,
            }
        }



    def convert_passing(self, results: tuple[tuple], is_player: bool, _type: str) -> list[dict]:
        final_results = []
        for result in results:
            result = dict(zip(self.map[is_player][_type], result))
            final_results.append(result)
        return final_results
    


    def convert_to_insert(self, result: dict, _type: str) -> list:
        match _type:
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
        self.passing_types = ["passing", "behind_los_central", "behind_los_left", "behind_los_right", "deep_center", "deep_left", "deep_right", "intermediate_central", "intermediate_left", "intermediate_right", "short_central", "short_left", "short_right", "no_pressure", "pressure", "blitz", "no_blitz"]
        self.passing_countables = ["snaps", "db", "cmp", "aim", "att", "yds", "adot", "td", "int", "1d", "btt", "twp", "drp", "bat", "hat", "ta", "spk", "sk", "scrm", "pen", "grade_pass"]



    
    def _find_game(self, game: int, stats: list) -> int:
        for i, game_stats in enumerate(stats):
            if game_stats["week"] == game:
                return i
        return -1



    def _convert_zero_one_pt(self, offense: list, defense: list, player_stats: list):
        new_player_stats = []

        for week_stats in player_stats:
            week = week_stats["week"]
            off_game = offense[self._find_game(week, offense)]
            def_game = defense[self._find_game(week, defense)]

            stats = {}
            for key in week_stats:
                if key in self.passing_countables:
                    break

                stats[key] = week_stats[key]

            stats["version"] = "0.1"
            del stats["week"]

            if off_game["db"] == 0:
                for key in self.passing_countables:
                    stats[key] = 0
                new_player_stats.append(stats)
                continue

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
                    stats[key] = round(pct * def_game[key] * def_game["att"], 0) if def_game[key] is not None else 0
                    continue
                
                pct = week_stats[key] / off_game[key] if off_game[key] != 0 else dp_pct
                result = pct * def_game[key]
                
                stats[key] = int(round(result, 0))
            new_player_stats.append(stats)
        
        return new_player_stats



    def _update_types(self, old_player_stats: list, new_player_stats: list, args: dict):
        final_stats = []
        checks = [0, 1, 2, 3, 4]
        for _type in self.passing_types:
            args["type"] = _type
            new_stats = self.stats.season_passing_game(True, args)
            for stat in new_stats:
                game_index = self._find_game_player_to_player(stat, old_player_stats, checks)
                old_stats = old_player_stats[game_index]
                new_stats = new_player_stats[game_index]
                final_stats.append(self._convert_zero_one_pp(list(old_stats), new_stats, list(stat), 5))



    def create_zero_one_version(self, is_player: bool, args: list):
        final_results = []
        for _type in self.passing_types:
            args["type"] = _type
            offense_stats = self.converter.convert_passing(self.stats.season_passing_game(is_player, args, side_of_ball=OFFENSE), is_player, "passing")
            defense_stats = self.converter.convert_passing(self.stats.season_passing_game(is_player, args, side_of_ball=DEFENSE), is_player, "passing")
            passing_stats = self.converter.convert_passing(self.stats.season_passing_game(not is_player, args), not is_player, "passing")

            new_player_stats = self._convert_zero_one_pt(offense_stats, defense_stats, passing_stats)

            final_results += new_player_stats
        return final_results



    def insert_into_db(self, results: list, _type: str):
        count = 0
        # amount = self.db.cache
        amount = 1

        for result in results:
            match _type:
                case "passing":
                    formatted_result = self.converter.convert_to_insert(result, _type)
                    self.db.quick_add_passing(formatted_result)
            
            count += 1
            if count % amount == 0:
                self.db.commit()

        self.db.commit()

            




if __name__ == "__main__":
    make_version = MakeVersion()
    is_player = False
    data = {
        "start_week": 1,
        "end_week": 18,
        "start_year": 2023,
        "end_year": 2023,
        "type": None,
        "league": "NFL",
        "version": "0.0",
        "position": None,
        "limit": None,
        "team": "CAR"
    }
    results = make_version.create_zero_one_version(is_player, data)
    make_version.insert_into_db(results, "passing")
    

        
