
from typing import Any, cast
from dataclasses import dataclass

from converter import Converter
from query_args import QueryArgs
from prettytable import PrettyTable
from queries import get_query, game_data_query

from db import Database

OPP = True
ASC = False
DESC = True
TEAM = False
TOTAL = True
PLAYER = True
DISPLAY = True
OFFENSE = True
DEFENSE = False
PER_GAME = True
STATS = {
    "passing": False,
    "rushing": False,
    "receiving": False,
    "blocking": False,
    "pass_blocking": False,
    "run_blocking": False,
    "pass_rush": True,
    "run_defense": True,
    "coverage": True,
    "game_data": False
}


@dataclass(frozen=True, slots=True)
class SeasonStatsOptions:
    """Options to control season stats query/display behavior."""

    display: bool = False
    order: bool = False
    by_game: bool = False
    opp: bool = False
    valid_stats: bool = True
    order_key: str | None = None



class GetStats:
    """Retrieves and processes football statistics from the database.
    
    Provides methods to query player and team statistics, calculate fantasy points,
    compute SPRS (Statistical Performance Rating System) scores, and format results
    for display. Supports multiple stat types including passing, receiving, rushing,
    blocking, pass rush, run defense, and coverage statistics.
    
    Attributes:
        db: Database instance for executing queries
        converter: Converter instance for transforming query results
        start_header: Base column headers for output tables
        headers: Dictionary mapping stat types to their column headers
        max_key: Dictionary mapping stat types to their primary metric key
    """

    def __init__(self) -> None:
        self.db = Database()
        self.converter = Converter()
        self.start_header = ["Pick", "Year", "VERSION", "TEAM", "POS", "GP"]
        self.headers = {
            'passing': [
                'snaps', 'db', 'cmp', 'aim', 'att', 'yds', 'adot', 'td', 'int', '1d',
                'btt', 'twp', 'drp', 'bat', 'hat', 'ta', 'spk', 'sk', 'scrm', 'pen',
                'PASS', 'FP', 'SPRS'
            ],
            'receiving': [
                'snaps', 'wide', 'slot', 'in', 'rts', 'tgt', 'rec', 'yds', 'td', 'int',
                '1d', 'drp', 'ybc', 'yac', 'at', 'fum', 'ct', 'cr', 'pen', 'RECV',
                'ROUTE', 'FP', 'SPRS'
            ],
            'rushing': [
                'snaps', 'att', 'yds', 'td', 'fum', '1d', 'avd', 'exp', 'ybc', 'yac',
                'b_att', 'b_yds', 'des_yds', 'gap_att', 'zone_att', 'scrm', 'scrm_yds',
                'pen', 'RUN', 'FUM', 'FP', 'SPRS'
            ],
            'blocking': [
                'snaps', 'p_snaps', 'r_snaps', 'lt_snaps', 'lg_snaps', 'ce_snaps',
                'rg_snaps', 'rt_snaps', 'te_snaps', 'pen', 'PASS_BLOCK', 'RUN_BLOCK',
                'FP', 'SPRS'
            ],
            'pass_blocking': [
                'snaps', 'hur', 'hit', 'sk', 'pr', 'PASS_BLOCK', 't_snaps', 't_hur',
                't_hit', 't_sk', 't_pr', 'T_PASS_BLOCK', 'FP', 'SPRS'
            ],
            'run_blocking': [
                'snaps', 'gap_snaps', 'zone_snaps', 'pen', 'RUN_BLOCK', 'GAP_GRADES',
                'ZONE_GRADES', 'FP', 'SPRS'
            ],
            'pass_rush': [
                'snaps_pp', 'snaps_pr', 'hur', 'hit', 'sk', 'pr', 'pass_rush', 'win',
                'bat', 'pen', 'RUSH', 't_snaps_pp', 't_snaps_pr', 't_hur', 't_hit',
                't_sk', 't_pr', 't_pass_rush', 't_win', 't_bat', 'T_RUSH', 'FP', 'SPRS'
            ],
            'run_defense': [
                'snaps', 'com', 'tkl', 'ast', 'stp', 'adot', 'm_tkl', 'ff', 'pen',
                'RUN_DEF', 'TACK', 'FP', 'SPRS'
            ],
            'coverage': [
                'snaps', 'tgt', 'rec', 'yds', 'td', 'int', 'adot', 'ybc', 'yac', 'pbu',
                'fi', 'd_int', 'COV', 'FP', 'SPRS'
            ]
        }
        self.max_key = {
            "passing": "db",
            "receiving": "rts",
            "rushing": "att",
            "blocking": "snaps",
            "pass_blocking": "snaps",
            "run_blocking": "snaps",
            "pass_rush": "snaps_pr",
            "run_defense": "snaps",
            "coverage": "snaps"
        }



    def _calculate_fantasy_points(self, result: dict, stat: str, sub_stat: str | None = None) -> int:
        fp = 0
        stat_weights = None
        match stat:
            case "passing":
                stat_weights = {
                    "yds": 0.05, "td": 6, "int": -6, "1d": 0.5,
                    "btt": 3, "twp": -3, "sk": -1.5, "pen": -3
                }
            case "receiving":
                stat_weights = {
                    "rec": 0.5, "td": 6, "int": -6, "1d": 0.5, "drp": 3,
                    "ybc": 0.0875, "yac": 0.1625, "at": 2, "fum": -6, "cr": 0.5, "pen": -3
                }
            case "rushing":
                stat_weights = {
                    "td": 6, "fum": -6, "1d": 0.5, "avd": 0.75, "exp": 1.5,
                    "ybc": 0.0875, "yac": 0.1625, "pen": -3
                }
            case "pass_blocking":
                stat_weights = {
                    "hur": -0.25, "hit": -0.3125, "sk": -0.375, "pr": -0.1875,
                    "t_hur": -0.5, "t_hit": -0.625, "t_sk": -0.75, "t_pr": -0.375
                }
            case "pass_rush":
                stat_weights = {
                    "hur": 0.25, "hit": 0.3125, "sk": 0.375, "pr": 0.1875, "win": 0.4375,
                    "pen": -3, "t_hur": 0.5, "t_hit": 0.625, "t_sk": 0.75, "t_pr": 0.375,
                    "t_win": 0.875
                }
            case "run_defense":
                stat_weights = {
                    "tkl": 1.25, "ast": 0.75, "stop": 2.25, "m_tkl": -1, "ff": 3, "pen": -3
                }
            case "coverage":
                stat_weights = {
                    "rec": -0.5, "td": -6, "int": 6, "ybc": -0.0875, "yac": -0.1625,
                    "pbu": 3, "fi": 2.5, "d_int": 1.5
                }
            case "total":
                results = {
                    "passing": {"td": 6, "int": -6, "1d": 0.5, "btt": 3, "twp": -3, "pen": -3},
                    "rushing": {
                        "td": 6, "fum": -6, "1d": 0.5, "avd": 0.75, "exp": 1.5,
                        "ybc": 0.0875, "yac": 0.1625, "pen": -3
                    },
                    "receiving": {
                        "rec": 0.5, "drp": 3, "ybc": 0.0875, "yac": 0.1625, "at": 2,
                        "fum": -6, "cr": 0.5, "pen": -3
                    },
                    "pass_blocking": {
                        "hur": -0.25, "hit": -0.3125, "sk": -0.375, "pr": -0.1875,
                        "t_hur": -0.5, "t_hit": -0.625, "t_sk": -0.75, "t_pr": -0.375
                    },
                    "pass_rush": {"win": -0.4375, "pen": 3, "t_win": -0.875},
                    "run_defense": {
                        "tkl": -0.3125, "ast": -0.1875, "stp": -0.5625, "m_tkl": 0.125,
                        "ff": -0.75, "pen": 0.75
                    },
                    "coverage": {"pbu": -3, "fi": -2.5, "d_int": -1.5}
                }
                if sub_stat not in results:
                    return 0
                stat_weights = results[sub_stat]

        if stat_weights is not None:
            for stat_key, mul in stat_weights.items():
                fp += result[stat_key] * mul

        return fp



    def calculate_sprs(self, result: dict, stat_type: str, per_week: bool) -> float:
        """Calculate SPRS (Statistical Performance Rating System) score for a stat type.
        
        Computes a weighted composite score based on fantasy points per game and
        position-specific grade metrics. The weighting formula varies by stat type
        to reflect the relative importance of different performance aspects.
        
        Args:
            headers: List of column header names corresponding to results indices
            results: List of numeric values matching the headers order
            _type: Stat type identifier (e.g., 'passing', 'receiving', 'rushing')
            
        Returns:
            SPRS score rounded to 3 decimal places
            
        Raises:
            KeyError: If required header keys are missing from headers list
        """
        divisor = 1 if per_week else result["GP"]
        match stat_type:
            case "passing":
                fp_per_gp = result["FP"] / divisor
                grade = result["PASS"] if result["PASS"] is not None else 0
                return round(fp_per_gp * 0.45 + grade * 0.55, 3)
            case "receiving":
                fp_per_gp = result["FP"] / divisor
                recv = result["RECV"] if result["RECV"] is not None else 0
                route = result["ROUTE"] if result["ROUTE"] is not None else 0
                return round(fp_per_gp * 0.4 + recv * 0.5 + route * 0.1, 3)
            case "rushing":
                fp_per_gp = result["FP"] / divisor
                run = result["RUN"] if result["RUN"] is not None else 0
                fum = result["FUM"] if result["FUM"] is not None else 0
                return round(fp_per_gp * 0.4 + run * 0.5 + fum * 0.1, 3)
            case "blocking":
                if result["PASS_BLOCK"] is None:
                    result["PASS_BLOCK"] = 0

                if result["RUN_BLOCK"] is None:
                    result["RUN_BLOCK"] = 0

                pass_block = result["PASS_BLOCK"]
                run_block = result["RUN_BLOCK"]
                return round(pass_block * 0.55 + run_block * 0.45, 3)
            case "pass_blocking":
                if result["T_PASS_BLOCK"] is None:
                    result["T_PASS_BLOCK"] = 0

                fp_per_gp = result["FP"] / divisor
                pass_block = result["PASS_BLOCK"]
                t_pass_block = result["T_PASS_BLOCK"]
                return round(fp_per_gp * 0.4 + pass_block * 0.325 + t_pass_block * 0.275, 3)
            case "run_blocking":
                gap_pct = result["GAP_SNAPS"] / result["Snaps"]
                if result["GAP_GRADES"] is None:
                    result["GAP_GRADES"] = 0

                if result["ZONE_GRADES"] is None:
                    result["ZONE_GRADES"] = 0

                gap_grades = result["GAP_GRADES"]
                zone_grades = result["ZONE_GRADES"]
                return round(gap_grades * gap_pct + zone_grades * (1 - gap_pct), 3)
            case "pass_rush":
                if result["T_RUSH"] is None:
                    result["T_RUSH"] = 0
                return round(
                    (result["FP"] / divisor * 0.4)
                    + (result["T_RUSH"] * 0.25)
                    + (result["RUSH"] * 0.25),
                    3
                )
            case "run_defense":
                run_def = result["RUN_DEF"] if result["RUN_DEF"] is not None else 0
                tack = result["TACK"] if result["TACK"] is not None else 0
                return round(
                    (result["FP"] / divisor * 0.3)
                    + (run_def * 0.35)
                    + (tack * 0.35),
                    3
                )
            case "coverage":
                return round(result["FP"] / divisor * 0.35 + result["COV"] * 0.65, 3)
            case _:
                # Unknown stat type: default to 0.0 so all control paths return.
                return 0.0



    def _print_pretty_table(
        self,
        args: QueryArgs,
        headers: list[str],
        results: list[list],
        order: bool,
        sort_by: str | None = None,
    ) -> None:
        table = PrettyTable()
        table.field_names = headers

        if sort_by is not None and sort_by not in headers:
            raise ValueError(
                f"Sort by column '{sort_by}' not found in headers, "
                f"Please choose from: {headers}"
            )

        if sort_by is not None:
            results.sort(key=lambda x: x[headers.index(sort_by)], reverse=order)

        max_key = self.max_key[args.stat_type] if args.stat_type is not None else None
        if max_key is None:
            raise ValueError(f"Invalid stat type: {args.stat_type}")

        max_key_index = headers.index(max_key)
        max_value = max(x[max_key_index] for x in results)
        threshold = max_value * 0.25
        results = [x for x in results if x[max_key_index] >= threshold]

        limit = args.limit if args.limit is not None else None
        if limit is not None:
            results = results[:limit]

        table.add_rows(results)
        print(table)



    def season_stats(
        self,
        is_player: bool,
        args: QueryArgs,
        options: SeasonStatsOptions | None = None,
    ) -> list[dict[str, str | int | float | None]]:
        """Retrieve and optionally display season statistics for players or teams.

        Args:
            args: Query arguments (use `QueryArgs`; dicts are no longer supported here).
            is_player: Whether to retrieve player or team statistics.
            options: Optional container for the above flags (preferred for new call sites).

        Returns:
            List of dictionaries with statistics if display=False, otherwise list of lists
            with formatted results including fantasy points and SPRS scores.
        """
        opts = options or SeasonStatsOptions()
        opp = opts.opp
        order = opts.order
        display = opts.display
        by_game = opts.by_game
        order_key = opts.order_key if opts.order_key is not None else "SPRS"
        if args.stat_type is None:
            raise ValueError("QueryArgs.stat_type must be set")
        stat_type = args.stat_type

        query = get_query(args, is_player, by_game, opp)
        query_results = self.db.call_query(query)
        results = self.converter.convert_results(
            query_results, is_player, stat_type, by_game
        )

        if len(results) == 0:
            raise ValueError("No results found")

        if display:
            header = list(results[0].keys())

            final_results = []
            header.extend(['FP', 'SPRS'])
            for result in results:
                result['FP'] = round(self._calculate_fantasy_points(result, stat_type), 2)
                result['SPRS'] = round(self.calculate_sprs(result, stat_type, by_game), 3)

                final_results.append(list(result.values()))

            self._print_pretty_table(
                args,
                header,
                final_results,
                sort_by=order_key,
                order=order,
            )

        return results


    def game_data(
        self,
        args: QueryArgs,
        *,
        display: bool = False,
        order: bool = False,
        sort_by: str | None = None,
    ) -> list[dict[str, int | float | str | None]]:
        """Retrieve per-game GAME_DATA rows using the same filter inputs as QueryArgs.

        Notes:
        - Only these QueryArgs fields apply: start_week/end_week, start_year/end_year,
          version, team, limit.
        - stat_type/league/pos are ignored for GAME_DATA queries.
        """
        query = game_data_query(args)
        query_results = self.db.call_query(query)

        if len(query_results) == 0:
            raise ValueError("No results found")

        headers = [
            "team",
            "opponent",
            "year",
            "version",
            "week",
            "gp",
            "pts_for",
            "pts_against",
            "fgm",
            "fga",
            "xpm",
            "xpa",
        ]

        results: list[dict[str, int | float | str | None]] = [
            dict(zip(headers, row)) for row in query_results
        ]

        # Apply limit (mirrors season_stats behavior)
        if args.limit is not None:
            results = results[: args.limit]

        if display:
            table = PrettyTable()
            table.field_names = headers
            rows = [list(r.values()) for r in results]
            if sort_by is not None and sort_by not in headers:
                raise ValueError(
                    f"Sort by column '{sort_by}' not found in headers, "
                    f"Please choose from: {headers}"
                )
            if sort_by is not None:
                # Cast to Any so type-checkers don't require a total ordering across union types.
                rows.sort(
                    key=lambda x: cast(Any, x[headers.index(sort_by)]),
                    reverse=order,
                )
            table.add_rows(rows)
            print(table)

        return results



if __name__ == "__main__":
    ARGUMENTS = QueryArgs(
        start_week=1,
        end_week=18,
        start_year=2013,
        end_year=2013,
        stat_type="passing",
        league="NFL",
        version="0.0",
        pos=None,
        limit=30,
        team="DEN",
    )

    stats = GetStats()
    res = stats.season_stats(
        is_player=TEAM,
        args=ARGUMENTS,
        options=SeasonStatsOptions(display=True, by_game=True, order=ASC, order_key="GP"),
    )
