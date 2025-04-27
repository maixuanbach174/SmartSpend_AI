from contextlib import asynccontextmanager


from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import account, activity, voice, auth
from app.dependencies import get_query_token
from app.internal import admin
from app.core.db import create_database, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database()
    yield
    engine.dispose()

# app = FastAPI(dependencies=[Depends(get_query_token)], lifespan=lifespan)
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=admin.router)
app.include_router(router=auth.router)
app.include_router(router=account.router)
app.include_router(router=activity.router)