from datetime import date, time, datetime
from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional
from enum import Enum

class RecurrenceType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    ABSOLUTE_MONTHLY = "absoluteMonthly"
    RELATIVE_MONTHLY = "relativeMonthly"
    ABSOLUTE_YEARLY = "absoluteYearly"
    RELATIVE_YEARLY = "relativeYearly"

class DayOfWeek(str, Enum):
    SUNDAY = "sunday"
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"

class WeekIndex(str, Enum):
    FIRST = "first"
    SECOND = "second"
    THIRD = "third"
    FOURTH = "fourth"
    LAST = "last"

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
    # __tablename__ = "account"
    # account_id: Optional[int] = Field(default=None, primary_key=True)
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


# class RecurrencePattern(SQLModel, table=True):
#     __tablename__ = "recurrence_pattern"
#     pattern_id: int = Field(primary_key=True)
#     type: RecurrenceType
#     interval: int = Field(default=1, ge=1, le=99)
#     month: Optional[int] = Field(default=None, le=12, ge=1)
#     dayOfMonth: Optional[int] = Field(default=None, ge=1, le=31)
#     index: Optional[WeekIndex] = Field(default=None)
#     daysOfWeek: List["RecurrencePatternDay"] = Relationship(back_populates="recurrencePattern")
#     pattern_schedule: "Schedule" = Relationship(back_populates="schedule_pattern")

# class RecurrencePatternDay(SQLModel, table=True):
#     __tablename__ = "recurrence_pattern_day"
#     pattern_id: Optional[int] = Field(default=None, foreign_key="recurrence_pattern.pattern_id", primary_key=True)
#     day: DayOfWeek = Field(primary_key=True)
#     recurrencePattern: "RecurrencePattern" = Relationship(back_populates="daysOfWeek")

# class Schedule(SQLModel, table=True):
#     schedule_id: Optional[int] = Field(default=None, primary_key=True)
#     pattern_id: Optional[int] = Field(default=None, foreign_key="recurrence_pattern.pattern_id")
#     is_active: bool = Field(default=True)
#     start_date: date = Field(default=date.today())
#     end_date: Optional[date] = None
#     start_time: time = Field(default=time(0, 0, 0))
#     end_time: Optional[time] = None

#     schedule_pattern: "RecurrencePattern" = Relationship(back_populates="pattern_schedule")
#     schedule_activity: "Activity" = Relationship(back_populates="activity_schedule")

# class Activity(SQLModel, table=True):
#     __tablename__ = "activity"
#     activity_id: Optional[int] = Field(default=None, primary_key=True)
#     account_id: int = Field(foreign_key="account.account_id", index=True)
#     name: str = Field(max_length=255, index=True)
#     description: Optional[str] = None
#     expense: float = Field(ge=0.0)
#     schedule_id: Optional[int] = Field(default=None,foreign_key="schedule.schedule_id")
#     location: Optional[str] = Field(max_length=255)
#     category: Category

#     activity_schedule: Schedule = Relationship(back_populates="schedule_activity")

#####################

class ActivityBase(SQLModel):
    name: str = Field(max_length=255, index=True)
    description: Optional[str] = Field(default=None)
    expense: float = Field(ge=0.0)
    location: Optional[str] = Field(default=None, max_length=255)
    category: Category

class ScheduleBase(SQLModel):
    is_active: bool = Field(default=True)
    start_date: date = Field(default=date.today())
    end_date: Optional[date] = Field(default=None)
    start_time: time = Field(default_factory=lambda: datetime.now().time())
    end_time: Optional[time] = Field(default=None)

class RecurrencePatternBase(SQLModel):
    # type: Optional[RecurrenceType]
    interval: int = Field(default=1, ge=1, le=99)

class RecurrencePatternDayBase(SQLModel):
    day: DayOfWeek = Field(primary_key=True)

class RecurrencePattern(RecurrencePatternBase, table=True):
    __tablename__ = "recurrence_pattern"
    pattern_id: Optional[int] = Field(default=None, primary_key=True)
    month: Optional[int] = Field(default=None, le=12, ge=1)
    dayOfMonth: Optional[int] = Field(default=None, ge=1, le=31)
    index: Optional[WeekIndex] = Field(default=None)
    type: Optional[RecurrenceType] = Field(default=None)
    daysOfWeek: List["RecurrencePatternDay"] = Relationship(back_populates="recurrencePattern")
    pattern_schedule: "Schedule" = Relationship(back_populates="schedule_pattern")   

class RecurrencePatternDay(RecurrencePatternDayBase, table=True):
    __tablename__ = "recurrence_pattern_day"
    pattern_id: Optional[int] = Field(default=None, foreign_key="recurrence_pattern.pattern_id", primary_key=True)
    recurrencePattern: "RecurrencePattern" = Relationship(back_populates="daysOfWeek")

