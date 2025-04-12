from sqlmodel import create_engine, Session, SQLModel
from ..core.config import settings
from typing import Annotated
from fastapi import Depends

engine = create_engine(str(settings.DATABASE_URL))

def create_database():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
