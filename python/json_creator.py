import csv
import json

from constants import *



def _add_stats(path: dict, stat: dict) -> None:
    for key, index in stat.items():
        num = float(row[index]) if row[index] else 0
        value = int(num * int(row[index - 2])) if "avg_depth_of_target" in key else int(row[index])
        
        if key in path:
            path[key] += value
        else:
            path[key] = value



def adding_PASSING_stats(year_data: dict, team_id: int, week: int, stat: str) -> None:
    _add_stats(year_data[team_id][week][stat], KEYS[stat])



def adding_PASSING_DEPTH_stats(year_data: dict, team_id: int, week: int, stat: str) -> None:
    for depth in KEYS[stat]:
        year_data[team_id][week][stat][depth] = {}
        for side in KEYS[stat][depth]:
            year_data[team_id][week][stat][depth][side] = {}
            _add_stats(year_data[team_id][week][stat][depth][side], KEYS[stat][depth][side])



if __name__ == "__main__":
    YEAR = 2024
    FILE_NAME = "PFF_{stat}_{year}.csv"
    KEYS = { "Passing": PASSING, "Passing_Depth": PASSING_DEPTH }

    with open("json/teams.json", "r") as j:
        teams = json.load(j)

    with open("json/players.json", "r") as j:
        players = json.load(j)

    files = [
        "Passing",
        "Passing_Depth",
        "Passing_Pressure",
        "Receiving",
        "Receiving_Depth",
        "Receiving_Scheme",
        "Rushing",
        "Blocking",
        "Blocking_Pass",
        "Blocking_Rush",
        "Defense",
        "Defense_Pass_Rush",
        "Defense_Run_Defense",
        "Defense_Coverage",
        "Defense_Coverage_Scheme"
    ]

    year_data = {}

    for stat in files:

        if stat not in KEYS:
            break

        file_name = FILE_NAME.format(stat=stat, year=YEAR)

        with open(f"csv/{file_name}", "r") as c:
            reader = csv.reader(c)

            for row in reader:

                if row[1] == "player":
                    continue

                player_id = row[2]
                if player_id not in players:
                    players[player_id] = row[1]

                team = row[4]
                team_id = teams[team]

                if team_id not in year_data:
                    year_data[team_id] = {}
                
                week = row[0]
                if week not in year_data[team_id]:
                    year_data[team_id][week] = {}

                if stat not in year_data[team_id][week]:
                    year_data[team_id][week][stat] = {}
                
                if stat == "Passing":
                    adding_PASSING_stats(year_data, team_id, week, stat)
                elif stat == "Passing_Depth":
                    adding_PASSING_DEPTH_stats(year_data, team_id, week, stat)
                
                
    with open("json/players.json", "w") as j:
        json.dump(players, j, indent=4)

    with open(f"json/{YEAR}_data.json", "w") as j:
        json.dump(year_data, j, indent=4)