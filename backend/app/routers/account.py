from fastapi import APIRouter, HTTPException
from sqlmodel import select

from ..core.db import SessionDep

from ..models import AccountCreate, AccountPublic, Account

router = APIRouter(
    prefix="/account",
    tags=["Account"],
    responses= {201: {"description" : "created"}},
)

@router.post("/", response_model=AccountPublic)
def create_new_account(account: AccountCreate, session: SessionDep):
    db_account = Account.model_validate(account)
    session.add(db_account)
    session.commit()
    session.flush(db_account)
    return db_account

@router.get("/{account_id}", response_model=AccountPublic)
def get_account_by_id(account_id: int, session: SessionDep):
    statement = select(Account).where(Account.account_id == account_id)
    account_db = session.exec(statement=statement).first()
    if not account_db:
        raise HTTPException(status_code=404, detail="Account not found")
    return account_db