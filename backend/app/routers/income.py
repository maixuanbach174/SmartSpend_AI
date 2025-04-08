
# 3. Income Management Endpoints
from fastapi import APIRouter, HTTPException
from app.models import *
from app.core.db import SessionDep
from pydantic import BaseModel
from app.crud import *

router = APIRouter()

@router.post("/incomes/", response_model=Income)
def create_income(
    name: str,
    income_type_id: int,
    account_id: int,
    amount: float,
    schedule_id: int,
    db: SessionDep,
    description: Optional[str] = None,
    source: Optional[str] = None
):
    """Create a new income entry"""
    try:
        return create_income(
            db, name, income_type_id, account_id, amount, 
            schedule_id, description, source
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/incomes/summary", response_model=IncomeSummaryResponse)
def get_income_summary(
    account_id: int,
    start_date: date,
    end_date: date,
    db: SessionDep
):
    """Get income summary by type within a date range"""
    try:
        return get_income_summary(db, account_id, start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
