import time 

from db import Database
from queries import get_query
from prettytable import PrettyTable

OPP = True
TEAM = False
PLAYER = True
DISPLAY = True

class GetStats():

    def __init__(self, db: Database) -> None:
        self.db = db
        self.start_header = ["Pick", "Year", "VERSION", "TEAM", "POS", "GP"]
        self.headers = {
            "passing": self.start_header + ["Snaps", "DB", "Cmp", "Aim", "Att", "Yds", "ADOT", "TD", "Int", "1D", "BTT", "TWP", "DRP", "Bat", "Hat", "TA", "Spk", "Sk", "Scrm", "Pen", "Grade", "FP", "SPRS"],
            "receiving": self.start_header + ["Snaps", "Wide", "Slot", "In", "RTS", "TGT", "REC", "YDS", "TD", "INT", "1D", "DRP", "YBC", "YAC", "AT", "FUM", "CT", "CR", "PEN", "RECV", "ROUTE", "FP", "SPRS"],
            "rushing": self.start_header + ["Snaps", "Att", "Yds", "TD", "Fum", "1D", "Avd", "Exp", "Ybc", "Yac", "b_att", "b_yds", "des_yds", "gap_att", "zone_att", "scrm", "scrm_yds", "pen", "RUN", "FUM", "FP", "SPRS"],
            "pass_rush": self.start_header + ["Snaps_pp", "Snaps_pr", "HUR", "HIT", "SK", "PR", "PASS_RUSH", "WIN", "BAT", "PEN", "RUSH", "T_Snaps_pp", "T_Snaps_pr", "T_HUR", "T_HIT", "T_SK", "T_PR", "T_PASS_RUSH", "T_WIN", "T_BAT", "T_RUSH", "FP", "SPRS"]
        }
        self.max_key = {
            "passing": "DB",
            "receiving": "RTS",
            "rushing": "Att",
            "pass_rush": "Snaps_pr"
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
            case "pass_rush":
                stats = {"HUR": 0.25, "HIT": 0.3125, "SK": 0.375, "PR": 0.1875, "WIN": 0.4375, "PEN": -3, "T_HUR": 1, "T_HIT": 1.25, "T_SK": 1.5, "T_PR": 0.75, "T_WIN": 1.75}

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
            case "pass_rush":
                if results[headers.index("T_RUSH")] is None:
                    results[headers.index("T_RUSH")] = 0
                return round((results[headers.index("FP")] / results[headers.index("GP")]) * 0.4 + results[headers.index("T_RUSH")] * 0.25 + results[headers.index("RUSH")] * 0.25, 3)



    def _print_pretty_table(self, headers: list[str], results: list[list], sort_by: str = None, order: str = "desc", limit: int = None) -> None:
        table = PrettyTable()
        table.field_names = headers

        if sort_by is not None and sort_by not in headers:
            raise ValueError(f"Sort by column '{sort_by}' not found in headers, Please choose from: {headers}")

        if sort_by is not None:
            order = True if order == "desc" else False
            results.sort(key=lambda x: x[headers.index(sort_by)], reverse=order)

        if limit is not None:
            results = results[:limit]

        table.add_rows(results)
        print(table)



    def season_stats(self, args: dict, _type: str, is_player: bool, display: bool):
        query = get_query(args, _type, is_player)
        results = self.db.call_query(query)

        if not display:
            return results
        
        header = self.headers[_type]
        if is_player:
            header[0] = "Player"
        else:
            header[0] = "Team"
            header.pop(4)
            header.pop(3)
        
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

        self._print_pretty_table(header, final_results, sort_by="SPRS", order="desc", limit=limit)

        return final_results



if __name__ == "__main__":
    db = Database()
    team = None
    year = 2006
    start_week = 1
    end_week = 32
    start_year = 2006
    end_year = 2024
    stat_type = "pass_rush"
    league = "NFL"
    version = "0.0"
    pos = ["QB"]
    limit = 50
    args = {"start_week": start_week, "end_week": end_week, "start_year": start_year, "end_year": end_year, "stat_type": stat_type, "league": league, "version": version, "pos": pos, "limit": limit, "team": team}
    _type = stat_type
    stats = GetStats(db)

    stats.season_stats(args, _type, PLAYER, DISPLAY)
    db.kill()