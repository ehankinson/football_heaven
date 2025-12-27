from __future__ import annotations

from typing import Any

class Converter:

    def __init__(self) -> None:
        self.start_header = {
            "player": {
                "week": ["Player", "Year", "VERSION", "Team", "POS", "Week", "GP"],
                "season": ["Player", "Year", "VERSION", "Team", "POS", "GP"]
            },
            "team": {
                "week": ["Team", "Year", "VERSION", "Week", "GP"],
                "season": ["Team", "Year", "VERSION", "GP"]
            }
        }
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
                'snaps', 'com', 'tkl', 'ast', 'stop', 'adot', 'm_tkl', 'ff', 'pen',
                'RUN_DEF', 'TACK', 'FP', 'SPRS'
            ],
            'coverage': [
                'snaps', 'tgt', 'rec', 'yds', 'td', 'int', 'adot', 'ybc', 'yac', 'pbu',
                'fi', 'd_int', 'COV', 'FP', 'SPRS'
            ],
            'game_data': [
                'team', 'opponent', 'year', 'version', 'week', 'gp', 'pts_for', 'pts_against',
                'fgm', 'fga', 'xpm', 'xpa'
            ]
        }



    def convert_results(
        self,
        results: list[tuple[Any, ...]],
        is_player: bool,
        stat: str,
        by_game: bool,
    ) -> list[dict[Any, Any]]:
        """Convert query results to a list of dictionaries with appropriate headers.

        Args:
            results: List of tuples containing query results.
            is_player: Whether the results are for player or team statistics.
            stat: The statistic type (e.g., 'passing', 'receiving', 'rushing').
            by_game: Whether the results are by game/week or season totals.

        Returns:
            List of dictionaries where each dictionary maps header names to values.
        """
        game = "week" if by_game else "season"
        player = "player" if is_player else "team"
        header = self.start_header[player][game] + self.headers[stat]

        return [dict(zip(header, result)) for result in results]
