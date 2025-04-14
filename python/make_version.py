from db import DB
from get_stats import GetStats

VERSIONS = [0.0, 0.1, 1.0, 1.1, 2.0, 2.1, 3.0, 3.1, 4.0, 5.0]
OFFENSE = False
DEFENSE = True

class MakeVersion():

    def __init__(self, db: DB) -> None:
        self.db = db
        self.stats = GetStats(db)
        self.passing_types = ["passing", "behind_los_central", "behind_los_left", "behind_los_right", "deep_center", "deep_left", "deep_right", "intermediate_central", "intermediate_left", "intermediate_right", "short_central", "short_left", "short_right", "no_pressure", "pressure", "blitz", "no_blitz"]



    def _find_game(self,game: int, stats: list) -> int:
        for i, game_stats in enumerate(stats):
            if game_stats[3] == game:
                return i
        return -1



    def _convert_zero_one_pt(self, offense: list, defense: list, player_stats: list):
        new_player_stats = []

        for week_stats in player_stats:
            week_stats = list(week_stats)
            stats = week_stats[0:5]

            off_game = offense[self._find_game(stats[-1], offense)]
            def_game = defense[self._find_game(stats[-1], defense)]

            if off_game[5] == 0:
                new_player_stats.append(stats + [0] * 20)
                continue
            
            dp_pct = week_stats[6] / off_game[5]

            for team_index, player_index in zip(range(4, 23), range(5, 25)):
                pct = week_stats[player_index] / off_game[team_index] if off_game[team_index] != 0 else dp_pct
                result = pct * def_game[team_index]
                
                stats.append(int(round(result, 0)))
            
            grade = dp_pct * def_game[team_index + 1] if def_game[team_index + 1] is not None else 0
            stats.append(round(grade, 1))
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
            offense_stats = self.stats.season_passing_game(is_player, args, side_of_ball=OFFENSE)
            defense_stats = self.stats.season_passing_game(is_player, args, side_of_ball=DEFENSE)
            passing_stats = self.stats.season_passing_game(not is_player, args)

            new_player_stats = self._convert_zero_one_pt(offense_stats, defense_stats, passing_stats)
            [val.insert(4, _type) for val in new_player_stats]
            final_results += new_player_stats
        
        for result in final_results:
            print(result)

        return final_results

            




if __name__ == "__main__":
    db = DB()
    make_version = MakeVersion(db)
    is_player = False
    data = {
        "start_week": 1,
        "end_week": 1,
        "start_year": 2006,
        "end_year": 2006,
        "type": None,
        "league": "NFL",
        "position": None,
        "limit": None,
        "team": "CAR"
    }
    make_version.create_zero_one_version(is_player, data)
