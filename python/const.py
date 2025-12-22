"""
Centralized constants module.

Going forward, prefer importing from `const` instead of `constants`.
`constants.py` is kept for compatibility and still contains the large constant maps.
"""

# Re-export existing constants to avoid breaking imports during the transition.
from constants import *  # noqa: F401,F403


# Common stat-type keys used by the simulation.
STAT_TYPES = [
    "passing",
    "rushing",
    "receiving",
    "blocking",
    "pass_blocking",
    "run_blocking",
    "pass_rush",
    "run_defense",
    "coverage",
]

# Week normalization
# Some source data encodes NFL playoffs as weeks 29-32. We normalize those to 19-22
# so the codebase has a single, intuitive week numbering scheme.
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


