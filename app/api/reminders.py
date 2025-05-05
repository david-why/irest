from fastapi import APIRouter, HTTPException

from app.models.calendar import (
    AuthorizationStatus,
    EntityType,
    Reminder,
    ReminderCreate,
    ReminderList,
    ReminderListCreate,
    ReminderListUpdate,
    ReminderUpdate,
)
from app.services.reminder import CalendarService

router = APIRouter(prefix="/reminder", tags=["Reminders"])
service = CalendarService()


@router.get("/status")
def get_authorization_status() -> AuthorizationStatus:
    status = service.get_authorization_status(EntityType.reminder)
    return status


@router.get("/lists")
def list_reminder_lists() -> list[ReminderList]:
    return service.get_reminder_lists()


@router.post("/lists")
def create_reminder_list(reminder_list: ReminderListCreate) -> ReminderList:
    try:
        created_list = service.create_reminder_list(reminder_list)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return created_list


@router.get("/lists/{list_id}")
def get_reminder_list(list_id: str) -> ReminderList:
    reminder_list = service.get_reminder_list(list_id)
    if reminder_list is None:
        raise HTTPException(status_code=404, detail="Reminder list not found")
    return reminder_list


@router.patch("/lists/{list_id}")
def update_reminder_list(list_id: str, reminder_list: ReminderListUpdate) -> ReminderList:
    try:
        updated_list = service.update_reminder_list(list_id, reminder_list)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return updated_list


@router.get("/lists/{list_id}/reminders")
def get_reminders_in_list(list_id: str) -> list[Reminder]:
    reminders = service.get_reminders_in_lists([list_id])
    return reminders


@router.post("/lists/{list_id}/reminders")
def create_reminder(list_id: str, reminder: ReminderCreate) -> Reminder:
    try:
        created_reminder = service.create_reminder(list_id, reminder)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return created_reminder


@router.get("/reminders/{reminder_id}")
def get_reminder(reminder_id: str) -> Reminder:
    reminder = service.get_reminder(reminder_id)
    if reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder


@router.patch("/reminders/{reminder_id}")
def update_reminder(reminder_id: str, reminder: ReminderUpdate) -> Reminder:
    try:
        updated_reminder = service.update_reminder(reminder_id, reminder)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return updated_reminder
