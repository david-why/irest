from datetime import datetime
from enum import IntEnum

from pydantic import BaseModel

from app.models.common import RGBA, Identified


class SourceType(IntEnum):
    local = 0
    exchange = 1
    caldav = 2
    mobile_me = 3
    subscribed = 4
    birthdays = 5


class Source(BaseModel):
    """A source of calendars, such as the local source or a CalDAV account (EKSource)."""

    id: str
    title: str
    type: SourceType


class CalendarType(IntEnum):
    local = 0
    caldav = 1
    exchange = 2
    subscription = 3
    birthday = 4


class ReminderList(BaseModel):
    """A reminder list (EKCalendar)."""

    id: str
    type: CalendarType
    title: str
    color: RGBA
    is_subscribed: bool
    source: Source


class ReminderListCreate(BaseModel):
    """A reminder list to be created."""

    title: str
    color: RGBA | None = None
    source: Identified


class Reminder(BaseModel):
    """A reminder (EKReminder)."""

    id: str
    title: str
    start_date: datetime | None
    due_date: datetime | None
    is_completed: bool
    completion_date: datetime | None
    priority: int
    location: str | None
    url: str | None
    notes: str | None
    # TODO alarms
    # TODO recurrence_rules


class ReminderCreate(BaseModel):
    """A reminder to be created."""

    title: str
    start_date: datetime | None = None
    due_date: datetime | None = None
    priority: int = 0
    location: str | None = None
    url: str | None = None
    notes: str | None = None
