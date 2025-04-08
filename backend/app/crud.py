from sqlmodel import Session, select, and_, or_, func
from typing import List, Optional
from datetime import date, timedelta
from . import models

# 1. Expense Tracking
def create_bill(
    db: Session,
    bill: models.BillCreate,
    account_id: int,
    category_detail_id: int
) -> models.Bill:
    """Create a new bill/expense entry"""
    db_bill = models.Bill(
        name=bill.name,
        category_detail_id=category_detail_id,
        account_id=account_id,
        description=bill.description,
        price=bill.price,
        schedule_id=bill.schedule_id,
        priority=bill.priority,
        recipient=bill.recipient
    )
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill

def get_bills_by_category(
    db: Session,
    account_id: int,
    category_name: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[models.Bill]:
    """Get all bills for a specific category within a date range"""
    query = select(models.Bill).join(models.CategoryDetail).join(models.Category).where(
        models.Bill.account_id == account_id,
        models.Category.name == category_name
    )
    
    if start_date:
        query = query.where(models.Bill.created_at >= start_date)
    if end_date:
        query = query.where(models.Bill.created_at <= end_date)
        
    return db.exec(query).all()

# 2. Budgeting & Goal Setting
def create_target_budget(
    db: Session,
    category_detail_id: int,
    account_id: int,
    amount: float,
    finish_date: date,
    priority: int = 0
) -> models.TargetBudget:
    """Create a new budget goal"""
    db_budget = models.TargetBudget(
        category_detail_id=category_detail_id,
        account_id=account_id,
        amount=amount,
        finish_date=finish_date,
        priority=priority,
        is_active=True,
        is_achieved=False
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

def get_budget_progress(
    db: Session,
    account_id: int,
    category_detail_id: int,
    start_date: date,
    end_date: date
) -> dict:
    """Get budget progress for a category within a date range"""
    # Get target budget
    target = db.exec(
        select(models.TargetBudget).where(
            models.TargetBudget.account_id == account_id,
            models.TargetBudget.category_detail_id == category_detail_id,
            models.TargetBudget.is_active == True
        )
    ).first()
    
    if not target:
        return {"error": "No active budget found"}
    
    # Get actual spending
    total_spent = db.exec(
        select(func.sum(models.Bill.price)).where(
            models.Bill.account_id == account_id,
            models.Bill.category_detail_id == category_detail_id,
            models.Bill.created_at >= start_date,
            models.Bill.created_at <= end_date
        )
    ).first() or 0
    
    return {
        "target_amount": target.amount,
        "total_spent": total_spent,
        "remaining": target.amount - total_spent,
        "progress_percentage": (total_spent / target.amount * 100) if target.amount > 0 else 0
    }

# 3. Income Management
def create_income(
    db: Session,
    name: str,
    income_type_id: int,
    account_id: int,
    amount: float,
    schedule_id: int,
    description: Optional[str] = None,
    source: Optional[str] = None
) -> models.Income:
    """Create a new income entry"""
    db_income = models.Income(
        name=name,
        income_type_id=income_type_id,
        account_id=account_id,
        amount=amount,
        schedule_id=schedule_id,
        description=description,
        source=source
    )
    db.add(db_income)
    db.commit()
    db.refresh(db_income)
    return db_income

def get_income_summary(
    db: Session,
    account_id: int,
    start_date: date,
    end_date: date
) -> dict:
    """Get income summary by type within a date range"""
    # Get total income by type
    income_by_type = db.exec(
        select(
            models.IncomeType.name,
            func.sum(models.Income.amount).label("total")
        )
        .join(models.Income)
        .where(
            models.Income.account_id == account_id,
            models.Income.created_at >= start_date,
            models.Income.created_at <= end_date
        )
        .group_by(models.IncomeType.name)
    ).all()
    
    total_income = sum(item.total for item in income_by_type)
    
    return {
        "total_income": total_income,
        "income_by_type": {item.name: item.total for item in income_by_type}
    }

# 5. Bill & Subscription Management
def get_upcoming_bills(
    db: Session,
    account_id: int,
    days_ahead: int = 7
) -> List[models.Bill]:
    """Get bills due in the next X days"""
    end_date = date.today() + timedelta(days=days_ahead)
    
    return db.exec(
        select(models.Bill)
        .join(models.Schedule)
        .where(
            models.Bill.account_id == account_id,
            models.Schedule.is_active == True,
            models.Schedule.start_date <= end_date
        )
    ).all()

def get_recurring_bills(
    db: Session,
    account_id: int
) -> List[models.Bill]:
    """Get all recurring bills"""
    return db.exec(
        select(models.Bill)
        .join(models.Schedule)
        .where(
            models.Bill.account_id == account_id,
            models.Schedule.is_active == True,
            models.Schedule.freq_type != 1  # Not one-time
        )
    ).all()

# 7. Smart Saving Features
def get_spending_trends(
    db: Session,
    account_id: int,
    months: int = 6
) -> dict:
    """Get spending trends over the last X months"""
    end_date = date.today()
    start_date = end_date - timedelta(days=30*months)
    
    # Get monthly spending by category
    monthly_spending = db.exec(
        select(
            func.date_trunc('month', models.Bill.created_at).label("month"),
            models.Category.name,
            func.sum(models.Bill.price).label("total")
        )
        .join(models.CategoryDetail)
        .join(models.Category)
        .where(
            models.Bill.account_id == account_id,
            models.Bill.created_at >= start_date,
            models.Bill.created_at <= end_date
        )
        .group_by("month", models.Category.name)
        .order_by("month")
    ).all()
    
    return {
        "monthly_spending": monthly_spending,
        "start_date": start_date,
        "end_date": end_date
    }

def get_category_spending_analysis(
    db: Session,
    account_id: int,
    start_date: date,
    end_date: date
) -> dict:
    """Get detailed spending analysis by category"""
    # Get total spending by category
    category_spending = db.exec(
        select(
            models.Category.name,
            func.sum(models.Bill.price).label("total")
        )
        .join(models.CategoryDetail)
        .join(models.Category)
        .where(
            models.Bill.account_id == account_id,
            models.Bill.created_at >= start_date,
            models.Bill.created_at <= end_date
        )
        .group_by(models.Category.name)
    ).all()
    
    total_spending = sum(item.total for item in category_spending)
    
    return {
        "total_spending": total_spending,
        "category_breakdown": {
            item.name: {
                "amount": item.total,
                "percentage": (item.total / total_spending * 100) if total_spending > 0 else 0
            }
            for item in category_spending
        }
    }
