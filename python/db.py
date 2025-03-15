import csv
import time
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
    


    def kill(self) -> None:
        self.conn.close()
    


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



    def get_game_id(self, year: int, week: int, team_id: int) -> int:
        self.cursor.execute("SELECT Game_ID FROM GAME_DATA WHERE Year = ? AND Week = ? and Team_ID = ?", (year, week, team_id))
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

    

    def insert_game(self, game_id: int, team_id: int, year: int, week: int, opponent_id: int, location: str) -> None:
        query = """
            INSERT OR IGNORE INTO GAME_DATA (Game_ID, Team_ID, Year, Week, Opponent_ID, Location)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (game_id, team_id, year, week, opponent_id, location))
        self.conn.commit()
    


    def _add_into_passing(self, row: list, values: list, game_id: int, team_id: int, year: int, _type: str):
        stats = [int(row[2]), game_id, team_id, _type, year]

        for key, val in values.items():
            if key == "avg_depth_of_target":
                if row[val] == '':
                    stats.append(0)
                    continue

                new_value = int(round(float(row[val]) * int(row[val - 2]), 0))
                stats.append(new_value)
            elif key == "grade_pass":
                stats.append(float(row[val]))
            else:
                stats.append(int(row[val]))

        query = """
            INSERT INTO PASSING (
                Player_ID, Game_ID, Team_ID, Type, Year, aimed_passes, attempts, avg_depth_of_target,
                bats, big_time_throws, completions, dropbacks, drops, first_downs, hit_as_threw, 
                interceptions, passing_snaps, penalties, sacks, scrambles, spikes, thrown_aways, 
                touchdowns, turnover_worthy_plays, yards, grade_pass
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        self.cursor.execute(query, (stats))
        self.conn.commit()
        


    def insert_passing(self, row: list, year: int, week: int, team: str, passing: str) -> None:
        team_id = self.get_team_id(team)
        game_id = self.get_game_id(year, week, team_id)

        if passing == "PASSING":
            self._add_into_passing(row, PASSING, game_id, team_id, year, "passing")
        elif passing == "PASSING_DEPTh":
            for depth in PASSING_DEPTH:
                for area in PASSING_DEPTH[depth]:
                    self._add_into_passing(row, PASSING_DEPTH[depth][area], game_id, team_id, year, f"{depth.lower()}_{area.lower()}")
        else:
            for pre in PASSING_PRESSURE:
                self._add_into_passing(row, PASSING_PRESSURE[pre], game_id, team_id, year, pre.lower())
    


    def insert_game_data(self) -> None:
        with open("csv/games.csv", "r") as c:
            reader = csv.reader(c)
            for i, row in enumerate(reader):

                if row[1] == 'Year':
                    continue

                team_id = self.get_team_id(row[0])
                year = int(row[1])
                week = int(row[2])
                opp_id = self.get_team_id(row[3])

                location = row[4]
                self.insert_game(i + 1, team_id, year, week, opp_id, location)



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
                        self.insert_player(player_id, player_name, pos)
                        self.insert_team(team_name)
                        
                        
                        if info == "Passing":
                            self.insert_passing(row, year, week, team_name, "PASSING")
                        # elif info == "Passing_Depth":
                        #     self.insert_passing_depth(row, year, week, team_name, "PASSING_DEPTH")
                        # elif info == "Passing_Pressure":
                        #     self.insert_passing_pressure(row, year, week, team_name, "PASSING_PRESSURE")

        self.kill()
    


    def print_table_columns(self, table_name: str) -> None:
        query = f"PRAGMA table_info({table_name})"
        self.cursor.execute(query)
        columns = self.cursor.fetchall()
        
        print(f"\nColumns in {table_name}:")
        for col in columns:
            # col contains: (id, name, type, notnull, default_value, pk)
            print(f"- {col[1]} ({col[2]})")
    


    def sum_team_stats(self, team: str, year: int, start_week: int = None, end_week: int = None, in_games: list[int] = None):
        team_id = self.get_team_id(team)
        base_query = """
        SELECT 
            COUNT(DISTINCT GAME_DATA.Game_ID), 
            SUM(aimed_passes), SUM(attempts), SUM(avg_depth_of_target), SUM(bats),
            SUM(big_time_throws), SUM(completions), SUM(dropbacks), SUM(drops),
            SUM(first_downs), SUM(hit_as_threw), SUM(interceptions), SUM(passing_snaps),
            SUM(penalties), SUM(sacks), SUM(scrambles), SUM(spikes), SUM(thrown_aways),
            SUM(touchdowns), SUM(turnover_worthy_plays), SUM(yards), SUM(grade_pass)
        FROM PASSING
        JOIN GAME_DATA ON PASSING.Game_ID = GAME_DATA.Game_ID
        WHERE PASSING.Team_ID = ? 
        AND GAME_DATA.Year = ?
        """

        params = [team_id, year]

        if start_week is not None:
            base_query += " AND GAME_DATA.Week >= ?"
            params.append(start_week)

        if end_week is not None:
            base_query += " AND GAME_DATA.Week <= ?"
            params.append(end_week + 1)

        if in_games:  # If a specific list of weeks is provided
            placeholders = ", ".join("?" for _ in in_games)
            base_query += f" AND GAME_DATA.Week IN ({placeholders})"
            params.extend(in_games)
        start_time = time.time()
        self.cursor.execute(base_query, tuple(params))
        result = self.cursor.fetchone()
        end_time = time.time()
        print(f"The query time took {end_time - start_time}")
        
        return result



if __name__ == "__main__":
    db = DB()
    start_year = 2006
    end_year = 2025

    # db.print_table_columns("PASSING")
    # db.insert_values(start_year, end_year)
    team = "NO"
    year = 2018
    sw = 1
    ew = 16
    stats = db.sum_team_stats(team, year, sw, ew)
    print(stats)
    db.kill()
