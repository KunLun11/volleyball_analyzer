from datetime import datetime
from uuid import UUID


_storage: dict[int, dict] = {}


def get_active_match(chat_id: int) -> dict | None:
    if chat_id not in _storage:
        return None
    match_info = _storage[chat_id]
    if match_info.get("status") == "COMPLETED":
        return None
    return match_info


def set_active_match(chat_id: int, match_id: UUID, message_id: int) -> None:
    match_info = {}
    match_info["match_id"] = str(match_id)
    match_info["status"] = "LIVE"
    match_info["message_id"] = message_id
    match_info["created_at"] = datetime.now()
    _storage[chat_id] = match_info


def update_message_id(chat_id: int, message_id: int) -> None:
    if chat_id in _storage:
        _storage[chat_id]["message_id"] = message_id


def complete_match(chat_id: int) -> None:
    if chat_id in _storage:
        _storage[chat_id]["status"] = "COMPLETED"


def clear_match(chat_id: int) -> None:
    if chat_id in _storage:
        del _storage[chat_id]


def get_all_active() -> list[tuple[int, dict]]:
    result = []
    for chat_id, match_info in _storage.items():
        if match_info.get("status") == "LIVE":
            result.append((chat_id, match_info))
    return result
