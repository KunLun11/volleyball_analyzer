from dataclasses import dataclass, field
from datetime import datetime

from app.domain.enums import MatchStatusEnum, ResultEnum
from app.domain.events import (
    DomainEvent,
    MatchCompleted,
    MatchStarted,
    PointScored,
    SetCompleted,
)
from app.domain.utils import now
from app.domain.values.composites import MatchEvent, Rotation, Score, TeamComposition
from app.domain.values.identifiers import ChatID, MatchID
from app.domain.values.primitives import (
    RotationPosition,
    ScoreValue,
    SetNumber,
    TeamName,
)


@dataclass
class Match:
    id: MatchID

    status: MatchStatusEnum
    created_at: datetime
    updated_at: datetime

    team_a_name: TeamName
    team_b_name: TeamName
    composition_a: TeamComposition
    composition_b: TeamComposition

    current_set: SetNumber
    score: Score
    rotation: Rotation
    chat_id: ChatID
    
    set_scores: list[Score] = field(default_factory=list, repr=False)
    _events: list[MatchEvent] = field(default_factory=list, repr=False)
    _domain_events: list[DomainEvent] = field(default_factory=list, repr=False)

    @property
    def domain_events(self) -> list[DomainEvent]:
        return self._domain_events.copy()

    def clear_domain_events(self) -> None:
        self._domain_events.clear()

    @classmethod
    def start(
        cls,
        team_a: TeamName,
        team_b: TeamName,
        composition_a: TeamComposition,
        composition_b: TeamComposition,
        chat_id: ChatID,
    ) -> "Match":
        match_id = MatchID.generate()
        status = MatchStatusEnum.LIVE
        score = Score(a=ScoreValue(0), b=ScoreValue(0))
        set_scores = []
        rotation = Rotation(team_a=RotationPosition(1), team_b=RotationPosition(1))
        _events = []
        _domain_events = []
        instance = cls(
            id=match_id,
            created_at=now(),
            updated_at=now(),
            status=status,
            team_a_name=team_a,
            team_b_name=team_b,
            composition_a=composition_a,
            composition_b=composition_b,
            current_set=SetNumber(1),
            score=score,
            set_scores=set_scores,
            rotation=rotation,
            chat_id=chat_id,
            _events=_events,
            _domain_events=_domain_events,
        )
        match_started = MatchStarted(
            match_id=match_id,
            team_a=team_a,
            team_b=team_b,
            occurred_at=now(),
        )
        instance._domain_events.append(match_started)
        return instance

    def record_event(self, event: MatchEvent):
        if self.status != MatchStatusEnum.LIVE:
            raise RuntimeError(f"Cannot record event: match status is {self.status}")
        self._events.append(event)
        if event.result == ResultEnum.SCORED:
            self.score = self.score.increment(event.team_id)
            self.updated_at = now()
            point_scored = PointScored(
                match_id=self.id,
                team_id=event.team_id,
                new_score_a=self.score.a,
                new_score_b=self.score.b,
                current_set=self.current_set,
                occurred_at=now(),
            )
            self._domain_events.append(point_scored)
        is_won, winner = self.score.is_set_won()
        if is_won:
            self.set_scores.append(self.score)

            set_completed = SetCompleted(
                match_id=self.id,
                set_number=self.current_set,
                winner=winner,
                final_score_a=self.score.a,
                final_score_b=self.score.b,
                occurred_at=now(),
            )
            self._domain_events.append(set_completed)

            sets_won_a = 0
            sets_won_b = 0
            for set_score in self.set_scores:
                if set_score.a > set_score.b:
                    sets_won_a += 1
                else:
                    sets_won_b += 1

            if sets_won_a >= 3 or sets_won_b >= 3:
                winner = 1 if sets_won_a > sets_won_b else 2
                self.complete(winner)
            else:
                self.current_set = SetNumber(self.current_set.value + 1)
                self.score = Score(a=ScoreValue(0), b=ScoreValue(0))
                rotation = self.rotation.next(1).next(2)
                self.rotation = rotation
                self.updated_at = now()

    def complete(self, winner: int | None = None) -> None:
        if self.status != MatchStatusEnum.LIVE:
            raise RuntimeError(f"Cannot record event: match status is {self.status}")
        if winner is None:
            sets_won_a = 0
            sets_won_b = 0
            for set_score in self.set_scores:
                if set_score.a > set_score.b:
                    sets_won_a += 1
                else:
                    sets_won_b += 1

            if sets_won_a >= 3 or sets_won_b >= 3:
                winner = 1 if sets_won_a > sets_won_b else 2
            else:
                raise RuntimeError("Cannot determine winner: match not finished")
        self.status = MatchStatusEnum.COMPLETED
        self.updated_at = now()

        match_completed = MatchCompleted(
            match_id=self.id,
            winner=winner,
            total_sets=len(self.set_scores),
            final_set_scores=[
                (set_score.a.value, set_score.b.value) for set_score in self.set_scores
            ],
            occurred_at=now(),
        )
        self._domain_events.append(match_completed)
        return


__all__ = [
    "Match",
]
