from fastapi import FastAPI

from app.api import reminders

app = FastAPI(title="iREST")

app.include_router(reminders.router)
