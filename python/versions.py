from dataclasses import replace

from query_args import QueryArgs
from const import TEAM_ABR_TO_FULL
from get_stats import GetStats, SeasonStatsOptions
from queries import INSERT_START, INSERT_TABLE

TEAM = False
PLAYER = True
DESC = False

MAX_STAT = {
    "passing": "db"
}

UPDATE_FIELDS = {
    "passing": {
        "snaps": False,
        "db": False,
        "cmp": True,
        "aim": False,
        "att": False,
        "yds": True,
        "td": True,
        "int": False,
        "1d": True,
        "btt": True,
        "twp": False,
        "drp": False,
        "bat": False,
        "hat": False,
        "ta": False,
        "spk": False,
        "sk": False,
        "scrm": False,
        "pen": False,
        "PASS": True,
    }
}

class Versions:


    def __init__(self) -> None:
        self.stats = GetStats()
        self._player_id_cache: dict[tuple[str, str], int] = {}
        self.args = QueryArgs(
            start_week=1,
            end_week=22,
            start_year=None,
            end_year=None,
            stat_type=None,
            league=None,
            version=None,
            pos=None,
            limit=None,
            team=None
        )
        self.options = SeasonStatsOptions(display=False, by_game=True, order=DESC)



    def create_version_1_0(self) -> None:
        args = replace(
            self.args,
            start_year=2006,
            end_year=2024,
            stat_type="passing",
            league="NFL",
            version="0.0"
        )
        player_stats = self.quick_data(
            PLAYER,
            self.stats.season_stats(PLAYER, args, self.options)
        )
        team_stats = self.quick_data(
            TEAM,
            self.stats.season_stats(TEAM, args, self.options)
        )
        game_stats = self.quick_game_data(self.stats.game_data(args))

        new_stats = []

        for _, team, year, week, player_data in self.iter_player_team_year_week(player_stats):
            team_name = TEAM_ABR_TO_FULL[team]
            game_data = game_stats[team_name][year][week]
            team_data = team_stats[team_name][year][week]
            opp_data = team_stats[game_data["opponent"]][year][week]
            is_best = game_data["pts_for"] > game_data["pts_against"]
            new_team_data = self._update_team_stats(team_data, opp_data, is_best)
            self.update_player_stats(player_data, team_data, new_team_data)
            row = self._build_passing_row(
                player_data=player_data,
                team_abbr=team,
                year=year,
                week=week,
                from_version=str(args.version),
                to_version="1.0",
                league=str(args.league),
            )
            if row is not None:
                new_stats.append(row)
        
        self._insert_passing_rows(new_stats)
        
        



    def update_player_stats(
        self, player_stats: dict, team_stats: dict, new_team_stats: dict
    ) -> None:
        """Update player stats proportionally based on team stat changes.
        
        Calculates each player stat as a percentage of team totals, then applies
        that percentage to the new team stats. Modifies player_stats in place.
        """
        for stat in UPDATE_FIELDS["passing"]:
            if team_stats[stat] != 0:
                pct = player_stats[stat] / team_stats[stat]
            else:
                max_stat = MAX_STAT["passing"]
                pct = player_stats[max_stat] / team_stats[max_stat]

            val = pct * new_team_stats[stat]
            new_val = round(val, 1) if stat.isupper() else int(round(val, 0))

            player_stats[stat] = new_val



    def _get_player_id(self, player_name: str, player_pos: str) -> int:
        key = (player_name, player_pos)
        if key in self._player_id_cache:
            return self._player_id_cache[key]

        cur = self.stats.db.cursor
        cur.execute(
            "SELECT Player_ID FROM PLAYERS WHERE Player_Name = ? AND Player_Pos = ?",
            (player_name, player_pos),
        )
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"Player not found in PLAYERS: {player_name!r} ({player_pos!r})")

        self._player_id_cache[key] = int(row[0])
        return self._player_id_cache[key]


    def _build_passing_row(
        self,
        *,
        player_data: dict,
        team_abbr: str,
        year: int,
        week: int,
        from_version: str,
        to_version: str,
        league: str,
    ) -> list | None:
        """Build one PASSING row (VERSION=to_version) from a GetStats per-game record."""
        team_id = self.stats.db.get_team_id(team_abbr)
        if team_id is None:
            raise ValueError(f"Unknown team abbr: {team_abbr!r}")

        game_id = self.stats.db.get_game_id(year, week, team_id, from_version)
        if game_id is None:
            # Bye week / cumulative snapshot row.
            return None

        player_id = self._get_player_id(player_data["Player"], player_data["POS"])

        attempts = int(player_data["att"])
        adot = float(player_data["adot"])
        # DB stores total depth; GetStats reports average adot.
        total_adot = int(round(adot * attempts, 0)) if attempts else 0

        return [
            # INSERT_START fields
            player_id,
            game_id,
            team_id,
            "passing",  # TYPE
            year,
            league,
            to_version,
            # PASSING columns (matches PASSING_INSERT order in queries.py)
            int(player_data["aim"]),
            attempts,
            total_adot,
            int(player_data["bat"]),
            int(player_data["btt"]),
            int(player_data["cmp"]),
            int(player_data["db"]),
            int(player_data["drp"]),
            int(player_data["1d"]),
            int(player_data["hat"]),
            int(player_data["int"]),
            int(player_data["snaps"]),
            int(player_data["pen"]),
            int(player_data["sk"]),
            int(player_data["scrm"]),
            int(player_data["spk"]),
            int(player_data["ta"]),
            int(player_data["td"]),
            int(player_data["twp"]),
            int(player_data["yds"]),
            float(player_data["PASS"]),
        ]


    def _insert_passing_rows(self, rows: list[list]) -> None:
        """Bulk insert derived PASSING rows into the DB."""
        if not rows:
            return

        placeholders = ", ".join(["?"] * len(rows[0]))
        query = INSERT_TABLE["passing"].format(start=INSERT_START, result=placeholders)

        conn = self.stats.db.conn
        cur = self.stats.db.cursor
        conn.execute("BEGIN TRANSACTION")
        try:
            cur.executemany(query, rows)
            conn.commit()
        except Exception:
            conn.rollback()
            raise


    def _update_team_stats(self, team_stats: dict, opp_stats: dict, is_best: bool) -> dict:
        update_fields = UPDATE_FIELDS["passing"]
        if not is_best:
            update_fields = {k: not v for k, v in update_fields.items()}

        new_stats = {}
        for stat, value in update_fields.items():
            func = max if value else min
            new_val = func(team_stats[stat], opp_stats[stat])
            new_stats[stat] = new_val

        return new_stats



    @staticmethod
    def iter_player_team_year_week(player_stats: dict):
        """Yield flattened rows from `quick_data(is_player=True, ...)`.

        Produces: (player, team, year, week, record)
        """
        for player, team_data in player_stats.items():
            for team, year_data in team_data.items():
                for year, week_data in year_data.items():
                    for week, record in week_data.items():
                        yield player, team, year, week, record



    def _nest_by_keys(self, records: list[dict], keys: list[str]) -> dict:
        """Index a list of record dicts into a nested dict by an ordered list of keys.

        Example:
            keys=["team","year","week"] yields:
            out[team][year][week] = record

        If duplicates occur at the leaf, the first record wins (matches current behavior).
        """
        out: dict = {}
        for rec in records:
            node = out
            for k in keys[:-1]:
                v = rec[k]
                if v not in node:
                    node[v] = {}
                node = node[v]

            leaf_key = rec[keys[-1]]
            if leaf_key not in node:
                node[leaf_key] = rec
        return out



    def quick_data(self, is_player: bool, stats: list[dict[str, str | int | float | None]]) -> dict:
        """Nest season/week stats into a dict for fast lookup.

        Shapes:
        - is_player=True:  out[Player][Team][Year][Week] = record
        - is_player=False: out[Team][Year][Week] = record
        """
        if is_player:
            return self._nest_by_keys(stats, ["Player", "Team", "Year", "Week"])
        return self._nest_by_keys(stats, ["Team", "Year", "Week"])



    def quick_game_data(self, games: list[dict[str, str | int | float | None]]) -> dict:
        """Nest `GetStats.game_data(...)` results: out[team][year][week] = record."""
        return self._nest_by_keys(games, ["team", "year", "week"])


if __name__ == "__main__":
    versions = Versions()
    versions.create_version_1_0()