import asyncio
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException

from app.api import reminders
from app.deps.auth import verify_api_key
from app.exceptions import ApplicationException
from app.models.calendar import EntityType
from app.services.reminder import CalendarService


@asynccontextmanager
async def lifespan(app: FastAPI):
    service = CalendarService()
    if service.get_authorization_status(EntityType.reminder) == 0:
        print("Requesting access to reminders...")
        await asyncio.to_thread(service.request_access_to_reminders)
    yield


app = FastAPI(
    title="iREST",
    lifespan=lifespan,
    dependencies=[Depends(verify_api_key)],
)

app.include_router(reminders.router)


@app.exception_handler(ApplicationException)
def application_exception_handler(request, exc: ApplicationException):
    raise HTTPException(status_code=exc.code, detail=exc.detail) from exc
