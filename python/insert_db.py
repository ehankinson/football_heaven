"""CSV-to-SQLite ingestion utilities for Football Heaven.

This module loads team, game, and player statistic CSVs and inserts them into the
SQLite database used by the project. It includes batching/caching for performance
and normalizes certain source quirks (e.g., playoff week codes).
"""

import os
import csv
import time
from collections.abc import Callable

from queries import INSERT_START, CREATE_INDEXES, CREATE_TABLE, INSERT_TABLE
from const import (
    PASSING,
    RUSHING,
    BLOCKING,
    COVERAGE,
    RECEIVING,
    PASS_RUSH,
    RUN_DEFENSE,
    RUN_BLOCKING,
    PASS_BLOCKING,
    PASSING_DEPTH,
    COVERAGE_SCHEME,
    RECEIVING_DEPTH,
    PASSING_PRESSURE,
    RECEIVING_SCHEME,
    normalize_week,
)

from db import Database

PLAYER_ID = 2
TEAM_NAME_INDEX = 1
OPPONENT_NAME_INDEX = 4
GAME_YEAR_INDEX = 2
GAME_WEEK_INDEX = 3

START_FILE = "csv/PFF_{league}_{info}_{year}.csv"
INFO = [
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
    "Run_Defense"
]


class Insert:
    """Handles bulk insertion of football statistics into the database.
    
    Manages the insertion of teams, games, and player statistics from CSV files
    into the database. Uses caching to optimize repeated lookups and batched
    transactions for performance. Supports multiple stat types including passing,
    receiving, rushing, blocking, defense, and coverage statistics.
    
    Attributes:
        db: Database instance for executing queries
        cache: Batch size for transaction commits (default: 100,000)
        START_FILE: Template string for CSV file paths
        INFO: List of stat types to process
        TABLES: Dictionary of table creation queries
        _team_id_cache: Cache for team name to team ID lookups
        _game_id_cache: Cache for game ID lookups
        _handlers: Dispatch table mapping stat types to handler functions
    """

    def __init__(self) -> None:
        self.db = Database()
        self.cache = 100_000
        self._team_id_cache: dict[str, int | None] = {}
        self._game_id_cache: dict[tuple[int, int, int, str], int | None] = {}
        self._handlers: dict[str, Callable[[list[str], dict], None]] = self._build_handlers()

    @staticmethod
    def _normalize_week(week: int) -> int:
        """Normalize week numbering to be human-friendly."""
        return normalize_week(week)



    def _insert_mapping(
        self,
        row: list[str],
        base_args: dict,
        *,
        stat_type: str,
        key: str,
        mapping: dict,
    ) -> None:
        """Set stat metadata and insert one stat mapping into the DB."""
        base_args["type"] = stat_type
        base_args["key"] = key
        self.add_into_db(row, mapping, base_args)


    def _insert_nested(
        self,
        row: list[str],
        base_args: dict,
        *,
        key: str,
        nested: dict,
        type_fmt: str,
    ) -> None:
        """Insert nested stat mappings (e.g. depth/area breakdowns)."""
        for outer_key, inner in nested.items():
            for inner_key, mapping in inner.items():
                self._insert_mapping(
                    row,
                    base_args,
                    stat_type=type_fmt.format(
                        outer=outer_key.lower(),
                        inner=inner_key.lower(),
                    ),
                    key=key,
                    mapping=mapping,
                )


    def _build_handlers(self) -> dict[str, Callable[[list[str], dict], None]]:
        """Build handler dispatch for INFO stat types."""

        def handle_passing_pressure(row: list[str], a: dict) -> None:
            for pre, mapping in PASSING_PRESSURE.items():
                self._insert_mapping(
                    row, a, stat_type=pre.lower(), key="passing", mapping=mapping
                )

        def handle_receiving_scheme(row: list[str], a: dict) -> None:
            for scheme, mapping in RECEIVING_SCHEME.items():
                self._insert_mapping(
                    row, a, stat_type=scheme.lower(), key="receiving", mapping=mapping
                )

        def handle_coverage_scheme(row: list[str], a: dict) -> None:
            for scheme, mapping in COVERAGE_SCHEME.items():
                self._insert_mapping(
                    row, a, stat_type=scheme.lower(), key="coverage", mapping=mapping
                )

        return {
            "Passing": lambda row, a: self._insert_mapping(
                row, a, stat_type="passing", key="passing", mapping=PASSING
            ),
            "Passing_Depth": lambda row, a: self._insert_nested(
                row, a, key="passing", nested=PASSING_DEPTH, type_fmt="{outer}_{inner}"
            ),
            "Passing_Pressure": handle_passing_pressure,
            "Receiving": lambda row, a: self._insert_mapping(
                row, a, stat_type="receiving", key="receiving", mapping=RECEIVING
            ),
            "Receiving_Depth": lambda row, a: self._insert_nested(
                row, a, key="receiving", nested=RECEIVING_DEPTH, type_fmt="{outer}_{inner}"
            ),
            "Receiving_Scheme": handle_receiving_scheme,
            "Rushing": lambda row, a: self._insert_mapping(
                row, a, stat_type="rushing", key="rushing", mapping=RUSHING
            ),
            "Blocking": lambda row, a: self._insert_mapping(
                row, a, stat_type="blocking", key="blocking", mapping=BLOCKING
            ),
            "Pass_Blocking": lambda row, a: self._insert_mapping(
                row,
                a,
                stat_type="pass_blocking",
                key="pass_blocking",
                mapping=PASS_BLOCKING,
            ),
            "Run_Blocking": lambda row, a: self._insert_mapping(
                row,
                a,
                stat_type="run_blocking",
                key="run_blocking",
                mapping=RUN_BLOCKING,
            ),
            "Pass_Rush": lambda row, a: self._insert_mapping(
                row, a, stat_type="pass_rush", key="pass_rush", mapping=PASS_RUSH
            ),
            "Run_Defense": lambda row, a: self._insert_mapping(
                row, a, stat_type="run_defense", key="run_defense", mapping=RUN_DEFENSE
            ),
            "Coverage": lambda row, a: self._insert_mapping(
                row, a, stat_type="coverage", key="coverage", mapping=COVERAGE
            ),
            "Coverage_Scheme": handle_coverage_scheme,
        }


    def _get_team_id(self, team_name: str) -> int:
        """Return cached Team_ID for a team, raising if unknown."""
        if team_name not in self._team_id_cache:
            self._team_id_cache[team_name] = self.db.get_team_id(team_name)
        team_id = self._team_id_cache[team_name]
        if team_id is None:
            raise ValueError(f"Unknown team: {team_name!r}")
        return team_id


    def _get_game_id(self, *, year: int, week: int, team_id: int, version: str) -> int | None:
        """Return cached GAME_ID for (year, week, team_id, version).

        Notes:
            Some PFF player stat files include bye-week rows (cumulative snapshots)
            where a team has no game for that week. In that case there is no
            matching GAME_DATA row, and this returns None.
        """
        game_key = (year, week, team_id, version)
        if game_key not in self._game_id_cache:
            self._game_id_cache[game_key] = self.db.get_game_id(year, week, team_id, version)
        return self._game_id_cache[game_key]


    def _parse_player_id(self, raw_player_id: str) -> int:
        """Parse player_id from CSV."""
        try:
            return int(raw_player_id)
        except ValueError as e:
            raise ValueError(f"Invalid player_id: {raw_player_id!r}") from e


    def _process_stat_row(
        self,
        *,
        year: int,
        league: str,
        info: str,
        version: str,
        row: list[str],
    ) -> None:
        """Process one CSV row and insert associated player + stat records."""
        if row[1] == "player":
            return

        week = self._normalize_week(int(row[0]))
        team_id = self._get_team_id(row[4])
        game_id = self._get_game_id(year=year, week=week, team_id=team_id, version=version)
        if game_id is None:
            # Bye week / cumulative snapshot row: no corresponding game to attach stats to.
            return

        player_id = self._parse_player_id(row[2])
        # Avoid per-row commits; the surrounding transaction handles batching.
        self.db.insert_player(player_id, row[1], row[3], commit=False)

        args = {
            "game_id": game_id,
            "team_id": team_id,
            "year": year,
            "type": None,
            "league": league,
            "version": version,
            "key": None,
        }
        try:
            handler = self._handlers[info]
        except KeyError as e:
            raise ValueError(f"Unhandled info type: {info}") from e
        handler(row, args)


    def insert_teams(self) -> None:
        """Insert team data from CSV file into the TEAMS database table.
        
        Reads team information from csv/teams.csv and inserts records into the
        TEAMS table. Skips header rows and uses INSERT OR IGNORE to avoid
        duplicate entries.
        """
        with open("csv/teams.csv", "r", encoding="utf-8") as c:
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
        """Insert game data from CSV files into the GAME_DATA database table.
        
        Reads game statistics from CSV files (currently NFL games) and inserts them
        into the GAME_DATA table. Processes team names to team IDs, converts values
        to integers, and assigns sequential GAME_IDs. Uses batched commits for
        performance optimization.
        """
        # Get the next available GAME_ID
        self.db.cursor.execute("SELECT MAX(GAME_ID) FROM GAME_DATA")
        result = self.db.cursor.fetchone()
        next_game_id = 1 if result[0] is None else result[0] + 1

        leagues = {"NFL": "csv/nfl_games.csv"} #, "NCAA": "csv/ncaa_games.csv"}
        for i, (league, fil) in enumerate(leagues.items()):
            with open(fil, "r", encoding="utf-8") as c:
                reader = csv.reader(c)
                for row in reader:
                    if row[2] == "Team":
                        continue

                    if league == "NCAA":
                        row.insert(14, row[14])

                    row.pop(5)
                    row.pop(1)

                    team_id = self.db.get_team_id(row[TEAM_NAME_INDEX].strip())
                    opp_id = self.db.get_team_id(row[OPPONENT_NAME_INDEX].strip())
                    row[TEAM_NAME_INDEX] = str(team_id)
                    row[OPPONENT_NAME_INDEX] = str(opp_id)
                    # Normalize playoff week encoding (29-32) to sequential weeks (19-22).
                    row[GAME_WEEK_INDEX] = str(self._normalize_week(int(row[GAME_WEEK_INDEX])))

                    # Convert all available values to integers
                    for i, r in enumerate(row):
                        if not i:
                            continue

                        row[i] = str(int(r)) if r not in {'', None} else '0'

                    if league == "NFL":
                        row += ['0'] * 4

                    # Prepend GAME_ID to row
                    row = [str(next_game_id)] + row
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



    def add_into_db(self, row: list, values: dict, args: dict):
        """Process and insert player statistics into the database.
        
        Extracts game and player context from args, processes statistical values
        from the row data according to the values mapping, and inserts the formatted
        data into the appropriate database table.
        
        Args:
            row: List containing player/stat data from CSV row
            values: Dictionary mapping stat keys to column indices in row
            args: Dictionary containing game_id, team_id, year, type, league, version, insert_key
            
        Raises:
            Exception: If there's an error formatting a value during processing
        """
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
                    raise ValueError(
                        f"There was an issue formatting {key} for val {row[val]}. ERROR: {e}"
                    ) from e

        self.insert_query(insert_key, stats)



    def insert_query(self, key: str, result: list):
        """Execute an INSERT query for the specified table with the given values.
        
        Formats an INSERT query using the table name from INSERT_TABLE[key],
        creates parameter placeholders for all values, and executes the query
        with the provided result list.
        
        Args:
            key: Key that maps to a table name in INSERT_TABLE
            result: List of values to insert into the table
        """
        res = ', '.join(['?'] * len(result))
        query = INSERT_TABLE[key]
        query = query.format(start=INSERT_START, result=res)
        self.db.cursor.execute(query, result)



    def insert_values(self, stat_versions: list[str], start_year: int = 2006, end_year: int = 2024):
        """Insert all player statistics from CSV files into the database.
        
        Main entry point for bulk data insertion. Creates tables, inserts teams and games,
        then processes player statistics from CSV files for the specified year range.
        Handles multiple stat types including passing, receiving, rushing, blocking,
        pass rush, run defense, and coverage statistics with their various breakdowns.
        
        Args:
            version: Version identifier for the data (e.g., '0.0')
            start_year: First year to process (default: 2006)
            end_year: Last year to process (default: 2024)
            
        Note:
            Uses batched commits for performance optimization. Processes files for
            NFL league and all stat types defined in INFO.
        """
        records_processed = 0
        self.db.create_tables(CREATE_TABLE, CREATE_INDEXES)
        self.insert_teams()
        self.insert_games()
        self._team_id_cache.clear()
        self._game_id_cache.clear()

        start_time = time.time()
        for version in stat_versions:
            if version != "0.0":
                continue

            for year in range(start_year, end_year + 1):
                for league in ["NFL"]:  # , "NCAA"]:
                    for info in INFO:
                        csv_file = START_FILE.format(league=league, info=info, year=year)
                        print(f"On file: {csv_file}")

                        if not os.path.exists(csv_file):
                            print(f"File does not exist {csv_file}")
                            continue

                        with open(csv_file, "r", encoding="utf-8") as c:
                            reader = csv.reader(c)

                            # Begin transaction
                            self.db.conn.execute("BEGIN TRANSACTION")

                            for row in reader:
                                self._process_stat_row(
                                    year=year,
                                    league=league,
                                    info=info,
                                    version=version,
                                    row=row,
                                )

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
    versions = ["0.0", "0.1", "1.0", "1.1"]
    insert = Insert()
    insert.insert_values(versions)
