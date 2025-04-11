
from db import DB
from prettytable import PrettyTable
from queries import get_players_passing, get_passing_grades, get_team_passing, get_players_receiving

class GetStats():

    def __init__(self, db: DB) -> None:
        self.db = db
        self.PASSING_HEADERS = ["Pick", "Year", "GP", "Snaps", "DB", "Cmp", "Aim", "Att", "Yds", "TD", "Int", "1D", "BTT", "TWP", "DRP", "Bat", "Hat", "TA", "Spk", "Sk", "Scrm", "Pen", "Grade", "FP", "SPRS"]
        self.RECEIVING_HEADERS = ["Pick", "Year", "TEAM", "POS","GP", "Snaps", "Wide", "Slot", "In", "RTS", "TGT", "REC", "YDS", "TD", "INT", "1D", "DRP", "YBC", "YAC", "AT", "FUM", "CT", "CR", "PEN", "RECV", "ROUTE", "FP", "SPRS"]


    def _calculate_grade(self, results: list[tuple], is_player: bool = False) -> dict[str, dict[str, int | float]]:
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
    


    def _calculate_fantasy_points(self, result: list, stat: str) -> int:
        fp = 0
        match stat:
            case "passing":
                fp += result[9] * 0.05 # yds
                fp += result[10] * 6   # td
                fp -= result[11] * 6   # int
                fp += result[12] * 0.5 # 1d
                fp += result[13] * 3   # btt
                fp -= result[14] * 3   # twp
                fp -= result[20] * 1.5 # sk
                fp -= result[22] * 3   # pen
            case "receiving":
                fp += result[11] * 0.5 # rec
                fp += result[13] * 6   # td
                fp -= result[14] * 6   # int
                fp += result[15] * 0.5 # 1d
                fp -= result[16] * 3 # drp
                fp += result[17] * 0.0875 # ybc
                fp += result[18] * 0.1625 # yac
                fp += result[19] * 2 # at
                fp -= result[20] * 6 # fum
                fp += result[22] * 0.5 # ct
                fp -= result[23] * 3 # pen
        return fp
    


    def calculate_sprs(self, att: int, grade: float, fp: float) -> float:
        return round((fp / att) * 0.45 + grade * 0.55, 3)



    def _print_pretty_table(self, headers: list[str], results: list[list], sort_by: str = None, limit: int = None) -> None:
        table = PrettyTable()
        table.field_names = headers

        if sort_by is not None and sort_by not in headers:
            raise ValueError(f"Sort by column '{sort_by}' not found in headers, Please choose from: {headers}")

        if sort_by is not None:
            results.sort(key=lambda x: x[headers.index(sort_by)], reverse=True)

        if limit is not None:
            results = results[:limit]

        table.add_rows(results)
        print(table)



    def season_passing(self, is_player: bool, args: list):
        start_week, end_week, start_year, end_year, start_type, league, pos, limit = args
        sum_query = get_players_passing(start_week, end_week, start_year, end_year, start_type, league, pos) if is_player else get_team_passing(start_week, end_week, start_year, end_year, start_type, league)
        grade_query = get_passing_grades(start_week, end_week, start_year, end_year, start_type, league, pos)

        grade_results = self.db.call_query(grade_query)
        calculated_grades = self._calculate_grade(grade_results, is_player=is_player)

        sum_results = self.db.call_query(sum_query)

        max_att = max(result[5] for result in sum_results)

        final_results = []
        for result in sum_results:
            if not result[5] >= max_att * 0.25:
                continue

            key = f"{result[1]}_{result[2]}"
            result = list(result)

            result.append(round(calculated_grades[key]["grade"], 1))
            result.append(round(self._calculate_fantasy_points(result, "passing"), 2))
            result.append(round(self.calculate_sprs(result[5], result[-2], result[-1]), 3))
            result.pop(1)
            final_results.append(result)

        self.PASSING_HEADERS[0] = "Player" if is_player else "Team"
        self._print_pretty_table(self.PASSING_HEADERS, final_results, "SPRS", limit=limit)

        return final_results



    def season_receiving(self, is_player: bool, args: list):
        start_week, end_week, start_year, end_year, start_type, league, pos, limit = args
        sum_query = get_players_receiving(start_week, end_week, start_year, end_year, start_type, league, pos)  # if is_player else get_team_receiving(start_week, end_week, start_year, end_year, start_type, league)
        sum_results = self.db.call_query(sum_query)

        max_routes = max(result[9] for result in sum_results)
        final_results = []
        for result in sum_results:
            if not result[9] >= max_routes * 0.25:
                continue

            result = list(result)
            result.insert(17, result[12] - result[17])
            result.insert(6, sum(result[6:9]))
            result.pop(1)
            result.append("G1")
            result.append("G2")
            result.append(round(self._calculate_fantasy_points(result, "receiving"), 2))
            result.append(round(result[-1] / result[4], 2))
            final_results.append(result)

        self.RECEIVING_HEADERS[0] = "Player" if is_player else "Team"
        self._print_pretty_table(self.RECEIVING_HEADERS, final_results, "SPRS", limit=limit)

        return final_results


if __name__ == "__main__":
    db = DB()
    start_week = 29
    end_week = 33
    sy = 2023
    ey = 2023
    start_type = "receiving"
    league = "NFL"
    pos = ["HB", "FB", "WR", "TE"]
    limit = 50

    team = True
    data = [start_week, end_week, sy, ey, start_type, league, pos, limit]

    stats = GetStats(db)

    stats.season_receiving(team, data)
    db.kill()