import time 
from tqdm import tqdm
from db import Database
from converter import Converter
from prettytable import PrettyTable
from queries import get_query

OPP = True
ASC = False
DESC = True
TEAM = False
TOTAL = True
PLAYER = True
DISPLAY = True
OFFENSE = True
DEFENSE = False
PER_GAME = True
STATS = {
    "passing": False,
    "rushing": False,
    "receiving": False,
    "blocking": False,
    "pass_blocking": False,
    "run_blocking": False,
    "pass_rush": True,
    "run_defense": True,
    "coverage": True,
    "game_data": False
}

class GetStats():

    def __init__(self) -> None:
        self.db = Database()
        self.converter = Converter()
        self.start_header = ["Pick", "Year", "VERSION", "TEAM", "POS", "GP"]
        self.headers = {
            'passing': ['snaps', 'db', 'cmp', 'aim', 'att', 'yds', 'adot', 'td', 'int', '1d', 'btt', 'twp', 'drp', 'bat', 'hat', 'ta', 'spk', 'sk', 'scrm', 'pen', 'PASS', 'FP', 'SPRS'],
            'receiving': ['snaps', 'wide', 'slot', 'in', 'rts', 'tgt', 'rec', 'yds', 'td', 'int', '1d', 'drp', 'ybc', 'yac', 'at', 'fum', 'ct', 'cr', 'pen', 'RECV', 'ROUTE', 'FP', 'SPRS'],
            'rushing': ['snaps', 'att', 'yds', 'td', 'fum', '1d', 'avd', 'exp', 'ybc', 'yac', 'b_att', 'b_yds', 'des_yds', 'gap_att', 'zone_att', 'scrm', 'scrm_yds', 'pen', 'RUN', 'FUM', 'FP', 'SPRS'],
            'blocking': ['snaps', 'p_snaps', 'r_snaps', 'lt_snaps', 'lg_snaps', 'ce_snaps', 'rg_snaps', 'rt_snaps', 'te_snaps', 'pen', 'PASS_BLOCK', 'RUN_BLOCK', 'FP', 'SPRS'],
            'pass_blocking': ['snaps', 'hur', 'hit', 'sk', 'pr', 'PASS_BLOCK', 't_snaps', 't_hur', 't_hit', 't_sk', 't_pr', 'T_PASS_BLOCK', 'FP', 'SPRS'],
            'run_blocking': ['snaps', 'gap_snaps', 'zone_snaps', 'pen', 'RUN_BLOCK', 'GAP_GRADES', 'ZONE_GRADES', 'FP', 'SPRS'],
            'pass_rush': ['snaps_pp', 'snaps_pr', 'hur', 'hit', 'sk', 'pr', 'pass_rush', 'win', 'bat', 'pen', 'RUSH', 't_snaps_pp', 't_snaps_pr', 't_hur', 't_hit', 't_sk', 't_pr', 't_pass_rush', 't_win', 't_bat', 'T_RUSH', 'FP', 'SPRS'],
            'run_defense': ['snaps', 'com', 'tkl', 'ast', 'stp', 'adot', 'm_tkl', 'ff', 'pen', 'RUN_DEF', 'TACK', 'FP', 'SPRS'],
            'coverage': ['snaps', 'tgt', 'rec', 'yds', 'td', 'int', 'adot', 'ybc', 'yac', 'pbu', 'fi', 'd_int', 'COV', 'FP', 'SPRS']
        }
        self.max_key = {
            "passing": "db",
            "receiving": "rts",
            "rushing": "att",
            "blocking": "snaps",
            "pass_blocking": "snaps",
            "run_blocking": "snaps",
            "pass_rush": "snaps_pr",
            "run_defense": "snaps",
            "coverage": "snaps"
        }
            
            

    def _calculate_fantasy_points(self, result: dict, stat: str, sub_stat: str = None) -> int:
        fp = 0
        stats = None
        match stat:
            case "passing":
                stats = {"yds": 0.05, "td": 6, "int": -6, "1d": 0.5, "btt": 3, "twp": -3, "sk": -1.5, "pen": -3}
            case "receiving":
                stats = {"rec": 0.5, "td": 6, "int": -6, "1d": 0.5, "drp": 3, "ybc": 0.0875, "yac": 0.1625, "at": 2, "fum": -6, "cr": 0.5, "pen": -3}      
            case "rushing":
                stats = {"td": 6, "fum": -6, "1d": 0.5, "avd": 0.75, "exp": 1.5, "ybc": 0.0875, "yac": 0.1625, "pen": -3}
            case "pass_blocking":
                stats = {"hur": -0.25, "hit": -0.3125, "sk": -0.375, "pr": -0.1875, "t_hur": -0.5, "t_hit": -0.625, "t_sk": -0.75, "t_pr": -0.375}
            case "pass_rush":
                stats = {"hur": 0.25, "hit": 0.3125, "sk": 0.375, "pr": 0.1875, "win": 0.4375, "pen": -3, "t_hur": 0.5, "t_hit": 0.625, "t_sk": 0.75, "t_pr": 0.375, "t_win": 0.875}
            case "run_defense":
                stats = {"tkl": 1.25, "ast": 0.75, "stop": 2.25, "m_tkl": -1, "ff": 3, "pen": -3}
            case "coverage":
                stats = {"rec": -0.5, "td": -6, "int": 6, "ybc": -0.0875, "yac": -0.1625, "pbu": 3, "fi": 2.5, "d_int": 1.5}
            case "total":
                results = {
                    "passing": {"td": 6, "int": -6, "1d": 0.5, "btt": 3, "twp": -3, "pen": -3},
                    "rushing": {"td": 6, "fum": -6, "1d": 0.5, "avd": 0.75, "exp": 1.5, "ybc": 0.0875, "yac": 0.1625, "pen": -3},
                    "receiving": {"rec": 0.5, "drp": 3, "ybc": 0.0875, "yac": 0.1625, "at": 2, "fum": -6, "cr": 0.5, "pen": -3},
                    "pass_blocking": {"hur": -0.25, "hit": -0.3125, "sk": -0.375, "pr": -0.1875, "t_hur": -0.5, "t_hit": -0.625, "t_sk": -0.75, "t_pr": -0.375},
                    "pass_rush": {"win": -0.4375, "pen": 3, "t_win": -0.875},
                    "run_defense": {"tkl": -0.3125, "ast": -0.1875, "stp": -0.5625, "m_tkl": 0.125, "ff": -0.75, "pen": 0.75},
                    "coverage": {"pbu": -3, "fi": -2.5, "d_int": -1.5}
                }
                if sub_stat not in results:
                    return 0
                stats = results[sub_stat]

        if stats is not None:
            for stat, mul in stats.items():
                fp += result[stat] * mul

        return fp
    


    def calculate_sprs(self, headers: list, results: list, _type: str) -> float:
        match _type:
            case "passing":
                return round((results[headers.index("FP")] / results[headers.index("GP")]) * 0.45 + results[headers.index("Grade")] * 0.55, 3)
            case "receiving":
                return round((results[headers.index("FP")] / results[headers.index("GP")]) * 0.4 + results[headers.index("RECV")] * 0.5 + results[headers.index("ROUTE")] * 0.1, 3)
            case "rushing":
                return round((results[headers.index("FP")] / results[headers.index("GP")]) * 0.4 + results[headers.index("RUN")] * 0.5 + results[headers.index("FUM")] * 0.1, 3)
            case "blocking":
                if results[headers.index("PASS_BLOCK")] is None:
                    results[headers.index("PASS_BLOCK")] = 0

                if results[headers.index("RUN_BLOCK")] is None:
                    results[headers.index("RUN_BLOCK")] = 0

                return round(results[headers.index("PASS_BLOCK")] * 0.55 + results[headers.index("RUN_BLOCK")] * 0.45, 3)
            case "pass_blocking":
                if results[headers.index("T_PASS_BLOCK")] is None:
                    results[headers.index("T_PASS_BLOCK")] = 0

                return round((results[headers.index("FP")] / results[headers.index("GP")]) * 0.4 + results[headers.index("PASS_BLOCK")] * 0.325 + results[headers.index("T_PASS_BLOCK")] * 0.275, 3)
            case "run_blocking":
                gap_pct = results[headers.index("GAP_SNAPS")] / results[headers.index("Snaps")]
                if results[headers.index("GAP_GRADES")] is None:
                    results[headers.index("GAP_GRADES")] = 0

                if results[headers.index("ZONE_GRADES")] is None:
                    results[headers.index("ZONE_GRADES")] = 0

                return round(results[headers.index("GAP_GRADES")] * gap_pct + results[headers.index("ZONE_GRADES")] * (1 - gap_pct), 3)
            case "pass_rush":
                if results[headers.index("T_RUSH")] is None:
                    results[headers.index("T_RUSH")] = 0
                return round((results[headers.index("FP")] / results[headers.index("GP")]) * 0.4 + results[headers.index("T_RUSH")] * 0.25 + results[headers.index("RUSH")] * 0.25, 3)
            case "run_defense":
                return round((results[headers.index("FP")] / results[headers.index("GP")]) * 0.3 + results[headers.index("RUN_DEF")] * 0.35 + results[headers.index("TACK")] * 0.35, 3)
            case "coverage":
                return round((results[headers.index("FP")] / results[headers.index("GP")]) * 0.35 + results[headers.index("COV")] * 0.65, 3)



    def _print_pretty_table(self, headers: list[str], results: list[list], order: bool, sort_by: str = None, limit: int = None) -> None:
        table = PrettyTable()
        table.field_names = headers

        if sort_by is not None and sort_by not in headers:
            raise ValueError(f"Sort by column '{sort_by}' not found in headers, Please choose from: {headers}")

        if sort_by is not None:
            results.sort(key=lambda x: x[headers.index(sort_by)], reverse=order)

        if limit is not None:
            results = results[:limit]

        table.add_rows(results)
        print(table)



    def season_stats(self, args: dict, _type: str, is_player: bool, display: bool = False, order: bool = False, by_game: bool = False, opp: bool = False):
        query = get_query(args, _type, is_player, by_game, opp)
        results = self.converter.convert_results(self.db.call_query(query), is_player, _type)

        if not display:
            return results
        
        header = self.start_header + self.headers[_type]
        if is_player:
            header[0] = "Player"
            if by_game:
                header.insert(5, "Week")
        else:
            header[0] = "Team"
            [header.pop(i) for i in [4, 3]]
            if by_game:
                header.insert(3, "Week")

        # att = header.index(self.max_key[_type])
        # max_att = max(result[att] for result in results)

        final_results = []
        for week in results:

            # result = list(result)
            results[week]['fp'] = round(self._calculate_fantasy_points(results[week], _type), 2)
            results[week]['sprs'] = 0
            # result.append(round(self.calculate_sprs(header, result, _type), 3))

            # if not result[att] >= max_att * 0.25:
            #     result[-1] = result[-1] / 4

            final_results.append(list(results[week].values()))

        self._print_pretty_table(header, final_results, sort_by="FP", order=order, limit=limit)

        return final_results



    def get_total_stats(self, args: dict, is_offense: bool) -> list:
        total_stats = {'scoring': {}}
        for stat in STATS:
            if stat not in total_stats:
                total_stats[stat] = {}

            if stat == "game_data":
                continue
                # args['stat_type'], args['league'] = None, None
                # query = game_data_query(args)
                # results = self.db.call_query(query)
                # total_stats[stat] = results
                # continue

            args['stat_type'] = stat
            opp = STATS[stat] if is_offense else not STATS[stat]
            results = self.season_stats(args, stat, TEAM, by_game=PER_GAME, opp=opp)

            total_stats[stat] = results
            for week in results:
                if week not in total_stats['scoring']:
                    total_stats['scoring'][week] = {'FP': 0}

                total_stats['scoring'][week]['FP'] += self._calculate_fantasy_points(total_stats[stat][week], "total", sub_stat=stat)

        return total_stats


if __name__ == "__main__":
    team = "CAR"
    year = 2012
    start_week = 1
    end_week = 32
    stat_type = "passing"
    league = "NFL"
    version = "0.0"
    pos = None
    limit = 50
    args = {"start_week": start_week, "end_week": end_week, "start_year": year, "end_year": year, "stat_type": stat_type, "league": league, "version": version, "pos": pos, "limit": limit, "team": team}
    _type = stat_type

    stats = GetStats()