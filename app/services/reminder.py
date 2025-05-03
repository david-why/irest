from concurrent.futures import Future
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from AppKit import NSColor  # type: ignore
from EventKit import EKCalendar, EKEntityTypeReminder, EKEventStore, EKReminder  # type: ignore
from Foundation import NSURL, NSCalendar, NSDate, NSDateComponents, NSTimeZone  # type: ignore

from app.exceptions import NotFoundException
from app.models.calendar import (
    AuthorizationStatus,
    EntityType,
    Reminder,
    ReminderCreate,
    ReminderList,
    ReminderListCreate,
    ReminderListUpdate,
    Source,
)
from app.models.common import RGBA


def _components_to_datetime(components):
    if components is None:
        return None
    calendar = components.calendar()
    if calendar is None:
        return None
    date = calendar.dateFromComponents_(components)
    if date is None:
        return None
    tz = components.timeZone()
    if tz is None:
        tzinfo = None
    else:
        tzinfo = ZoneInfo(tz.name())
    return datetime.fromtimestamp(date.timeIntervalSince1970(), tz=tzinfo)


def _datetime_to_components(date: datetime) -> Any:
    # FIXME this always uses floating timezone
    date = date.astimezone()
    components = NSDateComponents()
    components.setCalendar_(NSCalendar.currentCalendar())
    components.setYear_(date.year)
    components.setMonth_(date.month)
    components.setDay_(date.day)
    components.setHour_(date.hour)
    components.setMinute_(date.minute)
    components.setSecond_(date.second)
    components.setTimeZone_(NSTimeZone.localTimeZone())
    return components


def _date_to_datetime(date):
    if date is None:
        return None
    return datetime.fromtimestamp(
        date.timeIntervalSince1970(), tz=timezone.utc
    ).astimezone()


def _datetime_to_date(date: datetime | None) -> Any | None:
    if date is None:
        return None
    return NSDate.dateWithTimeIntervalSince1970_(date.timestamp())


def _rgba_to_ns_color(rgba: RGBA) -> Any:
    return NSColor.colorWithRed_green_blue_alpha_(rgba.r, rgba.g, rgba.b, rgba.a)


