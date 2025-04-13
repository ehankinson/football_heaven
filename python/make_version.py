from db import DB
from get_stats import GetStats

VERSIONS = [0.0, 0.1, 1.0, 1.1, 2.0, 2.1, 3.0, 3.1, 4.0, 5.0]
OFFENSE = False
DEFENSE = True

class MakeVersion():

    def __init__(self, db: DB) -> None:
        self.db = db
        self.stats = GetStats(db)


    def create_version(self, version: str):
        pass


    def _find_game(self,game: int, stats: list) -> int:
        for i, game_stats in enumerate(stats):
            if game_stats[3] == game:
                return i
        return -1



    def _convert_zero_one(self,offense: list, defense: list, player_stats: list):
        new_player_stats = []

        for week_stats in player_stats:
            week_stats = list(week_stats)
            stats = week_stats[0:5]

            off_game = offense[self._find_game(stats[-1], offense)]
            def_game = defense[self._find_game(stats[-1], defense)]

            dp_pct = week_stats[6] / off_game[5]

            for team_index, player_index in zip(range(4, 23), range(5, 25)):
                pct = week_stats[player_index] / off_game[team_index] if off_game[team_index] != 0 else dp_pct
                result = pct * def_game[team_index]
                
                stats.append(int(round(result, 0)))

            new_player_stats.append(stats)
        
        return new_player_stats



    def create_zero_one_version(self, is_player: bool, args: list):
        offense_stats = self.stats.season_passing_game(is_player, args, side_of_ball=OFFENSE)
        defense_stats = self.stats.season_passing_game(is_player, args, side_of_ball=DEFENSE)
        passing_stats = self.stats.season_passing_game(not is_player, args)

        new_player_stats = self._convert_zero_one(offense_stats, defense_stats, passing_stats)
        for stat in new_player_stats:
            print(stat)
        return new_player_stats

            




if __name__ == "__main__":
    db = DB()
    make_version = MakeVersion(db)
    is_player = False
    data = [1, 32, 2024, 2024, "passing", "NFL", None, None, "NE"]
    make_version.create_zero_one_version(is_player, data)
