from datetime import date, time, datetime
from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional
from enum import Enum

class RecurrenceType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    ONCE = "once"

class Category(str, Enum):
    # Housing
    RENT = "rent"
    MORTGAGE = "mortgage"
    UTILITIES = "utilities"  # (electricity, water, gas)
    INTERNET = "internet"
    PHONE = "phone"
    
    # Transportation
    FUEL = "fuel"
    PUBLIC_TRANSPORT = "public_transport"
    CAR_MAINTENANCE = "car_maintenance"
    PARKING = "parking"
    
    # Daily Living
    GROCERIES = "groceries"
    DINING_OUT = "dining_out"
    SHOPPING = "shopping"  # (clothing, electronics, etc.)
    
    # Health
    HEALTH_INSURANCE = "health_insurance"
    MEDICAL = "medical"
    PHARMACY = "pharmacy"
    GYM = "gym"
    
    # Entertainment
    SUBSCRIPTIONS = "subscriptions"  # (Netflix, Spotify)
    TRAVEL = "travel"
    HOBBIES = "hobbies"
    
    # Financial Obligations
    LOAN_PAYMENT = "loan_payment"
    CREDIT_CARD = "credit_card"
    INSURANCE = "insurance"  # (car, home, life)
    
    # Miscellaneous
    EDUCATION = "education"
    CHARITY = "charity"
    OTHER = "other"

class IncomeType(str, Enum):
    SALARY = "salary"
    BONUS = "bonus"
    COMMISSION = "commission"
    
    # Investments
    INVESTMENT = "investment"
    DIVIDENDS = "dividends"
    INTEREST = "interest"  # (savings, bonds)
    
    # Government/Retirement
    PENSION = "pension"
    SOCIAL_SECURITY = "social_security"
    UNEMPLOYMENT = "unemployment"
    
    # Side Income
    FREELANCE = "freelance"
    RENTAL_INCOME = "rental_income"
    SIDE_HUSTLE = "side_hustle"
    
    # Other
    GIFTS = "gifts"
    REFUNDS = "refunds"
    OTHER = "other"

class Priority(int, Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2

class Gender(int, Enum):
    UNSPECIFIED = 0
    MALE = 1
    FEMALE = 2
    NON_BINARY = 3  # Optional expansion

class AccountBase(SQLModel):
    first_name: str = Field(max_length=255, index=True)
    last_name: str = Field(max_length=255)
    dob: date
    gender: Gender
    country: str = Field(max_length=255)
    email: str = Field(max_length=255, index=True)
    start_date: date = Field(default=date.today())

class Account(AccountBase, table=True):
    __tablename__ = "account"
    account_id: Optional[int] = Field(default=None, primary_key=True)

class AccountCreate(AccountBase):
    pass

class AccountPublic(AccountBase):
    account_id: int

#######################

class ActivityBase(SQLModel):
    name: str = Field(max_length=255, index=True)
    startDate: date = Field(default=date.today())
    endDate: date | None = Field(default=None)
    expense: float = Field(ge=0.0, default=0.0)
    category: Category
    description: str | None = Field(default=None)
    recurrenceType: RecurrenceType = Field(default=RecurrenceType.ONCE)

class Activity(ActivityBase, table=True):
    __tablename__ = "activity"
    activity_id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.account_id", index=True)

class ActivityCreate(ActivityBase):
    account_id: int
    pass

class ActivityPublic(ActivityBase):
    activity_id: int
    account_id: int

####################

class TargetBudget(SQLModel, table=True):
    __tablename__ = "target_budget"
    target_budget_id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.account_id", index=True)
    amount: float = Field(ge=0.0)
    targetDate: Optional[date] = Field(default=date.today())
    finished: bool = Field(default=False)
    enabled: bool = Field(default=True)
    priority: Priority = Field(default=Priority.MEDIUM)
    category: Category 

class Income(SQLModel, table=True):
    __tablename__ = "income"
    income_id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.account_id", index=True)
    name: str = Field(max_length=255, index=True)
    incomeType: IncomeType
    description: Optional[str] = None
    amount: float = Field(ge=0.0)
    source: Optional[str] = None

class SpendPublic(SQLModel):
    year: int = Field(le=3000, ge=1900)
    month: int | None = Field(default=None, ge=1, le=12)
    day: int | None = Field(default=None,ge=1, le=31)
    totalSpend: float = Field(ge=0.0)