from fastapi import APIRouter, HTTPException
from app.models import *
from app.core.db import SessionDep
from pydantic import BaseModel
from app.crud import *

router = APIRouter()

# 1. Expense Tracking Endpoints
@router.post("/bills/", response_model=BillResponse)
def create_bill(
    bill: BillCreate,
    category_detail_id: int,
    account_id: int,
    db: SessionDep
):
    """Create a new bill/expense entry"""
    try:
        return create_bill(db, bill, account_id, category_detail_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/bills/category/{category_name}", response_model=List[BillResponse])
def get_bills_by_category(
    db: SessionDep,
    category_name: str,
    account_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    """Get all bills for a specific category within a date range"""
    try:
        return get_bills_by_category(db, account_id, category_name, start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/bills/upcoming", response_model=List[BillResponse])
def get_upcoming_bills(
    db: SessionDep,
    account_id: int,
    days_ahead: int = 7
):
    """Get bills due in the next X days"""
    try:
        return get_upcoming_bills(db, account_id, days_ahead)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/bills/recurring", response_model=List[BillResponse])
def get_recurring_bills(
    account_id: int,
    db: SessionDep
):
    """Get all recurring bills"""
    try:
        return get_recurring_bills(db, account_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 7. Smart Saving Features Endpoints
@router.get("/spending/trends", response_model=SpendingTrendsResponse)
def get_spending_trends(
    db: SessionDep,
    account_id: int,
    months: int = 6
):
    """Get spending trends over the last X months"""
    try:
        return get_spending_trends(db, account_id, months)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/spending/analysis", response_model=CategorySpendingResponse)
def get_category_spending_analysis(
    account_id: int,
    start_date: date,
    end_date: date,
    db: SessionDep
):
    """Get detailed spending analysis by category"""
    try:
        return get_category_spending_analysis(db, account_id, start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 