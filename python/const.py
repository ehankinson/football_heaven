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


