from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, field_validator, Field

# --- Nested models ---

class Behavior(BaseModel):
    category: Optional[Literal[
        "off-task", "disruption", "non-participation", "tardy", "absence",
        "peer-disruption", "technology-violation", "prosocial", "defiance",
        "aggression", "self-management", "respect", "other"
    ]] = None
    description: Optional[str] = None
    severity: Optional[Literal["low", "moderate", "high"]] = None
    is_positive: Optional[bool] = None
    needs_followup: Optional[bool] = None
    tags: Optional[List[str]] = []

class Context(BaseModel):
    class_name: Optional[str] = None
    teacher: Optional[str] = None
    activity: Optional[str] = None
    group_ids: Optional[List[str]] = []
    location: Optional[str] = None

class Intervention(BaseModel):
    status: Optional[Literal["none", "recommended", "in_progress", "completed"]] = None
    type: Optional[str] = None
    notes: Optional[str] = None
    tier: Optional[Literal["universal", "tier_1", "tier_2", "tier_3"]] = None

# --- Main model ---

class BehaviorRecord(BaseModel):
    student_name: str = ""
    source: Literal["teacher_note"] = "teacher_note"
    recording_timestamp: datetime = Field(default_factory=datetime.utcnow)

    student_id: Optional[int] = None
    behavior: Behavior = Field(default_factory=Behavior)
    context: Context = Field(default_factory=Context)
    intervention: Intervention = Field(default_factory=Intervention)
    behavior_date: Optional[datetime] = None

    @field_validator("student_id", mode="before")
    @classmethod
    def blank_string_to_none(cls, value):
        if value == "":
            return None
        return value

    @field_validator("recording_timestamp", "behavior_date", mode="before")
    @classmethod
    def parse_datetime(cls, value):
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value
