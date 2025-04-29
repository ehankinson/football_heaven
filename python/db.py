import os
import csv
import time
import sqlite3

from tqdm import tqdm
from constants import *
from queries import GAME_DATA, TEAMS, CREATE_PASSING, CREATE_PLAYERS

MAP = [
    'passing',
    'receiving',
    'players',
    'teams',
    'game_data',
]

class DB():
    
    def __init__(self) -> None:
        self.START_FILE = "csv/PFF_{league}_{info}_{year}.csv"
        self.cache = 100_000
        self.INFO = [
            "Passing",
            "Passing_Depth",
            "Passing_Pressure",
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
        self.conn = sqlite3.connect("db/football.db")
        self.cursor = self.conn.cursor()
        
        # Add SQLite optimizations for bulk operations
        self.cursor.execute("PRAGMA synchronous = OFF")
        self.cursor.execute("PRAGMA journal_mode = MEMORY")
        self.cursor.execute("PRAGMA temp_store = MEMORY")
        self.cursor.execute(f"PRAGMA cache_size = {self.cache}")
    


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
    


    def _add_into_passing(self, row: list, values: list, game_id: int, team_id: int, year: int, _type: str, league: str, version: str):
        stats = [int(row[2]), game_id, team_id, _type, year, league, version]

        for key, val in values.items():
            if "avg_depth_of_target" in key:
                if row[val] == '':
                    stats.append(0)
                    continue

                new_value = int(round(float(row[val]) * int(row[val - 2]), 0))
                stats.append(new_value)
            elif "grades_pass" in key or "grade_pass" in key:
                if row[val] == '':
                    stats.append(0)
                    continue

                stats.append(float(row[val]))
            else:
                if val is None:
                    stats.append(0)
                    continue

                try:
                    number = int(row[val])
                except:
                    if row[val] == '':
                        number = 0
                    else:
                        number = int(float(row[val]))

                stats.append(number)

        self.quick_add_passing(stats)
    


    def quick_add_passing(self, result: list):
        query = f"""
            INSERT OR IGNORE INTO PASSING (
                Player_ID, Game_ID, Team_ID, TYPE, YEAR, LEAGUE, VERSION, aimed_passes, attempts, avg_depth_of_target,
                bats, big_time_throws, completions, dropbacks, drops, first_downs, hit_as_threw, 
                interceptions, passing_snaps, penalties, sacks, scrambles, spikes, thrown_aways, 
                touchdowns, turnover_worthy_plays, yards, grade_pass
            ) 
            VALUES ({', '.join(['?'] * len(result))});
        """
        self.cursor.execute(query, result)



    def _add_into_receiving(self, row: list, values: list, game_id: int, team_id: int, year: int, _type: str, league: str):
        stats = [int(row[2]), game_id, team_id, _type, year, league]

        for key, val in values.items():

            if val is None:
                val = 0

            if "depth_of_target" in key:
                if row[val] == '':
                    stats.append(0)
                    continue

                stats.append(float(row[val]))
            elif "grades_hands_drop" in key or "grades_pass_route" in key:
                if row[val] == '':
                    stats.append(0)
                    continue

                stats.append(float(row[val]))
            else:
                try:
                    number = int(row[val])
                except:
                    if row[val] == '':
                        number = 0
                    else:
                        number = int(float(row[val]))
                stats.append(number)

        query = """
            INSERT INTO RECEIVING (
                Player_ID, Game_ID, Team_ID, Type, Year, League, avoided_tackles, contested_reception,
                contested_targets, drops, first_downs, fumbles, inline_snaps, interceptions,
                penalties, receptions, routes, slot_snaps, targets, touchdowns, wide_snaps,
                yards, yards_after_catch, grades_hands_drop, grades_pass_route
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        self.cursor.execute(query, stats)



    def insert_passing(self, row: list, year: int, week: int, team_id: int, passing: str, league: str, version: str) -> None:
        game_id = self.get_game_id(year, week, team_id, version)
        if game_id is None:
            return

        if passing == "PASSING":
            self._add_into_passing(row, PASSING, game_id, team_id, year, "passing", league, version)
        elif passing == "PASSING_DEPTH":
            for depth in PASSING_DEPTH:
                for area in PASSING_DEPTH[depth]:
                    self._add_into_passing(row, PASSING_DEPTH[depth][area], game_id, team_id, year, f"{depth.lower()}_{area.lower()}", league, version)
        else:
            for pre in PASSING_PRESSURE:
                self._add_into_passing(row, PASSING_PRESSURE[pre], game_id, team_id, year, pre.lower(), league, version)
    


    def insert_receiving(self, row: list, year: int, week: int, team: str, receiving: str, league: str, version: str) -> None:
        team_id = self.get_team_id(team)
        try:
            game_id = self.get_game_id(year, week, team_id, version)
        except:
            print(f"Game ID not found for {team} ({team_id}) in {year} week {week}")
            return

        if receiving == "RECEIVING":
            self._add_into_receiving(row, RECEIVING, game_id, team_id, year, "receiving", league)
        elif receiving == "RECEIVING_DEPTH":
            for depth in RECEIVING_DEPTH:
                for area in RECEIVING_DEPTH[depth]:
                    self._add_into_receiving(row, RECEIVING_DEPTH[depth][area], game_id, team_id, year, f"{depth.lower()}_{area.lower()}", league)
        else:  # RECEIVING_SCHEME
            for scheme in RECEIVING_SCHEME:
                
                self._add_into_receiving(row, RECEIVING_SCHEME[scheme], game_id, team_id, year, scheme.lower(), league)
    


    def insert_values(self, version: str, start_year: int = 2006, end_year: int = 2024):
        records_processed = 0
        self.drop_table("PASSING")
        self.create_table(CREATE_PASSING)
        
        start_time = time.time()
        for year in range(start_year, end_year + 1):
            for league in ["NFL"]: #, "NCAA"]:
                for info in self.INFO:
                    csv_file = self.START_FILE.format(league=league, info=info, year=year)

                    if not os.path.exists(csv_file):
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

                            player_id = row[2]
                            player_name = row[1]
                            pos = row[3]
                            self.insert_player(player_id, player_name, pos)
                            
                            
                            if info == "Passing":
                                self.insert_passing(row, year, week, team_id, "PASSING", league, version)
                            elif info == "Passing_Depth":
                                self.insert_passing(row, year, week, team_id, "PASSING_DEPTH", league, version)
                            elif info == "Passing_Pressure":
                                self.insert_passing(row, year, week, team_id, "PASSING_PRESSURE", league, version)
                            elif info == "Receiving":
                                self.insert_receiving(row, year, week, team_id, "RECEIVING", league, version)
                            elif info == "Receiving_Depth":
                                self.insert_receiving(row, year, week, team_id, "RECEIVING_DEPTH", league, version)
                            elif info == "Receiving_Scheme":
                                self.insert_receiving(row, year, week, team_id, "RECEIVING_SCHEME", league, version)
                            
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
    # db.create_table(CREATE_PLAYERS)
    # db.insert_teams()
    db.insert_games()
    db.drop_table("PASSING")
    # db.insert_values("0.0")