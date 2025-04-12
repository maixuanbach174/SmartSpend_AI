from fastapi import Depends, FastAPI
from .routers import account, activity

from .dependencies import get_query_token
from .internal import admin
from .core.db import create_database, engine
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database()
    yield
    engine.dispose()

# app = FastAPI(dependencies=[Depends(get_query_token)], lifespan=lifespan)
app = FastAPI(lifespan=lifespan)

app.include_router(router=admin.router)
app.include_router(router=account.router)
app.include_router(router=activity.router)