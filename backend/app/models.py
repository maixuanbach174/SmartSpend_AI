from datetime import date, time
from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional
from pydantic import BaseModel

class Account(SQLModel, table=True):
    __tablename__ = "account"
    account_id: int | None = Field(default=None, primary_key=True)
    first_name: str = Field(max_length=255, index=True)
    last_name: str = Field(max_length=255)
    dob: date
    gender: int = Field(ge=0, le=2)
    country: str = Field(max_length=255)
    email: str = Field(max_length=255, index=True)
    start_date: date = Field(default=date.today())
    total_spend_in_month: float = Field(default=0.0, ge=0.0)
    total_income_in_month: float = Field(default=0.0, ge=0.0)

class Category(SQLModel, table=True):
    __tablename__ = "category"
    category_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, index=True)
    total_spend: float = Field(default=0.0, ge=0.0)
    account_id: int = Field(foreign_key="account.account_id")

class CategoryDetail(SQLModel, table=True):
    __tablename__ = "category_detail"
    category_detail_id: int | None = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="category.category_id")
    name: str = Field(max_length=255, index=True)
    total_spend: float = Field(default=0.0, ge=0.0)
    priority: int = Field(ge=0, le=2)
    account_id: int = Field(foreign_key="account.account_id")

class Schedule(SQLModel, table=True):
    schedule_id: int | None = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.account_id")
    start_date: date = Field(default=date.today())
    end_date: date = Field(default=date.today())
    is_active: bool = Field(default=True)
    # 1: once, 4: daily, 8: weekly, 16: monthly, 32: monthly(relative)
    freq_type: int = Field(default=1, ge=1, le=32)
    freq_interval: int = Field(default=0, ge=0)
     # 1: at the specified time, 2: seconds, 4, minutes, 8: hours
    time_type: int = Field(default=1, ge=1, le=8)
    time_interval: int = Field(default=0, ge=0)
    start_time: time = Field(default=time(0, 0, 0))

class Activity(SQLModel, table=True):
    __tablename__ = "activity"
    activity_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, index=True)
    category_detail_id: int = Field(foreign_key="category_detail.category_detail_id")
    account_id: int = Field(foreign_key="account.account_id")
    description: str | None = Field(max_length=255)
    location: str | None = Field(max_length=255)
    schedule_id: int = Field(foreign_key="schedule.schedule_id")

class BillCreate(BaseModel):
    __tablename__ = "bill"
    name: str
    category_name: str
    description: Optional[str] = None
    price: float
    priority: int
    recipient: Optional[str] = None
    schedule_id: int

class Bill(SQLModel, table=True):
    __tablename__ = "bill"
    bill_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, index=True)
    category_detail_id: int = Field(foreign_key="category_detail.category_detail_id")
    account_id: int = Field(foreign_key="account.account_id")
    description: str | None = Field(max_length=255)
    price: float = Field(ge=0.0)
    schedule_id: int = Field(foreign_key="schedule.schedule_id")
    priority: int = Field(ge=0, le=2)
    recipient: str | None = Field(max_length=255)

class TargetBudget(SQLModel, table=True):
    __tablename__ = "target_budget"
    target_budget_id: int | None = Field(default=None, primary_key=True)
    category_detail_id: int = Field(foreign_key="category_detail.category_detail_id")
    account_id: int = Field(foreign_key="account.account_id")
    amount: float = Field(ge=0.0)
    finish_date: date | None = Field(default=date.today())
    is_achieved: bool = Field(default=False)
    is_active: bool = Field(default=True)
    priority: int = Field(ge=0, le=2)

class IncomeType(SQLModel, table=True):
    __tablename__ = "income_type"
    income_type_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, index=True)
    total_income: float = Field(ge=0.0)
    account_id: int = Field(foreign_key="account.account_id")

class Income(SQLModel, table=True):
    __tablename__ = "income"
    income_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, index=True)
    income_type_id: int = Field(foreign_key="income_type.income_type_id")
    account_id: int = Field(foreign_key="account.account_id")
    amount: float = Field(ge=0.0)
    schedule_id: int = Field(foreign_key="schedule.schedule_id")
    description: str | None = Field(max_length=255)
    source: str | None = Field(max_length=255)

class ActivityBill(SQLModel, table=True):
    __tablename__ = "activity_bill"
    activity_id: int = Field(foreign_key="activity.activity_id", primary_key=True)
    bill_id: int = Field(foreign_key="bill.bill_id", primary_key=True)
    account_id: int = Field(foreign_key="account.account_id")

# Response Models
class BillResponse(BaseModel):
    bill_id: int
    name: str
    category_detail_id: int
    account_id: int
    description: Optional[str] = None
    price: float
    schedule_id: int
    priority: int
    recipient: Optional[str] = None

class BudgetProgressResponse(BaseModel):
    target_amount: float
    total_spent: float
    remaining: float
    progress_percentage: float

class IncomeSummaryResponse(BaseModel):
    total_income: float
    income_by_type: dict[str, float]

class SpendingTrendsResponse(BaseModel):
    monthly_spending: List[dict]
    start_date: date
    end_date: date

class CategorySpendingResponse(BaseModel):
    total_spending: float
    category_breakdown: dict[str, dict[str, float]]