import sqlite3

class Database():
    
    def __init__(self) -> None:
        self.conn = sqlite3.connect("db/football.db")
        self.cursor = self.conn.cursor()
        # Add SQLite optimizations for bulk operations
        self.cursor.execute("PRAGMA synchronous = OFF")
        self.cursor.execute("PRAGMA journal_mode = MEMORY")
        self.cursor.execute("PRAGMA temp_store = MEMORY")
        self.cursor.execute(f"PRAGMA cache_size = {100_000}")
        # Set maximum file size to 2GB (assuming 4KB page size)
        self.cursor.execute("PRAGMA max_page_count = 524288")  # 2GB = 2 * 1024 * 1024 * 1024 / 4096



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
    


    def create_tables(self, tables: dict):
        for name, query in tables.items():
            self.drop_table(name)
            self.create_table(query)