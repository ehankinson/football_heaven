import csv
import sqlite3

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



START_FILE = "csv/PFF_{info}_{year}.csv"
INFO = [
    "Passing",
    "Passing_Depth",
    "Passing_Pressure",
    "Receiving",
    "Receiving_Depth",
    "Receiving_Scheme",
    "Rushing",
    "Blocking_Pass",
    "Blocking_Rush",
    "Defense_Coverage",
    "Defense_Coverage_Scheme",
    "Defense_Pass_Rush",
    "Defense_Run_Defense"
]

start_year = 2024
end_year = 2025



for year in range(start_year, end_year):
    for info in INFO:
        csv_file = START_FILE.format(info=info, year=year)
        with open(csv_file, "r") as c:
            reader = csv.reader(c)

            print(f"One file: {csv_file}")
            
            for row in reader:

                if row[1] == "player":
                    tn = row.index("team_name")
                    ti = row.index("franchise_id")
                    continue

                team_name = row[tn]
                team_id = int(row[ti])

                insert_teams(team_id, team_name)

conn.close()