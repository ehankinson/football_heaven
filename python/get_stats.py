import time 

from db import DB
from queries import *
from prettytable import PrettyTable

class GetStats():

    def __init__(self, db: DB) -> None:
        self.db = db
        self.PASSING_HEADERS = ["Pick", "Year", "VERSION", "TEAM", "POS", "GP", "Snaps", "DB", "Cmp", "Aim", "Att", "Yds", "ADOT", "TD", "Int", "1D", "BTT", "TWP", "DRP", "Bat", "Hat", "TA", "Spk", "Sk", "Scrm", "Pen", "Grade", "FP", "SPRS"]
        self.RECEIVING_HEADERS = ["Pick", "Year", "VERSION", "TEAM", "POS", "GP", "Snaps", "Wide", "Slot", "In", "RTS", "TGT", "REC", "YDS", "TD", "INT", "1D", "DRP", "YBC", "YAC", "AT", "FUM", "CT", "CR", "PEN", "RECV", "ROUTE", "FP", "SPRS"]



    def _calculate_passing_grade(self, results: list[tuple], is_player: bool = False, grade_type: str = None) -> dict[str, dict[str, int | float]]:
        results_dict = {}
        key_index = [0, 2] if is_player else [1, 2]

        for result in results:
            key = f"{result[key_index[0]]}_{result[key_index[1]]}"
            if key not in results_dict:
                results_dict[key] = {"att": result[-2], "grade": result[-1]}
                continue
            
            new_total = results_dict[key]["att"] + result[-2]
            if new_total == 0:
                continue

            old_grade_pct = (results_dict[key]["att"] / new_total) * results_dict[key]["grade"]
            new_grade_pct = (result[-2] / new_total) * result[-1]

            results_dict[key]["att"] = new_total
            results_dict[key]["grade"] = old_grade_pct + new_grade_pct
        
        return results_dict
    


    def _calculate_receiving_grade(self, results: list[tuple], is_player: bool = False, grade_type: str = None) -> dict[str, dict[str, int | float]]:
        results_dict = {}
        key_index = [0, 2] if is_player else [1, 2]

        for result in results:
            key = f"{result[key_index[0]]}_{result[key_index[1]]}"
            routes = result[3]
            g1 = result[-2]
            g2 = result[-1]

            if key not in results_dict:
                results_dict[key] = {"routes": routes, "grade1": result[-2], "grade2": result[-1]}
                continue
            
            new_total = results_dict[key]["routes"] + routes
            if new_total == 0:
                continue

            old_g1 = (results_dict[key]["routes"] / new_total) * results_dict[key]["grade1"]
            old_g2 = (results_dict[key]["routes"] / new_total) * results_dict[key]["grade2"]

            new_g1 = (routes / new_total) * g1
            new_g2 = (routes / new_total) * g2

            results_dict[key]["routes"] = new_total
            results_dict[key]["grade1"] = old_g1 + new_g1
            results_dict[key]["grade2"] = old_g2 + new_g2
        
        return results_dict
            
            

    def _calculate_fantasy_points(self, result: list, stat: str, base: int = None) -> int:
        fp = 0
        match stat:
            case "passing":
                fp += result[base] * 0.05     # yds
                fp += result[base + 2] * 6    # td
                fp -= result[base + 3] * 6    # int
                fp += result[base + 4] * 0.5  # 1d
                fp += result[base + 5] * 3    # btt
                fp -= result[base + 6] * 3    # twp
                fp -= result[base + 11] * 1.5 # sk
                fp -= result[base + 12] * 3   # pen
            case "receiving":
                fp += result[11] * 0.5        # rec
                fp += result[13] * 6          # td
                fp -= result[14] * 6          # int
                fp += result[15] * 0.5        # 1d
                fp -= result[16] * 3          # drp
                fp += result[17] * 0.0875     # ybc
                fp += result[18] * 0.1625     # yac
                fp += result[19] * 2          # at
                fp -= result[20] * 6          # fum
                fp += result[22] * 0.5        # ct
                fp -= result[23] * 3          # pen
        return fp
    


    def calculate_sprs(self, gp: int, grades: list[float], fp: float, type: str) -> float:
        match type:
            case "passing":
                return round((fp / gp) * 0.45 + grades[0] * 0.55, 3)
            case "receiving":
                return round((fp / gp) * 0.45 + grades[0] * 0.35 + grades[1] * 0.2, 3)



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



    def season_passing(self, is_player: bool, args: list):
        start_week, end_week, start_year, end_year, start_type, league, version, pos, limit = args
        sum_query = get_players_passing(start_week, end_week, start_year, end_year, start_type, league, version, pos) if is_player else get_team_passing(start_week, end_week, start_year, end_year, start_type, league, version)
        sum_results = self.db.call_query(sum_query)

        headers = self.PASSING_HEADERS.copy()
        if is_player:
            headers[0] = "Player"
        else:
            headers[0] = "Team"
            headers.pop(3)
            headers.pop(2)

        snaps = headers.index("Snaps")
        start_fp = headers.index("Yds")

        max_att = max(result[snaps] for result in sum_results)

        final_results = []
        for result in sum_results:
            if not result[snaps] >= max_att * 0.25:
                continue

            result = list(result)
            index = headers.index("ADOT")
            result[index] = round(result[index], 1)

            result.append(round(self._calculate_fantasy_points(result, "passing", start_fp), 2))
            result.append(round(self.calculate_sprs(result[snaps], [result[-2]], result[-1], "passing"), 3))
            final_results.append(result)

        self._print_pretty_table(headers, final_results, sort_by="SPRS", order="desc", limit=limit)

        return final_results



    def season_receiving(self, is_player: bool, args: list):
        start_week, end_week, start_year, end_year, start_type, league, pos, limit = args
        # calculated_grades = self._calculate_receiving_grade(grade_results, is_player=is_player)

        sum_query = get_players_receiving(start_week, end_week, start_year, end_year, start_type, league, pos)  # if is_player else get_team_receiving(start_week, end_week, start_year, end_year, start_type, league)
        sum_results = self.db.call_query(sum_query)

        max_routes = max(result[9] for result in sum_results)

        final_results = []
        for result in sum_results:
            key = f"{result[1]}_{result[2]}"
            if not result[9] >= max_routes * 0.25:
                continue

            result = list(result)
            result.insert(17, result[12] - result[17])
            result.insert(6, sum(result[6:9]))
            result.pop(1)
            # result.append(round(calculated_grades[key]["grade2"], 1))
            # result.append(round(calculated_grades[key]["grade1"], 1))
            result.append(round(self._calculate_fantasy_points(result, "receiving"), 2))
            result.append(self.calculate_sprs(result[4], [result[-3], result[-2]], result[-1], "receiving"))
            final_results.append(result)

        self.RECEIVING_HEADERS[0] = "Player" if is_player else "Team"
        self._print_pretty_table(self.RECEIVING_HEADERS, final_results, "SPRS", limit=limit)

        return final_results



    def season_passing_game(self, is_player: bool, args: list, side_of_ball: bool = False, print_table: bool = False):
        start_week, end_week, start_year, end_year, stat_type, league, version, pos, limit, team = args.values()
        query = player_passing_game(start_week, end_week, start_year, end_year, stat_type, league, version, team) if is_player else get_passing_game(start_week, end_week, start_year, end_year, stat_type, league, version, team, opp=side_of_ball)
        results = self.db.call_query(query)
        return results



if __name__ == "__main__":
    db = DB()
    team = "NO"
    year = 2024
    start_week = 1
    end_week = 32
    sy = 2006
    ey = 2024
    start_type = "passing"
    league = "NFL"
    version = "1.0"
    pos = ["QB"]
    limit = 50

    is_player = True
    opp = False
    data = [start_week, end_week, sy, ey, start_type, league, version, pos, limit]

    stats = GetStats(db)

    stats.season_passing(is_player, data)
    # off = stats.season_passing_game(is_player, False, data, True)
    # defense = stats.season_passing_game(is_player, True, data)
    db.kill()