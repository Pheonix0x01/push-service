from pydantic import BaseModel
from typing import Optional, Literal
from enum import Enum
from uuid import UUID
from datetime import datetime

class NotificationMessage(BaseModel):
    request_id: str
    user_id: UUID
    notification_type: Literal["push"]
    template_code: str
    variables: dict
    priority: int
    metadata: Optional[dict] = None

class NotificationStatus(str, Enum):
    delivered = "delivered"
    pending = "pending"
    failed = "failed"

class StatusUpdate(BaseModel):
    notification_id: str
    status: NotificationStatus
    timestamp: datetime
    error: Optional[str] = None