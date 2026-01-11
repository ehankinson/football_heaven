"""CSV-to-SQLite ingestion utilities for Football Heaven.

This module loads team, game, and player statistic CSVs and inserts them into the
SQLite database used by the project. It includes batching/caching for performance
and normalizes certain source quirks (e.g., playoff week codes).
"""

import os
import csv
import time
import re

from queries import INSERT_START, CREATE_INDEXES, CREATE_TABLE, INSERT_TABLE
from const import (
    normalize_week,
    LEAGUES,
    STAT_TYPES,
    LEAGUE_YEARS,
    PASSING,
    PASSING_DEPTH,
    PASSING_PRESSURE,
    RECEIVING_,
    RECEIVING_DEPTH,
    RECEIVING_SCHEME,
    RUSHING,
    BLOCKING,
    PASS_BLOCKING,
    RUN_BLOCKING,
    PASS_RUSH,
    RUN_DEFENSE,
    COVERAGE,
    COVERAGE_SCHEME,
)

# Maps stat_type to its list of expected column names
STAT_TYPE_KEYS: dict[str, list[str]] = {
    "passing": PASSING,
    "passing-depth": PASSING_DEPTH,
    "passing-pressure": PASSING_PRESSURE,
    "passing-concept": [],  # Placeholder
    "receiving": RECEIVING_,
    "receiving-depth": RECEIVING_DEPTH,
    "receiving-scheme": RECEIVING_SCHEME,
    "rushing": RUSHING,
    "offense-blocking": BLOCKING,
    "offense-pass-blocking": PASS_BLOCKING,
    "offense-run-blocking": RUN_BLOCKING,
    "defense-pass-rush": PASS_RUSH,
    "defense-run": RUN_DEFENSE,
    "defense-coverage": COVERAGE,
    "defense-coverage-scheme": COVERAGE_SCHEME,
}

# Stat types that have prefixed columns and need grouped insertion
# Maps stat_type -> (base_keys_list, insert_key)
GROUPED_STAT_TYPES: dict[str, tuple[list[str], str]] = {
    "passing-depth": (PASSING, "passing"),
    "passing-pressure": (PASSING, "passing"),
    "receiving-depth": (RECEIVING_, "receiving"),
    "receiving-scheme": (RECEIVING_, "receiving"),
    "defense-coverage-scheme": (COVERAGE, "coverage"),
}

# Maps stat_type to INSERT_TABLE key (for simple stat types)
STAT_TYPE_TO_INSERT_KEY: dict[str, str] = {
    "passing": "passing",
    "receiving": "receiving",
    "rushing": "rushing",
    "offense-blocking": "blocking",
    "offense-pass-blocking": "pass_blocking",
    "offense-run-blocking": "run_blocking",
    "defense-pass-rush": "pass_rush",
    "defense-run": "run_defense",
    "defense-coverage": "coverage",
}

from db import Database

RK_INDEX = 0
PLAYER_ID = 2
TEAM_NAME_INDEX = 0
GAME_YEAR_INDEX = 1
GAME_WEEK_INDEX = 2
AT_SYMBOL_INDEX = 4
NCAA_2PA_INDEX = 14
OPPONENT_NAME_INDEX = 3

START_FILE = "csv/{league}/{league}-{year}-{stat_type}.csv"


