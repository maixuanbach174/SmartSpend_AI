from fastapi import APIRouter, Depends
from sqlmodel import select
from ..core.db import SessionDep
from ..models import Account
from ..dependencies import get_token_header

router = APIRouter(
    prefix="/admin",
    tags=["admin"], 
    # dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)

@router.post("/")
async def add_new_account(account: Account, session: SessionDep):
    session.add(account)
    session.commit()
    session.refresh(account)
    return account

@router.get("/")
async def get_all_accounts(session: SessionDep):
    accounts = session.exec(select(Account)).all()
    return accounts