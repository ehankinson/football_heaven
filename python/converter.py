class Converter():

    def __init__(self) -> None:
        self.player_start_header = ["Player", "Year", "VERSION", "TEAM", "POS", "GP"]
        self.team_start_header = ["team", "year", "version", "week", "gp"]
        self.headers = {
            'passing': ['snaps', 'db', 'cmp', 'aim', 'att', 'yds', 'adot', 'td', 'int', '1d', 'btt', 'twp', 'drp', 'bat', 'hat', 'ta', 'spk', 'sk', 'scrm', 'pen', 'PASS', 'FP', 'SPRS'],
            'receiving': ['snaps', 'wide', 'slot', 'in', 'rts', 'tgt', 'rec', 'yds', 'td', 'int', '1d', 'drp', 'ybc', 'yac', 'at', 'fum', 'ct', 'cr', 'pen', 'RECV', 'ROUTE', 'FP', 'SPRS'],
            'rushing': ['snaps', 'att', 'yds', 'td', 'fum', '1d', 'avd', 'exp', 'ybc', 'yac', 'b_att', 'b_yds', 'des_yds', 'gap_att', 'zone_att', 'scrm', 'scrm_yds', 'pen', 'RUN', 'FUM', 'FP', 'SPRS'],
            'blocking': ['snaps', 'p_snaps', 'r_snaps', 'lt_snaps', 'lg_snaps', 'ce_snaps', 'rg_snaps', 'rt_snaps', 'te_snaps', 'pen', 'PASS_BLOCK', 'RUN_BLOCK', 'FP', 'SPRS'],
            'pass_blocking': ['snaps', 'hur', 'hit', 'sk', 'pr', 'PASS_BLOCK', 't_snaps', 't_hur', 't_hit', 't_sk', 't_pr', 'T_PASS_BLOCK', 'FP', 'SPRS'],
            'run_blocking': ['snaps', 'gap_snaps', 'zone_snaps', 'pen', 'RUN_BLOCK', 'GAP_GRADES', 'ZONE_GRADES', 'FP', 'SPRS'],
            'pass_rush': ['snaps_pp', 'snaps_pr', 'hur', 'hit', 'sk', 'pr', 'pass_rush', 'win', 'bat', 'pen', 'RUSH', 't_snaps_pp', 't_snaps_pr', 't_hur', 't_hit', 't_sk', 't_pr', 't_pass_rush', 't_win', 't_bat', 'T_RUSH', 'FP', 'SPRS'],
            'run_defense': ['snaps', 'com', 'tkl', 'ast', 'stp', 'adot', 'm_tkl', 'ff', 'pen', 'RUN_DEF', 'TACK', 'FP', 'SPRS'],
            'coverage': ['snaps', 'tgt', 'rec', 'yds', 'td', 'int', 'adot', 'ybc', 'yac', 'pbu', 'fi', 'd_int', 'COV', 'FP', 'SPRS'],
            'game_data': ['team', 'year', 'version', 'week', 'gp', 'pts_for', 'pts_against', 'fgm', 'fga', 'xpm', 'xpa']
        }



    def convert_results(self, results: tuple[tuple], is_player: bool, stat: str) -> list[dict]:
        final_results = {}
        start = self.player_start_header if is_player else self.team_start_header
        header = start + self.headers[stat] if stat != 'game_data' else self.headers[stat]
            
        for result in results:
            results = (dict(zip(header, result)))
            final_results[results['week']] = results
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



if __name__ == "__main__":
    converter = Converter()
    headers = converter.headers
    for stat, types in headers.items():
        items = ['[']
        for t in types:
            items.append(f"'{t.lower()}'")
        items.append('],')
        s = ', '.join(items)
        print(f"'{stat}': {s}")