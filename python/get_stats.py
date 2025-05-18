import time 

from db import Database
from queries import get_query
from prettytable import PrettyTable

OPP = True
ASC = False
TEAM = False
DESC = True
PLAYER = True
DISPLAY = True
PER_GAME = True

class GetStats():

    def __init__(self, db: Database) -> None:
        self.db = db
        self.start_header = ["Pick", "Year", "VERSION", "TEAM", "POS", "GP"]
        self.headers = {
            "passing": ["Snaps", "DB", "Cmp", "Aim", "Att", "Yds", "ADOT", "TD", "Int", "1D", "BTT", "TWP", "DRP", "Bat", "Hat", "TA", "Spk", "Sk", "Scrm", "Pen", "Grade", "FP", "SPRS"],
            "receiving": ["Snaps", "Wide", "Slot", "In", "RTS", "TGT", "REC", "YDS", "TD", "INT", "1D", "DRP", "YBC", "YAC", "AT", "FUM", "CT", "CR", "PEN", "RECV", "ROUTE", "FP", "SPRS"],
            "rushing": ["Snaps", "Att", "Yds", "TD", "Fum", "1D", "Avd", "Exp", "Ybc", "Yac", "b_att", "b_yds", "des_yds", "gap_att", "zone_att", "scrm", "scrm_yds", "pen", "RUN", "FUM", "FP", "SPRS"],
            "blocking": ["Snaps", "P_SNAPS", "R_SNAPS", "LT_SNAPS", "LG_SNAPS", "CE_SNAPS", "RG_SNAPS", "RT_SNAPS", "TE_SNAPS", "PEN", "PASS_BLOCK", "RUN_BLOCK", "FP", "SPRS"],
            "pass_blocking": ["Snaps", "HUR", "HIT", "SK", "PR", "PASS_BLOCK", "T_Snaps", "T_HUR", "T_HIT", "T_SK", "T_PR", "T_PASS_BLOCK", "FP", "SPRS"],
            "run_blocking": ["Snaps", "GAP_SNAPS", "ZONE_SNAPS", "PEN", "RUN_BLOCK", "GAP_GRADES", "ZONE_GRADES", "FP", "SPRS"],
            "pass_rush": ["Snaps_pp", "Snaps_pr", "HUR", "HIT", "SK", "PR", "PASS_RUSH", "WIN", "BAT", "PEN", "RUSH", "T_Snaps_pp", "T_Snaps_pr", "T_HUR", "T_HIT", "T_SK", "T_PR", "T_PASS_RUSH", "T_WIN", "T_BAT", "T_RUSH", "FP", "SPRS"],
            "run_defense": ["Snaps", "Combo", "Tackles", "Assists", "Stops", "Adot", "Missed Tackles", "FF", "PEN", "RUN_DEF", "TACK", "FP", "SPRS"],
            "coverage": ["Snaps", "TGT", "REC", "YDS", "TD", "INT", "ADOT", "YBC", "YAC", "PBU", "FI", "D_INT", "COV", "FP", "SPRS"] 
        }
        self.max_key = {
            "passing": "DB",
            "receiving": "RTS",
            "rushing": "Att",
            "blocking": "Snaps",
            "pass_blocking": "Snaps",
            "run_blocking": "Snaps",
            "pass_rush": "Snaps_pr",
            "run_defense": "Snaps",
            "coverage": "Snaps"
        }
            
            

    def _calculate_fantasy_points(self, result: list, stat: str, header: list) -> int:
        fp = 0
        stats = None
        match stat:
            case "passing":
                stats = {"Yds": 0.05, "TD": 6, "Int": -6, "1D": 0.5, "BTT": 3, "TWP": -3, "Sk": -1.5, "Pen": -3}
            case "receiving":
                stats = {"REC": 0.5, "TD": 6, "INT": -6, "1D": 0.5, "DRP": 3, "YBC": 0.0875, "YAC": 0.1625, "AT": 2, "FUM": -6, "CR": 0.5, "PEN": -3}      
            case "rushing":
                stats = {"TD": 6, "Fum": -6, "1D": 0.5, "Avd": 0.75, "Exp": 1.5, "Ybc": 0.0875, "Yac": 0.1625, "pen": -3}
            case "pass_blocking":
                stats = {"HUR": -0.25, "HIT": -0.3125, "SK": -0.375, "PR": -0.1875, "T_HUR": -0.5, "T_HIT": -0.625, "T_SK": -0.75, "T_PR": -0.375}
            case "pass_rush":
                stats = {"HUR": 0.25, "HIT": 0.3125, "SK": 0.375, "PR": 0.1875, "WIN": 0.4375, "PEN": -3, "T_HUR": 0.5, "T_HIT": 0.625, "T_SK": 0.75, "T_PR": 0.375, "T_WIN": 0.875}
            case "run_defense":
                stats = {"Tackles": 1.25, "Assists": 0.75, "Stops": 2.25, "Missed Tackles": -1, "FF": 3, "PEN": -3},
            case "coverage":
                stats = {"REC": -0.5, "TD": -6, "INT": 6, "YBC": -0.0875, "YAC": -0.1625, "PBU": 3, "FI": 2.5, "D_INT": 1.5}

        if stats is not None:
            for stat, mul in stats.items():
                fp += result[header.index(stat)] * mul 

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



    def season_stats(self, args: dict, _type: str, is_player: bool, display: bool, order: bool, by_game: bool = False):
        query = get_query(args, _type, is_player, by_game)
        results = self.db.call_query(query)

        if not display:
            return results
        
        header = self.start_header + self.headers[_type]
        if is_player:
            header[0] = "Player"
        else:
            header[0] = "Team"
            [header.pop(i) for i in [4, 3]]
        
        att = header.index(self.max_key[_type])

        max_att = max(result[att] for result in results)

        final_results = []
        for result in results:
            if not result[att] >= max_att * 0.45:
                continue

            result = list(result)

            result.append(round(self._calculate_fantasy_points(result, _type, header), 2))
            result.append(round(self.calculate_sprs(header, result, _type), 3))

            final_results.append(result)

        self._print_pretty_table(header, final_results, sort_by="SPRS", order=order, limit=limit)

        return final_results



if __name__ == "__main__":
    db = Database()
    team = "CAR"
    year = 2006
    start_week = 1
    end_week = 32
    start_year = 2024
    end_year = 2024
    stat_type = "passing"
    league = "NFL"
    version = "0.0"
    pos = ["QB"]
    limit = 50
    args = {"start_week": start_week, "end_week": end_week, "start_year": start_year, "end_year": end_year, "stat_type": stat_type, "league": league, "version": version, "pos": pos, "limit": limit, "team": team}
    _type = stat_type
    stats = GetStats(db)

    stats.season_stats(args, _type, TEAM, DISPLAY, DESC, PER_GAME)
    db.kill()