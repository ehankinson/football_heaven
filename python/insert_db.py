import os
import csv
import time

from db import Database
from constants import *
from queries import INSERT_START, CREATE_TABLE, INSERT_TABLE

PLAYER_ID = 2



class Insert():

    def __init__(self) -> None:
        self.db = Database()
        self.cache = 100_000
        self.START_FILE = "csv/PFF_{league}_{info}_{year}.csv"
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
            "Coverage",
            "Coverage_Scheme",
            "Pass_Rush",
            "Run_Defence"
        ]
        self.TABLES = CREATE_TABLE



    def insert_teams(self) -> None:
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
                self.db.cursor.execute(query, (team_abbr, league, team_name, division, conference))

        self.db.conn.commit()



    def insert_games(self) -> None:
        # Get the next available GAME_ID
        self.db.cursor.execute("SELECT MAX(GAME_ID) FROM GAME_DATA")
        result = self.db.cursor.fetchone()
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

                    team_id = self.db.get_team_id(row[1].strip())
                    opp_id = self.db.get_team_id(row[4].strip())
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
                    self.db.cursor.execute(query, row)
                    if i % self.cache == 0:
                        self.db.conn.commit()
                        self.db.conn.execute("BEGIN TRANSACTION")
        
        self.db.conn.commit()



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
                    elif "depth_of_target" in ["depth_of_target", "avg_depth_of_tackle"]:
                        stats.append(float(row[val]))
                    else: 
                        stats.append(int(row[val]))
                except Exception as e:
                    print("\n")
                    print("#################################")
                    print("There was an error when inputing a value")
                    print(f"The key: {key}")
                    print(f"The value {row[val]}")
                    print("#################################")
                    print("\n")
                    raise f"There was an issue formatting {key} for val {row[val]}. ERROR: {e}"
        
        self.insert_query(insert_key, stats)



    def insert_query(self, key: str, result: list):
        res = ', '.join(['?'] * len(result))
        query = INSERT_TABLE[key]
        query = query.format(start=INSERT_START, result=res)
        self.db.cursor.execute(query, result)



    def insert_values(self, version: str, start_year: int = 2006, end_year: int = 2024):
        records_processed = 0
        self.db.create_tables(self.TABLES)
        self.insert_teams()
        self.insert_games()
        
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
                        self.db.conn.execute("BEGIN TRANSACTION")
                        
                        for i, row in enumerate(reader):

                            if row[1] == "player":
                                continue

                            week = int(row[0])
                            team_name = row[4]
                            team_id = self.db.get_team_id(team_name)
                            game_id = self.db.get_game_id(year, week, team_id, version)

                            player_id = row[2]
                            player_name = row[1]
                            pos = row[3]
                            self.db.insert_player(player_id, player_name, pos)
                            
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
                            
                            elif info == "Pass_Rush":
                                args["type"], args["key"] = "pass_rush", "pass_rush"
                                self.add_into_db(row, PASS_RUSH, args)

                            elif info == "Run_Defence":
                                args["type"], args["key"] = "run_defence", "run_defence"
                                self.add_into_db(row, RUN_DEFENCE, args)
                            
                            elif info == "Coverage": 
                                args["type"], args["key"] = "coverage", "coverage"
                                self.add_into_db(row, COVERAGE, args)
                                
                            elif info == "Coverage_Scheme":
                                for scheme in COVERAGE_SCHEME:
                                    args["type"], args["key"] = scheme.lower(), "coverage"
                                    self.add_into_db(row, COVERAGE_SCHEME[scheme], args)

                            records_processed += 1
                            
                            # Commit in batches
                            if records_processed % self.cache == 0:
                                self.db.conn.commit()
                                self.db.conn.execute("BEGIN TRANSACTION")
                        # Commit any remaining changes
                        self.db.conn.commit()

        end_time = time.time()
        print(f"Time taken: {end_time - start_time} seconds")
        self.db.kill()


if __name__ == '__main__':
    version = '0.0'
    insert = Insert()
    insert.insert_values(version)

