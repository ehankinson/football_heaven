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