class CalendarService:
    def __init__(self):
        self.store = EKEventStore()

    def get_authorization_status(self, type: EntityType) -> AuthorizationStatus:
        status = EKEventStore.authorizationStatusForEntityType_(type)
        return AuthorizationStatus(status)

    def request_access_to_reminders(self) -> bool:
        future = Future()
        self.store.requestFullAccessToRemindersWithCompletion_(
            lambda granted, error: future.set_result(granted)
        )
        return future.result()

    def _get_ek_calendars(self, type: int):
        return self.store.calendarsForEntityType_()

    def _map_reminder_list(self, calendar) -> ReminderList:
        id = calendar.calendarIdentifier()
        type = calendar.type()
        title = calendar.title()
        color = calendar.color()
        color_r = color.redComponent()
        color_g = color.greenComponent()
        color_b = color.blueComponent()
        color_a = color.alphaComponent()
        is_subscribed = calendar.isSubscribed()
        source = calendar.source()
        source_id = source.sourceIdentifier()
        source_title = source.title()
        source_type = source.sourceType()
        return ReminderList(
            id=id,
            type=type,
            title=title,
            color=RGBA(r=color_r, g=color_g, b=color_b, a=color_a),
            is_subscribed=is_subscribed,
            source=Source(id=source_id, title=source_title, type=source_type),
        )

    def _map_reminder(self, reminder) -> Reminder:
        id = reminder.calendarItemIdentifier()
        title = reminder.title()
        start_date = _components_to_datetime(reminder.startDateComponents())
        due_date = _components_to_datetime(reminder.dueDateComponents())
        is_completed = reminder.isCompleted()
        completion_date = _date_to_datetime(reminder.completionDate())
        priority = reminder.priority()
        location = reminder.location()
        # FIXME url doesn't seem to work
        url = reminder.URL()
        if url is not None:
            url = url.absoluteString()
        notes = reminder.notes() if reminder.hasNotes() else None
        return Reminder(
            id=id,
            title=title,
            start_date=start_date,
            due_date=due_date,
            is_completed=is_completed,
            completion_date=completion_date,
            priority=priority,
            location=location,
            url=url,
            notes=notes,
        )

    def get_reminder_lists(self) -> list[ReminderList]:
        calendars = self._get_ek_calendars(EKEntityTypeReminder)
        return [self._map_reminder_list(calendar) for calendar in calendars]

    def get_reminder_list(self, id: str) -> ReminderList | None:
        calendar = self.store.calendarWithIdentifier_(id)
        if calendar is None:
            return None
        return self._map_reminder_list(calendar)

    def update_reminder_list(self, id: str, schema: ReminderListUpdate) -> ReminderList:
        calendar = self.store.calendarWithIdentifier_(id)
        if calendar is None:
            raise NotFoundException("Calendar not found")
        if schema.title is not None:
            calendar.setTitle_(schema.title)
        if schema.color is not None:
            calendar.setColor_(_rgba_to_ns_color(schema.color))
        success = self.store.saveCalendar_commit_error_(calendar, True, None)
        if not success:
            raise ValueError("Failed to save reminder list")
        return self._map_reminder_list(calendar)

    def get_reminders_in_lists(self, list_ids: list[str]) -> list[Reminder]:
        calendars = self._get_ek_calendars(EKEntityTypeReminder)
        filtered_calendars = [
            calendar
            for calendar in calendars
            if calendar.calendarIdentifier() in list_ids
        ]

        predicate = self.store.predicateForRemindersInCalendars_(filtered_calendars)

        future = Future()
        self.store.fetchRemindersMatchingPredicate_completion_(
            predicate, lambda reminders: future.set_result(reminders)
        )
        reminders = future.result()

        return [self._map_reminder(reminder) for reminder in reminders if reminder]

    def get_reminder(self, id: str) -> Reminder | None:
        reminder = self.store.calendarItemWithIdentifier_(id)
        if reminder is None:
            return None
        return self._map_reminder(reminder)

    def create_reminder(self, list_id: str, schema: ReminderCreate):
        calendar = self.store.calendarWithIdentifier_(list_id)
        if calendar is None:
            raise NotFoundException("Calendar not found")
        reminder = EKReminder.reminderWithEventStore_(self.store)
        reminder.setCalendar_(calendar)
        reminder.setTitle_(schema.title)
        if schema.start_date is not None:
            reminder.setStartDateComponents_(_datetime_to_components(schema.start_date))
        if schema.due_date is not None:
            reminder.setDueDateComponents_(_datetime_to_components(schema.due_date))
        reminder.setPriority_(schema.priority)
        if schema.location is not None:
            reminder.setLocation_(schema.location)
        if schema.url is not None:
            reminder.setURL_(NSURL.URLWithString_(schema.url))
        if schema.notes is not None:
            reminder.setNotes_(schema.notes)
        success = self.store.saveReminder_commit_error_(reminder, True, None)
        if not success:
            raise ValueError("Failed to save reminder")
        return self._map_reminder(reminder)

    def create_reminder_list(self, schema: ReminderListCreate):
        source = self.store.sourceWithIdentifier_(schema.source.id)
        if source is None:
            raise NotFoundException("Source not found")
        calendar = EKCalendar.calendarForEntityType_eventStore_(
            EKEntityTypeReminder, self.store
        )
        calendar.setTitle_(schema.title)
        if schema.color is not None:
            calendar.setColor_(_rgba_to_ns_color(schema.color))
        calendar.setSource_(source)
        success = self.store.saveCalendar_commit_error_(calendar, True, None)
        if not success:
            raise ValueError("Failed to save reminder list")
        return self._map_reminder_list(calendar)