class Schedule(ScheduleBase, table=True):
    __tablename__ = "schedule"
    schedule_id: Optional[int] = Field(default=None, primary_key=True)
    pattern_id: Optional[int] = Field(default=None, foreign_key="recurrence_pattern.pattern_id")
    schedule_pattern: "RecurrencePattern" = Relationship(back_populates="pattern_schedule")
    schedule_activity: "Activity" = Relationship(back_populates="activity_schedule")
 
class Activity(ActivityBase, table=True):
    __tablename__ = "activity"
    activity_id: Optional[int] = Field(default=None, primary_key=True)
    account_id: Optional[int] = Field(default=None, foreign_key="account.account_id", index=True)
    schedule_id: Optional[int] = Field(default=None,foreign_key="schedule.schedule_id")
    activity_schedule: Optional["Schedule"] = Relationship(back_populates="schedule_activity")

class RecurrencePatternDayPublic(RecurrencePatternDayBase):
    pattern_id: int

class RecurrencePatternPublic(RecurrencePatternBase):
    pattern_id: int
    type: RecurrenceType
    daysOfWeek: Optional[List[RecurrencePatternDay]] = Field(default=None)
    month: Optional[int] = Field(default=None, le=12, ge=1)
    dayOfMonth: Optional[int] = Field(default=None, ge=1, le=31)
    index: Optional[WeekIndex] = Field(default=None)

class SchedulePublic(ScheduleBase):
    schedule_id: int 
    pattern_id: int 
    pattern: Optional[RecurrencePatternPublic]

class ActivityPublic(ActivityBase):
    activity_id: int
    account_id: int
    schedule_id: Optional[int]
    activity_schedule: Optional[SchedulePublic]

class OnceActivityCreate(ActivityBase):
    pass

class DailyRecurrencePatternCreate(RecurrencePatternBase):
    interval: int = Field(default=1, ge=1, le=99)

class DailyScheduleCreate(ScheduleBase):
    schedule_pattern: DailyRecurrencePatternCreate

class DailyActivityCreate(ActivityBase):
    schedule: DailyScheduleCreate

class WeelyRecurrencePatternDayCreate(RecurrencePatternDayBase):
    day: DayOfWeek = Field(primary_key=True)

class WeeklyRecurrencePatternCreate(RecurrencePatternBase):
    interval: int = Field(default=1, ge=1, le=99)
    daysOfWeek: List[WeelyRecurrencePatternDayCreate]

class WeeklyScheduleCreate(ScheduleBase):
    schedule_pattern: WeeklyRecurrencePatternCreate

class WeeklyActivityCreate(ActivityBase):
    schedule: WeeklyScheduleCreate

class AbsoluteMonthlyRecurrencePatternCreate(RecurrencePatternBase):
    interval: int = Field(default=1, ge=1, le=99)
    dayOfMonth: int = Field(default=None, ge=1, le=31)

class AbsoluteMonthlyScheduleCreate(ScheduleBase):
    schedule_pattern: AbsoluteMonthlyRecurrencePatternCreate

class AbsoluteMonthlyActivityCreate(ActivityBase):
    schedule: AbsoluteMonthlyScheduleCreate

class RelativeMonthlyRecurrencePatternCreate(RecurrencePatternBase):
    interval: int = Field(default=1, ge=1, le=99)
    daysOfWeek: List[WeelyRecurrencePatternDayCreate]
    index: WeekIndex

class RelativeMonthlyScheduleCreate(ScheduleBase):
    schedule_pattern: RelativeMonthlyRecurrencePatternCreate

class RelativeMonthlyActivityCreate(ActivityBase):
    schedule: RelativeMonthlyScheduleCreate

class AbsoluteYearlyRecurrencePatternCreate(RecurrencePatternBase):
    interval: int = Field(default=1, ge=1, le=99)
    month: int = Field(default=None, le=12, ge=1)
    dayOfMonth: int = Field(default=None, ge=1, le=31)

class AbsoluteYearlyScheduleCreate(ScheduleBase):
    schedule_pattern: AbsoluteYearlyRecurrencePatternCreate

class AbsoluteYearlyActivityCreate(ActivityBase):
    schedule: AbsoluteYearlyScheduleCreate

class RelativeYearlyRecurrencePatternCreate(RecurrencePatternBase):
    interval: int = Field(default=1, ge=1, le=99)
    month: int = Field(default=None, le=12, ge=1)
    daysOfWeek: List[WeelyRecurrencePatternDayCreate]
    index: WeekIndex

class RelativeYearlyScheduleCreate(ScheduleBase):
    schedule_pattern: RelativeYearlyRecurrencePatternCreate
    
class RelativeYearlyActivityCreate(ActivityBase):
    schedule: RelativeYearlyScheduleCreate



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
    schedule_id: Optional[int] = Field(foreign_key="schedule.schedule_id")
    description: Optional[str] = None
    amount: float = Field(ge=0.0)
    source: Optional[str] = None