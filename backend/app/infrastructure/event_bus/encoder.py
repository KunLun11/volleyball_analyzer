import json
from datetime import datetime
from enum import Enum
from uuid import UUID


class DomainEventEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Enum):
            return obj.name
        if hasattr(obj, "value") and not isinstance(obj, (str, bytes, list, dict)):
            return obj.value
        return super().default(obj)
