from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class StartMatchSchema(BaseModel):
    team_a_name: str
    team_b_name: str
    composition_a: list[int]
    composition_b: list[int]
    chat_id: int


class RecordEventSchema(BaseModel):
    player_number: int
    team_id: int
    action_type: str
    result: str
    timestamp: datetime | None = None


class CompleteMatchSchema(BaseModel):
    winner: int | None = None


class MatchResponse(BaseModel):
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

    class Config:
        from_attributes = True


class MatchStateResponse(BaseModel):
    match_id: UUID
    status: str
    current_set: int
    score_a: int
    score_b: int
    rotation_a: int
    rotation_b: int
    changes: list[str]


class MatchResultResponse(BaseModel):
    match_id: UUID
    winner: int
    total_sets: int
    set_scores: list[tuple[int, int]]
    team_a_name: str
    team_b_name: str
