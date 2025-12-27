"""
Centralized csv_reader module.

Going forward, prefer importing from `const` instead of `csv_reader`.
`csv_reader.py` is kept for compatibility and still contains the large constant maps.
"""


# Re-export existing csv_reader to avoid breaking imports during the transition.
from datetime import datetime

END_YEAR = datetime.today().year
LEAGUES = ["NFL", "NCAA"]
NCAA_WEEKS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
NFL_WEEKS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 28, 29, 30, 32]
PFF_LINK = "https://premium.pff.com/{league}/positions/{year}/SINGLE/{stat_type}?week={week}"
NCAA_ADD_ON = "&division=fbs,fcs,lower"

LEAGUE_YEARS = {
    "NFL": {
        "start_year": 2012,
        "end_year": END_YEAR
    },
    "NCAA": {
        "start_year": 2014,
        "end_year": END_YEAR
    }
}

PFF_STAT_NAME = [
    "passing",
    "passing-depth",
    "passing-pressure",
    "passing-concept",
    "receiving",
    "receiving-depth",
    "receiving-scheme",
    "rushing",
    "offense-blocking",
    "offense-pass-blocking",
    "offense-run-blocking",
    "defense-pass-rush",
    "defense-run",
    "defense-coverage",
    "defense-coverage-scheme"

]

STAT_TYPES = [
    "passing",
    "passing_depth",
    "passing_pressure",
    "passing_concept",
    "rushing",
    "receiving",
    "receiving_depth",
    "receiving_scheme",
    "blocking",
    "pass_blocking",
    "run_blocking",
    "pass_rush",
    "run_defense",
    "coverage",
    "coverage_scheme"
]

TEAM_ABR_TO_FULL = {
    "ARZ": "Arizona Cardinals",
    "ATL": "Atlanta Falcons",
    "BLT": "Baltimore Ravens",
    "BUF": "Buffalo Bills",
    "CAR": "Carolina Panthers",
    "CHI": "Chicago Bears",
    "CIN": "Cincinnati Bengals",
    "CLV": "Cleveland Browns",
    "DAL": "Dallas Cowboys",
    "DEN": "Denver Broncos",
    "DET": "Detroit Lions",
    "GB": "Green Bay Packers",
    "HST": "Houston Texans",
    "IND": "Indianapolis Colts",
    "JAX": "Jacksonville Jaguars",
    "KC": "Kansas City Chiefs",
    "LA": "Los Angeles Rams",
    "LAC": "Los Angeles Chargers",
    "LV": "Las Vegas Raiders",
    "MIA": "Miami Dolphins",
    "MIN": "Minnesota Vikings",
    "NE": "New England Patriots",
    "NO": "New Orleans Saints",
    "NYG": "New York Giants",
    "NYJ": "New York Jets",
    "OAK": "Oakland Raiders",
    "PHI": "Philadelphia Eagles",
    "PIT": "Pittsburgh Steelers",
    "SF": "San Francisco 49ers",
    "SEA": "Seattle Seawhawks",
    "SD": "San Diego Chargers",
    "SL": "St. Louis Rams",
    "TB": "Tampa Bay Buccaneers",
    "TEN": "Tennessee Titans",
    "WAS": "Washington Redskins"
}

PLAYOFF_WEEK_CODE_START = 29
PLAYOFF_WEEK_CODE_END = 32
PLAYOFF_WEEK_NORMALIZED_START = 19


def normalize_week(week: int) -> int:
    """Normalize week numbering to a single, human-friendly scheme.

    - Regular season weeks remain unchanged (1-18).
    - Playoff week codes 29-32 are remapped to 19-22.
    """
    if week >= PLAYOFF_WEEK_CODE_START:
        return PLAYOFF_WEEK_NORMALIZED_START + (week - PLAYOFF_WEEK_CODE_START)
    return week
