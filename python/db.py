import csv
import sqlite3

from constants import *



class DB():
    
    def __init__(self) -> None:
        self.START_FILE = "csv/PFF_{info}_{year}.csv"
        self.INFO = [
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
        self.conn = sqlite3.connect("db/football.db")
        self.cursor = self.conn.cursor()
    


    def end(self) -> None:
        self.conn.close()
    


    def delete_table_values(self, table_name: str):
        query = f"DELETE FROM {table_name}"
        self.cursor.execute(query)
        self.conn.commit()
    


    def drop_table(self, table_name: str):
        query = f"DROP TABLE IF EXISTS {table_name}"
        self.cursor.execute(query)
        self.conn.commit()
    


    def create_table(self, table_name: str):
        query = f"""
            CREATE TABLE {table_name} (
                Team_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Team_Name TEXT UNIQUE NOT NULL
            )                   
        """
        self.cursor.execute(query)
        self.conn.commit()



    def get_game_id(self, year: int, week: int, team: str) -> int:
        self.cursor.execute("SELECT Game_ID FROM GAME_DATA WHERE Year = ? AND Week = ? and Team = ?", (year, week, team))
        return self.cursor.fetchone()[0]



    def get_team_id(self, team: str) -> int:
        self.cursor.execute("SELECT Team_ID FROM TEAMS WHERE Team_Name = ?", (team,))
        result = self.cursor.fetchone()
        return result[0] if result is not None else None




    def insert_player(self, player_id: int, player_name: str, player_pos: str) -> None:
        query = """
            INSERT OR IGNORE INTO PLAYERS (Player_ID, Player_Name, Player_Pos)
            VALUES (?, ?, ?)
        """
        self.cursor.execute(query, (player_id, player_name, player_pos))
        self.conn.commit()
    


    def insert_team(self, team_name: str) -> None:
        # Get the next available Team_ID based on row count
        self.cursor.execute("SELECT COUNT(*) FROM TEAMS")
        row_count = self.cursor.fetchone()[0]
        next_team_id = row_count + 1  # Assign the next Team_ID

        # Insert the new team only if it doesn't already exist
        query = """
            INSERT OR IGNORE INTO TEAMS (Team_ID, Team_Name) VALUES (?, ?)
        """ 
        self.cursor.execute(query, (next_team_id, team_name))
        self.conn.commit()

    


    def insert_game(self, year: int, week: int, team_name: str) -> None:
        query = """
            INSERT OR IGNORE INTO GAME_DATA (Game_ID, Year, Week, Team)
            VALUES ((SELECT COALESCE(MAX(Game_ID), 0) + 1 FROM GAME_DATA), ?, ?, ?)
        """
        self.cursor.execute(query, (year, week, team_name))
        self.conn.commit()
    


    def _add_into_passing(self, row: list, values: list, game_id: int, team_id: int, _type: str):
        stats = [int(row[2]), game_id, team_id, _type]

        for i, val in enumerate(values.values()):
            if i != 2:
                stats.append(int(row[val]))
            else:
                if row[val] == '':
                    stats.append(0)
                    continue

                new_value = round(float(row[val]) * int(row[val - 2]), 0)
                stats.append(new_value)

        query = """
            INSERT INTO PASSING (Player_ID, Game_ID, Team_ID, Type, aimed_passes, attempts, avg_depth_of_target, bats, big_time_throws, completions, dropbacks, drops, first_downs, hit_as_threw, interceptions, passing_snaps, penalties, sacks, scrambles, spikes, thrown_aways, touchdowns, turnover_worthy_plays, yards)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (stats))
        self.conn.commit()
        


    def insert_passing(self, row: list, year: int, week: int, team: str):
        game_id = self.get_game_id(year, week, team)
        team_id = self.get_team_id(team)
        self._add_into_passing(row, PASSING, game_id, team_id, "passing")



    def insert_passing_depth(self, row: list, year: int, week: int, team: str):
        game_id = self.get_game_id(year, week, team)
        team_id = self.get_team_id(team)
        for depth in PASSING_DEPTH:
            for area in PASSING_DEPTH[depth]:
                self._add_into_passing(row, PASSING_DEPTH[depth][area], game_id, team_id, f"{depth.lower()}_{area.lower()}")
    


    def insert_passing_pressure(self, row: list, year: int, week: int, team: str):
        game_id = self.get_game_id(year, week, team)
        team_id = self.get_team_id(team)
        for pre in PASSING_PRESSURE:
            self._add_into_passing(row, PASSING_PRESSURE[pre], game_id, team_id, pre.lower())

    


    def insert_values(self, start_year: int, end_year: int):
        for year in range(start_year, end_year):
            for info in self.INFO:
                csv_file = self.START_FILE.format(info=info, year=year)

                with open(csv_file, "r") as c:
                    reader = csv.reader(c)

                    print(f"On file: {csv_file}")
                    
                    for row in reader:

                        if row[1] == "player":
                            continue

                        week = int(row[0])
                        team_name = row[4]
                        player_id = row[2]
                        player_name = row[1]
                        pos = row[3]
                        # self.insert_game(year, week, team_name)
                        # self.insert_player(player_id, player_name, pos)
                        # self.insert_team(team_name)
                        
                        if info == "Passing":
                            self.insert_passing(row, year, week, team_name)
                        # elif info == "Passing_Depth":
                        #     self.insert_passing_depth(row, year, week, team_name)
                        # elif info == "Passing_Pressure":
                            # self.insert_passing_pressure(row, year, week, team_name)

        self.end()
    


if __name__ == "__main__":
    db = DB()
    start_year = 2006
    end_year = 2025

    db.insert_values(start_year, end_year)
