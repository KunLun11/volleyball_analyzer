from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.entities.matches import Match


@dataclass
class MatchDTO:
    id: UUID
    team_a_name: str
    team_b_name: str
    composition_a: list[int]
    composition_b: list[int]
    status: str
    created_at: datetime
    current_set: int
    score_a: int
    score_b: int

    @staticmethod
    def from_domain(match: Match) -> "MatchDTO":
        composition_a_list = [p.value for p in match.composition_a.get_players()]
        composition_b_list = [p.value for p in match.composition_b.get_players()]
        return MatchDTO(
            id=match.id.value,
            team_a_name=match.team_a_name.value,
            team_b_name=match.team_b_name.value,
            composition_a=composition_a_list,
            composition_b=composition_b_list,
            status=match.status.name,
            created_at=match.created_at,
            current_set=match.current_set.value,
            score_a=match.score.a.value,
            score_b=match.score.b.value,
        )


@dataclass
class MatchStateDTO:
    match_id: UUID
    status: str
    current_set: int
    score_a: int
    score_b: int
    rotation_a: int
    rotation_b: int
    changes: list[str]

    @staticmethod
    def from_domain(match: Match, changes: list[str]) -> "MatchStateDTO":
        return MatchStateDTO(
            match_id=match.id.value,
            status=match.status.name,
            current_set=match.current_set.value,
            score_a=match.score.a.value,
            score_b=match.score.b.value,
            rotation_a=match.rotation.team_a.value,
            rotation_b=match.rotation.team_b.value,
            changes=changes,
        )


@dataclass
class MatchResultDTO:
    match_id: UUID
    winner: int
    total_sets: int
    set_scores: list[tuple[int, int]]
    team_a_name: str
    team_b_name: str

    @staticmethod
    def from_domain(match: Match, winner: int) -> "MatchResultDTO":
        return MatchResultDTO(
            match_id=match.id.value,
            winner=winner,
            total_sets=len(match.set_scores),
            set_scores=[(s.a.value, s.b.value) for s in match.set_scores],
            team_a_name=match.team_a_name.value,
            team_b_name=match.team_b_name.value,
        )


@dataclass
class MatchEventDTO:
    timestamp: datetime
    player_id: int
    team_id: int
    action_type: str
    result: str
    rotation: int


@dataclass
class AdviceDTO:
    match_id: UUID
    advice: str
    generated_at: datetime
