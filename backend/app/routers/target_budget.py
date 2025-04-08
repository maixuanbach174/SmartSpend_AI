from fastapi import APIRouter, HTTPException
from app.models import *
from app.core.db import SessionDep
from pydantic import BaseModel
from app.crud import *

router = APIRouter()

# 2. Budgeting & Goal Setting Endpoints
@router.post("/budgets/", response_model=TargetBudget)
def create_target_budget(
    category_detail_id: int,
    account_id: int,
    amount: float,
    db: SessionDep,
    finish_date: date,      
    priority: int = 0
):
    """Create a new budget goal"""
    try:
        return create_target_budget(db, category_detail_id, account_id, amount, finish_date, priority)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/budgets/progress/{category_detail_id}", response_model=BudgetProgressResponse)
def get_budget_progress(
    category_detail_id: int,
    account_id: int,
    start_date: date,
    end_date: date,
    db: SessionDep  
):
    """Get budget progress for a category within a date range"""
    try:
        result = get_budget_progress(db, account_id, category_detail_id, start_date, end_date)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
