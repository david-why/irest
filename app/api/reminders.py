from fastapi import APIRouter, HTTPException

from app.models.calendar import (
    Reminder,
    ReminderCreate,
    ReminderList,
    ReminderListCreate,
)
from app.services.reminder import ReminderService

router = APIRouter(prefix="/reminder", tags=["Reminders"])
service = ReminderService()


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