class Insert:
    """Handles bulk insertion of football statistics into the database.
    
    Manages the insertion of teams, games, and player statistics from CSV files
    into the database. Uses caching to optimize repeated lookups and batched
    transactions for performance. Supports multiple stat types including passing,
    receiving, rushing, blocking, defense, and coverage statistics.
    
    Dynamically builds column index mappings from CSV headers, allowing the code
    to handle files where column order varies between weeks/years.

    Attributes:
        db: Database instance for executing queries
        cache: Batch size for transaction commits (default: 100,000)
        _team_id_cache: Cache for team name to team ID lookups
        _game_id_cache: Cache for game ID lookups
    """

    def __init__(self) -> None:
        self.db = Database()
        self.cache = 100_000
        self._team_id_cache: dict[str, int | None] = {}
        self._game_id_cache: dict[tuple[int, int, int, str], int | None] = {}



    @staticmethod
    def _normalize_week(week: int, *, is_pff_data: bool = True) -> int:
        """Normalize week numbering to be human-friendly.

        Args:
            week: The week number from the source data.
            is_pff_data: If True (default), applies PFF-specific adjustment for
                playoff weeks. Set to False for games CSV data.
        """
        return normalize_week(week, is_pff_data=is_pff_data)



    @staticmethod
    def _build_index_mapping(headers: list[str], keys: list[str]) -> dict[str, int | None]:
        """Build a mapping from column names to their indices in the header row.

        Args:
            headers: The header row from the CSV file
            keys: List of column names we want to find

        Returns:
            Dictionary mapping column names to their index (or None if not found)
        """
        header_to_idx = {h.lower(): i for i, h in enumerate(headers)}
        return {key: header_to_idx.get(key.lower()) for key in keys}



    def _insert_with_mapping(
        self,
        row: list[str],
        base_args: dict,
        *,
        db_type: str,
        insert_key: str,
        mapping: dict[str, int | None],
    ) -> None:
        """Set stat metadata and insert one stat mapping into the DB."""
        base_args["type"] = db_type
        base_args["key"] = insert_key
        self.add_into_db(row, mapping, base_args)

    @staticmethod
    def _group_keys_by_prefix(
        index_mapping: dict[str, int | None],
        base_keys: list[str],
    ) -> dict[str, dict[str, int | None]]:
        """Group index mapping keys by their prefix.

        For depth/scheme stats, keys have prefixes like "center_behind_los_",
        "left_deep_", "blitz_", "man_", etc. This groups them so we can
        insert each group with the appropriate type.

        Args:
            index_mapping: The full {column_name: index} mapping
            base_keys: Base stat names without prefixes (e.g., ["aimed_passes", "attempts", ...])

        Returns:
            Dict mapping prefix -> {column_name: index} for that prefix's columns
        """
        grouped: dict[str, dict[str, int | None]] = {}

        for key, idx in index_mapping.items():
            # Find which base key this column name ends with
            prefix = key
            for base in base_keys:
                if key.endswith(base) or key.endswith(base.replace("_", "")):
                    # Extract the prefix (everything before the base stat name)
                    prefix = key[: len(key) - len(base)].rstrip("_")
                    break

            if prefix not in grouped:
                grouped[prefix] = {}
            grouped[prefix][key] = idx

        return grouped



    def _get_team_id(self, team_name: str) -> int | None:
        """Return cached Team_ID for a team, or None if unknown."""
        if team_name not in self._team_id_cache:
            self._team_id_cache[team_name] = self.db.get_team_id(team_name)
        return self._team_id_cache[team_name]



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
        year: int,
        league: str,
        stat_type: str,
        version: str,
        row: list[str],
        index_mapping: dict[str, int | None],
    ) -> None:
        """Process one CSV row and insert associated player + stat records.

        Args:
            year: The year of the data
            league: NFL or NCAA
            stat_type: The type of stat (e.g., "passing", "rushing")
            version: Version identifier for the data
            row: The CSV row data
            index_mapping: Mapping from column names to their indices in this row
        """
        week = self._normalize_week(int(row[0]))
        team_id = self._get_team_id(row[4])
        if team_id is None:
            # Unknown team - skip this row
            return

        game_id = self._get_game_id(year=year, week=week, team_id=team_id, version=version)
        if game_id is None:
            # Bye week / cumulative snapshot row: no corresponding game to attach stats to.
            return

        player_id = self._parse_player_id(row[2])
        # Avoid per-row commits; the surrounding transaction handles batching.
        self.db.insert_player(player_id, row[1], row[3], commit=False)

        base_args = {
            "game_id": game_id,
            "team_id": team_id,
            "year": year,
            "type": None,
            "league": league,
            "version": version,
            "key": None,
        }

        # Check if this is a grouped stat type (depth/scheme stats)
        if stat_type in GROUPED_STAT_TYPES:
            base_keys, insert_key = GROUPED_STAT_TYPES[stat_type]
            grouped = self._group_keys_by_prefix(index_mapping, base_keys)

            for prefix, group_mapping in grouped.items():
                # Use the prefix as the db_type (e.g., "center_behind_los", "blitz", "man")
                args = base_args.copy()
                self._insert_with_mapping(
                    row,
                    args,
                    db_type=prefix,
                    insert_key=insert_key,
                    mapping=group_mapping,
                )
        else:
            # Simple stat type - map to INSERT_TABLE keys
            insert_key = STAT_TYPE_TO_INSERT_KEY.get(stat_type, stat_type.replace("-", "_"))

            self._insert_with_mapping(
                row,
                base_args,
                db_type=stat_type.replace("-", "_"),
                insert_key=insert_key,
                mapping=index_mapping,
            )



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

        leagues = {"NFL": "csv/NFL/nfl_games.csv", "NCAA": "csv/NCAA/ncaa_games.csv"}
        for _, (league, fil) in enumerate(leagues.items()):
            with open(fil, "r", encoding="utf-8") as c:
                reader = csv.reader(c)
                for row in reader:
                    if "Rk" in row[0]:
                        continue

                    row.pop(AT_SYMBOL_INDEX) # removing the "@" or empty space
                    row.pop(RK_INDEX) # removing the Rk column

                    if league == "NFL":
                        # Games CSV uses standard week numbering (not PFF's offset)
                        row[GAME_WEEK_INDEX] = str(self._normalize_week(
                            int(row[GAME_WEEK_INDEX]),
                            is_pff_data=False,
                        ))
                        row.extend(['0'] * 4)
                    else:
                        row.insert(NCAA_2PA_INDEX, row[NCAA_2PA_INDEX])

                    team_id = self.db.get_team_id(row[TEAM_NAME_INDEX].strip())
                    opp_id = self.db.get_team_id(row[OPPONENT_NAME_INDEX].strip())

                    if opp_id is None:
                        opp_id = -1
                    if team_id is None:
                        team_id = -1

                    row[TEAM_NAME_INDEX] = str(team_id)
                    row[OPPONENT_NAME_INDEX] = str(opp_id)

                    # Convert all available values to integers
                    row = [str(int(r)) if r not in {'', None} else '0' for r in row]

                    # Prepend GAME_ID to row
                    row = [str(next_game_id), "0.0"] + row
                    next_game_id += 1

                    query = f"""
                        INSERT OR IGNORE INTO GAME_DATA (
                            GAME_ID, Version, Team_ID, Year, Week, Opponent_ID, Points_For, Points_Against, Diff,
                            TD, XPA, XPM, FGA, FGM, "2PA", "2PM", Sfty, 
                            KRTD, PRTD, INTD, FRTD, OPP_KRTD, OPP_PRTD, OPP_INTD, OPP_FRTD
                        ) VALUES ({', '.join(['?'] * len(row))})
                    """
                    self.db.cursor.execute(query, row)

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



    def insert_values(self):
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
            NFL league and all stat types defined in stat_type.
        """
        records_processed = 0
        self.db.create_tables(CREATE_TABLE, CREATE_INDEXES)
        self.insert_teams()
        self.insert_games()
        self._team_id_cache.clear()
        self._game_id_cache.clear()

        start_time = time.time()
        for league in LEAGUES:
            start_year = LEAGUE_YEARS[league]["start_year"]
            end_year = LEAGUE_YEARS[league]["end_year"]
            for year in range(start_year, end_year + 1):
                for stat_type in STAT_TYPES:
                    csv_file = START_FILE.format(league=league, stat_type=stat_type, year=year)
                    print(f"On file: {csv_file}")

                    if not os.path.exists(csv_file):
                        print(f"File does not exist {csv_file}")
                        continue

                    with open(csv_file, "r", encoding="utf-8") as c:
                        reader = csv.reader(c)

                        # Begin transaction
                        self.db.conn.execute("BEGIN TRANSACTION")

                        # Get the expected keys for this stat type
                        keys = STAT_TYPE_KEYS.get(stat_type, [])
                        index_mapping: dict[str, int | None] = {}

                        for row in reader:
                            # Check if this is a header row (contains "week" in first column)
                            if "week" in row[0].lower():
                                # Build index mapping from this header row
                                index_mapping = self._build_index_mapping(row, keys)
                                continue  # Skip header row, don't process as data

                            # Skip rows if we haven't seen a header yet
                            if not index_mapping:
                                continue

                            try:
                                self._process_stat_row(
                                    year=year,
                                    league=league,
                                    stat_type=stat_type,
                                    version="0.0",
                                    row=row,
                                    index_mapping=index_mapping,
                                )
                                records_processed += 1
                            except (ValueError, IndexError, KeyError):
                                # Skip rows with issues (unknown team, missing data, etc.)
                                continue

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
    insert = Insert()
    insert.insert_values()
