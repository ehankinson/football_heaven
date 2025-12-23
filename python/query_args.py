from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class QueryArgs:
    """Typed container for common query arguments used to build SQL filters."""

    start_week: int | None = None
    end_week: int | None = None
    start_year: int | None = None
    end_year: int | None = None
    stat_type: str | None = None
    league: str | None = None
    version: Any | None = None
    pos: list[str] | None = None
    limit: int | None = None
    team: str | None = None

    @classmethod
    def from_mapping(cls, args: Mapping[str, Any]) -> QueryArgs:
        """Create a `QueryArgs` from an existing mapping (e.g., the current args dict)."""
        return cls(
            start_week=args.get("start_week"),
            end_week=args.get("end_week"),
            start_year=args.get("start_year"),
            end_year=args.get("end_year"),
            stat_type=args.get("stat_type"),
            league=args.get("league"),
            version=args.get("version"),
            pos=args.get("pos"),
            limit=args.get("limit"),
            team=args.get("team"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert back to the legacy dict shape expected elsewhere in the codebase."""
        return {
            "start_week": self.start_week,
            "end_week": self.end_week,
            "start_year": self.start_year,
            "end_year": self.end_year,
            "stat_type": self.stat_type,
            "league": self.league,
            "version": self.version,
            "pos": self.pos,
            "limit": self.limit,
            "team": self.team,
        }


