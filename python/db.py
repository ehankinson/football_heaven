import csv
import sqlite3

from constants import *

conn = sqlite3.connect("db/football.db")
cursor = conn.cursor()


def insert_players(player_id: int, player_name: str, player_pos: str):
    query = """
INSERT OR IGNORE INTO PLAYERS (Player_ID, Player_Name, Player_Pos)
VALUES (?, ?, ?)
"""
    cursor.execute(query, (player_id, player_name, player_pos))
    conn.commit()



def insert_teams(team_id: int, team_name: str):
    query = """
INSERT OR IGNORE INTO TEAMS (Team_ID, Team_Name)
VALUES (?, ?)
"""
    cursor.execute(query, (team_id, team_name))
    conn.commit()



def insert_game(game_id: int, year: int, week: int, team_name: str):
    cursor.execute("""
    SELECT COUNT(*) FROM GAME_DATA 
    WHERE Year = ? AND Week = ? AND Team = ?
""", (year, week, team_name))
    
    if not cursor.fetchone()[0] > 0:
        query = """
    INSERT OR IGNORE INTO GAME_DATA (Game_ID, Year, Week, Team)
    VALUES (?, ?, ?, ?)
    """
        cursor.execute(query, (game_id, year, week, team_name))
        conn.commit()



def insert_passing(row: list, year: int): 
    week = row[0]
    team = row[4]
    cursor.execute("""
    SELECT Game_ID FROM GAME_DATA 
    WHERE Year = ? AND Week = ? AND Team = ?
""", (year, week, team))

    game_id = cursor.fetchone()[0]

    cursor.execute("""
SELECT Team_ID
FROM TEAMS
WHERE Team_Name = ?
""", (team,))
    team_id = cursor.fetchone()[0]

    stats = [int(row[2]), game_id, team_id, "passing"]
    for val in PASSING.values():
        if val != 9:
            stats.append(int(row[val]))
        else:
            if row[val] == '':
                stats.append(0)
                continue
            new_value = round(float(row[val]) * int(row[7]), 0)
            stats.append(new_value)

    query = """
INSERT INTO PASSING (Player_ID, Game_ID, Team_ID, Type, aimed_passes, attempts, avg_depth_of_target, bats, big_time_throws, completions, dropbacks, drops, first_downs, hit_as_threw, interceptions, passing_snaps, penalties, sacks, scrambles, spikes, thrown_aways, touchdowns, turnover_worthy_plays, yards)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""
    cursor.execute(query, (stats))
    conn.commit()



START_FILE = "csv/PFF_{info}_{year}.csv"
INFO = [
    "Passing",
    # "Passing_Depth",
    # "Passing_Pressure",
    # "Receiving",
    # "Receiving_Depth",
    # "Receiving_Scheme",
    # "Rushing",
    # "Blocking_Pass",
    # "Blocking_Rush",
    # "Defense_Coverage",
    # "Defense_Coverage_Scheme",
    # "Defense_Pass_Rush",
    # "Defense_Run_Defense"
]

start_year = 2024
end_year = 2025


# cursor.execute("DELETE FROM PASSING")
# conn.commit()
for year in range(start_year, end_year):
    for info in INFO:
        csv_file = START_FILE.format(info=info, year=year)
        with open(csv_file, "r") as c:
            reader = csv.reader(c)

            print(f"On file: {csv_file}")
            
            for row in reader:

                if row[1] == "player":
                    continue
                    
                insert_passing(row, year)

conn.close()