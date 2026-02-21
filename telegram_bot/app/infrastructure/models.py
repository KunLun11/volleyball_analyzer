from dataclasses import dataclass
from typing import Any


@dataclass
class RabbitMQMessage:
    correlation_id: str
    action: str
    payload: dict
    reply_to: str
    timestamp: str

    @classmethod
    def from_dict(cls, data: dict) -> "RabbitMQMessage":
        return cls(
            correlation_id=data["correlation_id"],
            action=data["action"],
            payload=data["payload"],
            reply_to=data["reply_to"],
            timestamp=data["timestamp"],
        )

    def to_dict(self) -> dict:
        return {
            "correlation_id": self.correlation_id,
            "action": self.action,
            "payload": self.payload,
            "reply_to": self.reply_to,
            "timestamp": self.timestamp,
        }


@dataclass
class AdviceResponse:
    correlation_id: str
    advice: str
    match_id: str
    chat_id: int
    timestamp: str

    @classmethod
    def from_dict(cls, data: dict) -> "AdviceResponse":
        return cls(
            correlation_id=data["correlation_id"],
            advice=data["advice"],
            match_id=data["match_id"],
            chat_id=data["chat_id"],
            timestamp=data["timestamp"],
        )


@dataclass
class MatchResponse:
    correlation_id: str
    match: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict) -> "MatchResponse":
        return cls(
            correlation_id=data["correlation_id"],
            match=data["match"],
        )


@dataclass
class LiveMatchesResponse:
    correlation_id: str
    matches: list[dict[str, Any]]

    @classmethod
    def from_dict(cls, data: dict) -> "LiveMatchesResponse":
        return cls(
            correlation_id=data["correlation_id"],
            matches=data["matches"],
        )


@dataclass
class EventResponse:
    correlation_id: str
    match_state: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict) -> "EventResponse":
        return cls(
            correlation_id=data["correlation_id"],
            match_state=data["match_state"],
        )


@dataclass
class CompleteMatchResponse:
    correlation_id: str
    result: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict) -> "CompleteMatchResponse":
        return cls(
            correlation_id=data["correlation_id"],
            result=data["result"],
        )
