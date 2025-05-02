import os
import csv
import time
import sqlite3

from tqdm import tqdm
from constants import *
from queries import GAME_DATA, TEAMS, CREATE_PASSING, CREATE_PLAYERS, CREATE_RECEIVING, CREATE_RUSHING, CREATE_BLOCKING, CREATE_PASS_BLOCKING, CREATE_RUN_BLOCKING, INSERT_START, PASSING_INSERT, RECEIVING_INSERT, RUSHING_INSERT, BLOCKING_INSERT, PASS_BLOCKING_INSERT, RUN_BLOCKING_INSERT

PLAYER_ID = 2
MAP = [
    'passing',
    'receiving',
    'players',
    'teams',
    'game_data',
]

INSERT_TABLE = {
    "passing": PASSING_INSERT,
    "receiving": RECEIVING_INSERT,
    "rushing": RUSHING_INSERT,
    "blocking": BLOCKING_INSERT,
    "pass_blocking": PASS_BLOCKING_INSERT,
    "run_blocking": RUN_BLOCKING_INSERT
}



class DB():
    
    def __init__(self) -> None:
        self.START_FILE = "csv/PFF_{league}_{info}_{year}.csv"
        self.cache = 100_000
        self.INFO = [
            "Passing",
            "Passing_Depth",
            "Passing_Pressure",
            "Receiving",
            "Receiving_Depth",
            "Receiving_Scheme",
            "Rushing",
            "Blocking",
            "Pass_Blocking",
            "Run_Blocking",
            # "Defense_Coverage",
            # "Defense_Coverage_Scheme",
            # "Defense_Pass_Rush",
            # "Defense_Run_Defense"
        ]
        self.conn = sqlite3.connect("db/football.db")
        self.cursor = self.conn.cursor()
        
        # Add SQLite optimizations for bulk operations
        self.cursor.execute("PRAGMA synchronous = OFF")
        self.cursor.execute("PRAGMA journal_mode = MEMORY")
        self.cursor.execute("PRAGMA temp_store = MEMORY")
        self.cursor.execute(f"PRAGMA cache_size = {self.cache}")

        self.TABLES = {
            "TEAMS": self.insert_teams,
            "GAME_DATA": self.insert_games,
            "PLAYERS": CREATE_PLAYERS,
            "PASSING": CREATE_PASSING,
            "RECEIVING": CREATE_RECEIVING,
            "RUSHING": CREATE_RUSHING,
            "BLOCKING": CREATE_BLOCKING,
            "PASS_BLOCKING": CREATE_PASS_BLOCKING,
            "RUN_BLOCKING": CREATE_RUN_BLOCKING
        }



    def kill(self) -> None:
        self.conn.close()
    

    
    def commit(self) -> None:
        self.conn.commit()



    def call_query(self, query: str) -> list[tuple]:
        self.cursor.execute(query)
        return self.cursor.fetchall()
    


    def delete_table_values(self, table_name: str):
        query = f"DELETE FROM {table_name}"
        self.cursor.execute(query)
        self.conn.commit()
    


    def drop_table(self, table_name: str):
        query = f"DROP TABLE IF EXISTS {table_name}"
        self.cursor.execute(query)
        self.conn.commit()
    


    def create_table(self, query: str):
        self.cursor.execute(query)
        self.conn.commit()
    


    def get_teams(self, league: str) -> list[str]:
        self.cursor.execute("SELECT Team_Abbr FROM TEAMS WHERE League = ?", (league,))
        result = self.cursor.fetchall()
        return [row[0] for row in result]



    def get_games(self, team_id: int = None, version: str = None, year: int = None, start_week: int = None, end_week: int = None) -> list[list]:
        conditions = []
        if team_id is not None:
            conditions.append(f"Team_ID = {team_id}")
        if version is not None:
            conditions.append(f"Version = {version}")
        if year is not None:
            conditions.append(f"Year = {year}")
        if start_week is not None:
            conditions.append(f"Week >= {start_week}")
        if end_week is not None:
            conditions.append(f"Week <= {end_week}")

        query = "SELECT * FROM GAME_DATA"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return [list(row) for row in result]



    def get_game_id(self, year: int, week: int, team_id: int, version: str) -> int:
        self.cursor.execute("SELECT GAME_ID FROM GAME_DATA WHERE Year = ? AND Week = ? AND Team_ID = ? AND Version = ?", (year, week, team_id, version))
        result = self.cursor.fetchone()
        return result[0] if result is not None else None



    def get_team_id(self, team: str) -> int:
        self.cursor.execute("SELECT Team_ID FROM TEAMS WHERE Team_Abbr = ?", (team,))
        result = self.cursor.fetchone()
        return result[0] if result is not None else None



    def insert_player(self, player_id: int, player_name: str, player_pos: str) -> None:
        query = """
            INSERT OR IGNORE INTO PLAYERS (Player_ID, Player_Name, Player_Pos)
            VALUES (?, ?, ?)
        """
        self.cursor.execute(query, (player_id, player_name, player_pos))
        self.conn.commit()
    


    def insert_teams(self) -> None:
        self.drop_table("TEAMS")
        self.create_table(TEAMS)
        with open("csv/teams.csv", "r") as c:
            reader = csv.reader(c)
            for row in reader:
                if row[1] == "League":
                    continue

                team_abbr = row[0].strip()  # Remove regular spaces and special characters
                league = row[1]
                team_name = row[2].strip()
                division = row[3].strip()
                conference = row[4].strip()
                query = """
                    INSERT OR IGNORE INTO TEAMS (Team_Abbr, League, Team_Name, Division, Conference) VALUES (?, ?, ?, ?, ?)
                """ 
                self.cursor.execute(query, (team_abbr, league, team_name, division, conference))

        self.conn.commit()
    


    def create_tables(self):
        for name, query in self.TABLES.items():
            if isinstance(query, str):
                self.drop_table(name)
                self.create_table(query)
            else:
                query()

    

    def insert_games(self) -> None:
        self.drop_table("GAME_DATA")
        self.create_table(GAME_DATA)
        
        # Get the next available GAME_ID
        self.cursor.execute("SELECT MAX(GAME_ID) FROM GAME_DATA")
        result = self.cursor.fetchone()
        next_game_id = 1 if result[0] is None else result[0] + 1

        leagues = {"NFL": "csv/nfl_games.csv"} #, "NCAA": "csv/ncaa_games.csv"}
        for i, (league, fil) in enumerate(leagues.items()):
            with open(fil, "r") as c:
                reader = csv.reader(c)
                for row in reader:
                    if row[2] == "Team":
                        continue
                    
                    if league == "NCAA":
                        row.insert(14, row[14])

                    row.pop(5)
                    row.pop(1)

                    team_id = self.get_team_id(row[1].strip())
                    opp_id = self.get_team_id(row[4].strip())
                    row[1] = team_id
                    row[4] = opp_id

                    # Convert all available values to integers
                    for i, r in enumerate(row):
                        if not i:
                            continue

                        row[i] = int(r) if r not in {'', None} else 0

                    if league == "NFL":
                        row += [0] * 4
                    
                    # Prepend GAME_ID to row
                    row = [next_game_id] + row
                    next_game_id += 1
                    
                    query = f"""
                        INSERT OR IGNORE INTO GAME_DATA (
                            GAME_ID, Version, Team_ID, Year, Week, Opponent_ID, Points_For, Points_Against, Diff,
                            TD, XPA, XPM, FGA, FGM, "2PA", "2PM", Sfty, 
                            KRTD, PRTD, INTD, FRTD, OPP_KRTD, OPP_PRTD, OPP_INTD, OPP_FRTD
                        ) VALUES ({', '.join(['?'] * len(row))})
                    """
                    self.cursor.execute(query, row)
                    if i % self.cache == 0:
                        self.conn.commit()
                        self.conn.execute("BEGIN TRANSACTION")
        
        self.conn.commit()
    


    def add_into_db(self, row: list, values: list, args: list):
        game_id, team_id, year, _type, league, version, insert_key = args.values()
        stats = [int(row[PLAYER_ID]), game_id, team_id, _type, year, league, version]
        for key, val in values.items():
            if val is None or row[val] == '':
                stats.append(0)
            elif "grade" in key:
                stats.append(float(row[val]))
            else:
                try:
                    if "avg_depth_of_target" in key:
                        new_value = int(round(float(row[val]) * int(row[val - 2]), 0))
                        stats.append(new_value)
                    elif "depth_of_target" in key:
                        stats.append(float(row[val]))
                    else: 
                        stats.append(int(row[val]))
                except Exception as e:
                    print(key)
                    print(row[val])
                    raise f"There was an issue formatting {key} for val {row[val]}. ERROR: {e}"
        
        self.insert_query(insert_key, stats)



    def insert_query(self, key: str, result: list):
        res = ', '.join(['?'] * len(result))
        query = INSERT_TABLE[key]
        query = query.format(start=INSERT_START, result=res)
        self.cursor.execute(query, result)
    


    def insert_values(self, version: str, start_year: int = 2006, end_year: int = 2024):
        records_processed = 0
        self.create_tables()
        
        start_time = time.time()
        for year in range(start_year, end_year + 1):
            for league in ["NFL"]: #, "NCAA"]:
                for info in self.INFO:
                    csv_file = self.START_FILE.format(league=league, info=info, year=year)
                    print(f"On file: {csv_file}")

                    if not os.path.exists(csv_file):
                        print(f"File does not exist {csv_file}")
                        continue

                    with open(csv_file, "r") as c:
                        reader = csv.reader(c)
                        
                        # Begin transaction
                        self.conn.execute("BEGIN TRANSACTION")
                        
                        for row in reader:

                            if row[1] == "player":
                                continue

                            week = int(row[0])
                            team_name = row[4]
                            team_id = self.get_team_id(team_name)
                            game_id = self.get_game_id(year, week, team_id, version)

                            player_id = row[2]
                            player_name = row[1]
                            pos = row[3]
                            self.insert_player(player_id, player_name, pos)
                            
                            args = {"game_id": game_id, "team_id": team_id, "year": year, "type": None, "league": league, "version": version, "key": None}
                            if info == "Passing":
                                args["type"], args["key"] = "passing", "passing"
                                self.add_into_db(row, PASSING, args)

                            elif info == "Passing_Depth":
                                for depth in PASSING_DEPTH:
                                    for area in PASSING_DEPTH[depth]:
                                        args["type"], args["key"] = f"{depth.lower()}_{area.lower()}", "passing"
                                        self.add_into_db(row, PASSING_DEPTH[depth][area], args)

                            elif info == "Passing_Pressure":
                                for pre in PASSING_PRESSURE:
                                    args["type"], args["key"] = pre.lower(), "passing"
                                    self.add_into_db(row, PASSING_PRESSURE[pre], args)

                            elif info == "Receiving":
                                args["type"], args["key"] = "receiving", "receiving"
                                self.add_into_db(row, RECEIVING, args)

                            elif info == "Receiving_Depth":
                                for depth in RECEIVING_DEPTH:
                                    for area in RECEIVING_DEPTH[depth]:
                                        args["type"], args["key"] = f"{depth.lower()}_{area.lower()}", "receiving"
                                        self.add_into_db(row, RECEIVING_DEPTH[depth][area], args)

                            elif info == "Receiving_Scheme":
                                for scheme in RECEIVING_SCHEME:
                                    args["type"], args["key"] = scheme.lower(), "receiving"
                                    self.add_into_db(row, RECEIVING_SCHEME[scheme], args)

                            elif info == "Rushing":
                                args["type"], args["key"] = "rushing", "rushing"
                                self.add_into_db(row, RUSHING, args)
                            
                            elif info == "Blocking":
                                args["type"], args["key"] = "blocking", "blocking"
                                self.add_into_db(row, BLOCKING, args)
                            
                            elif info == "Pass_Blocking": 
                                args["type"], args["key"] = "pass_blocking", "pass_blocking"
                                self.add_into_db(row, PASS_BLOCKING, args)
                            
                            elif info == "Run_Blocking":
                                args["type"], args["key"] = "run_blocking", "run_blocking"
                                self.add_into_db(row, RUN_BLOCKING, args)

                            records_processed += 1
                            
                            # Commit in batches
                            if records_processed % self.cache == 0:
                                self.conn.commit()
                                self.conn.execute("BEGIN TRANSACTION")
                        
                        # Commit any remaining changes
                        self.conn.commit()

        end_time = time.time()
        print(f"Time taken: {end_time - start_time} seconds")
        self.kill()    


if __name__ == "__main__":
    db = DB()
    db.insert_values('0.0')