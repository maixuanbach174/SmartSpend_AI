from fastapi import Depends, FastAPI

from .routers import income, bill, target_budget

from .dependencies import get_query_token, get_token_header
from .internal import admin
from .core.db import create_database, engine
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database()
    yield
    engine.dispose()

app = FastAPI(dependencies=[Depends(get_query_token)], lifespan=lifespan)

app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)

app.include_router(router=income.router)
app.include_router(router=bill.router)
app.include_router(router=target_budget.router)