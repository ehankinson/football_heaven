import csv
import time
import sqlite3
from prettytable import PrettyTable

from constants import *



class DB():
    
    def __init__(self) -> None:
        self.START_FILE = "csv/PFF_{info}_{year}.csv"
        self.INFO = [
            "Passing",
            "Passing_Depth",
            "Passing_Pressure",
            "Receiving",
            "Receiving_Depth",
            "Receiving_Scheme",
            # # "Rushing",
            # # "Blocking_Pass",
            # # "Blocking_Rush",
            # # "Defense_Coverage",
            # # "Defense_Coverage_Scheme",
            # # "Defense_Pass_Rush",
            # # "Defense_Run_Defense"
        ]
        self.conn = sqlite3.connect("db/football.db")
        self.cursor = self.conn.cursor()
        
        # Add SQLite optimizations for bulk operations
        self.cursor.execute("PRAGMA synchronous = OFF")
        self.cursor.execute("PRAGMA journal_mode = MEMORY")
        self.cursor.execute("PRAGMA temp_store = MEMORY")
        self.cursor.execute("PRAGMA cache_size = 10000")
    


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
                try:
                    number = int(row[val])
                except:
                    if row[val] == '':
                        number = 0
                    else:
                        number = int(float(row[val]))
                stats.append(number)

        query = """
            INSERT INTO PASSING (
                Player_ID, Game_ID, Team_ID, Type, Year, aimed_passes, attempts, avg_depth_of_target,
                bats, big_time_throws, completions, dropbacks, drops, first_downs, hit_as_threw, 
                interceptions, passing_snaps, penalties, sacks, scrambles, spikes, thrown_aways, 
                touchdowns, turnover_worthy_plays, yards, grade_pass
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        self.cursor.execute(query, stats)
    


    def _add_into_receiving(self, row: list, values: list, game_id: int, team_id: int, year: int, _type: str):
        stats = [int(row[2]), game_id, team_id, _type, year]

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
                Player_ID, Game_ID, Team_ID, Type, Year, avoided_tackles, contested_reception,
                contested_targets, drops, first_downs, fumbles, inline_snaps, interceptions,
                penalties, receptions, routes, slot_snaps, targets, touchdowns, wide_snaps,
                yards, yards_after_catch, grades_hands_drop, grades_pass_route
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        self.cursor.execute(query, stats)



    def insert_passing(self, row: list, year: int, week: int, team: str, passing: str) -> None:
        team_id = self.get_team_id(team)
        try:
            game_id = self.get_game_id(year, week, team_id)
        except:
            print(f"Game ID not found for {team} ({team_id}) in {year} week {week}")
            return

        if passing == "PASSING":
            self._add_into_passing(row, PASSING, game_id, team_id, year, "passing")
        elif passing == "PASSING_DEPTH":
            for depth in PASSING_DEPTH:
                for area in PASSING_DEPTH[depth]:
                    self._add_into_passing(row, PASSING_DEPTH[depth][area], game_id, team_id, year, f"{depth.lower()}_{area.lower()}")
        else:
            for pre in PASSING_PRESSURE:
                self._add_into_passing(row, PASSING_PRESSURE[pre], game_id, team_id, year, pre.lower())
    


    def insert_receiving(self, row: list, year: int, week: int, team: str, receiving: str) -> None:
        team_id = self.get_team_id(team)
        try:
            game_id = self.get_game_id(year, week, team_id)
        except:
            print(f"Game ID not found for {team} ({team_id}) in {year} week {week}")
            return

        if receiving == "RECEIVING":
            self._add_into_receiving(row, RECEIVING, game_id, team_id, year, "receiving")
        elif receiving == "RECEIVING_DEPTH":
            for depth in RECEIVING_DEPTH:
                for area in RECEIVING_DEPTH[depth]:
                    self._add_into_receiving(row, RECEIVING_DEPTH[depth][area], game_id, team_id, year, f"{depth.lower()}_{area.lower()}")
        else:  # RECEIVING_SCHEME
            for scheme in RECEIVING_SCHEME:
                self._add_into_receiving(row, RECEIVING_SCHEME[scheme], game_id, team_id, year, scheme.lower())
    


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
        batch_size = 1_000  # Adjust based on your data size
        records_processed = 0
        
        for year in range(start_year, end_year):
            for info in self.INFO:
                csv_file = self.START_FILE.format(info=info, year=year)

                with open(csv_file, "r") as c:
                    reader = csv.reader(c)

                    print(f"On file: {csv_file}")
                    
                    # Begin transaction
                    self.conn.execute("BEGIN TRANSACTION")
                    
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
                        elif info == "Passing_Depth":
                            self.insert_passing(row, year, week, team_name, "PASSING_DEPTH")
                        elif info == "Passing_Pressure":
                            self.insert_passing(row, year, week, team_name, "PASSING_PRESSURE")
                        elif info == "Receiving":
                            self.insert_receiving(row, year, week, team_name, "RECEIVING")
                        elif info == "Receiving_Depth":
                            self.insert_receiving(row, year, week, team_name, "RECEIVING_DEPTH")
                        elif info == "Receiving_Scheme":
                            self.insert_receiving(row, year, week, team_name, "RECEIVING_SCHEME")
                        
                        records_processed += 1
                        
                        # Commit in batches
                        if records_processed % batch_size == 0:
                            self.conn.commit()
                            self.conn.execute("BEGIN TRANSACTION")
                    
                    # Commit any remaining changes
                    self.conn.commit()

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
    TABLE = "PASSING"
    start_week = 27
    end_week = 33
    query = f"""
        SELECT {TABLE}.* 
        FROM {TABLE}
        JOIN PLAYERS ON {TABLE}.Player_ID = PLAYERS.Player_ID
        JOIN GAME_DATA ON {TABLE}.Game_ID = GAME_DATA.Game_ID
        WHERE PLAYERS.Player_Pos = "QB" AND {TABLE}.Type = "passing"
        AND GAME_DATA.Week >= ? AND GAME_DATA.Week <= ?
    """
    db.cursor.execute(query, (start_week, end_week))
    results = db.cursor.fetchall()
    
    fun = {}
    
    for result in results:
        result = list(result)
        key = f"{result[0]}_{result[4]}"

        if key not in fun:
            fun[key] = []
        
        if len(fun[key]) == 0:
            fun[key] = result[5:]
            fun[key].insert(0, 1)
            continue
        
        total_db = result[11] + fun[key][6]
        fun_grade_pct = (fun[key][6] / total_db) * fun[key][-1]
        result_grade_pct = (result[11] / total_db) * result[-1]
        new_grade = fun_grade_pct + result_grade_pct
        
        length = len(result)
        fun[key][0] += 1

        for i in range(5, length):
            if i == length - 1:
                fun[key][-1] = new_grade
                continue
            
            fun[key][i - 4] += result[i]
        
    # adding score
    max_db = 0
    indexs = {4: -1, 5: 3, 9: 1.5, 10: -0.25, 11: -6, 13: -1, 17: 6, 18: 0.05}
    for player, stats in fun.items():
        max_db = max(max_db, stats[7])
        total_score = 0
        for index, score in indexs.items():
            total_score += stats[index] * score
        
        stats.append(total_score)
        stats.append((stats[-2] * 0.65) + ((stats[-1] / stats[0]) * 0.35))

    # sorting
    fun = dict(sorted(fun.items(), key=lambda x: x[1][-1], reverse=True))

    order = {"gp": 0, "db": 7, "cmp": 6, "aim": 1, "att": 2, "yds": 20, "td": 18, "int": 11, "1d": 9, "btt": 5, "twp": 19, "drp": 8, "bat": 4, "hat": 10, "ta": 17, "sk": 14, "pass": 21}
    # printing
    table = PrettyTable()
    table.field_names = ["Rank", "Name", "Year", "GP", "DB", "CMP", "AIM", "ATT", "YDS", "TD", "INT", "1D", "BTT", "TW", "DRP", "BAT", "HAT", "TA", "SK", "PASS", "FP", "SPRS"]
    
    total = 1000
    rank = 1
    for player, stats in fun.items():
        if not stats[7] > max_db * 0.25:
            continue

        total -= 1
        if total == 0:
            break
        
        display = []
        for i in order:
            display.append(stats[order[i]])

        display.append(stats[-2])
        display.append(stats[-1])

        query = "SELECT Player_Name FROM PLAYERS WHERE Player_ID = ?"
        split = player.split("_")
        player_id = split[0]
        year = split[1] 
        db.cursor.execute(query, (player_id,))
        player_name = db.cursor.fetchone()[0]
        
        # Format float values to have 2 decimal places
        formatted_display = []
        for value in display:
            if isinstance(value, float):
                formatted_display.append(f"{value:.2f}")
            else:
                formatted_display.append(value)
        
        # Add row to the table with rank
        table.add_row([rank, player_name, year] + formatted_display)
        rank += 1
    
    # Print the table
    table.align = "r"  # Right align all columns
    table.align["Name"] = "l"  # Left align Name column
    table.align["Rank"] = "r"  # Right align Rank column
    table.min_width["Rank"] = 4  # Set minimum width for rank column
    table.sortby = "SPRS"  # Sort by SPRS column
    table.reversesort = True  # Sort in descending order
    print(table)











    # start_year = 2006
    # end_year = 2024
    # db.delete_table_values("PASSING")
    # db.delete_table_values("RECEIVING")
    # print("Cleared Tables")
    # start_time = time.time()
    # db.insert_values(start_year, end_year + 1)        
    # end_time = time.time()
    # print(f"The query time took {end_time - start_time}")
    
    db.kill()
