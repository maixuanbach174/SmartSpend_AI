from calendar import monthrange
from fastapi import APIRouter, Query, HTTPException
from sqlmodel import select, func, or_
from typing import Annotated
from datetime import date, datetime

from ..models import Activity, ActivityCreate, ActivityPublic, Category, RecurrenceType, SpendPublic

from ..core.db import SessionDep

router = APIRouter(
    prefix="/activity",
    tags=["Activity"],
    responses={201: {"description": "created"}},
)

@router.post("/", response_model=ActivityPublic)
def create_new_activity(activity: ActivityCreate, session: SessionDep):
    db_activity = Activity.model_validate(activity)
    session.add(db_activity)
    session.commit()
    session.refresh(db_activity)
    return db_activity

@router.get("/{account_id}")
def get_activities(*,account_id: int,offset: Annotated[int, Query(ge=0)] = 0, limit: Annotated[int, Query(ge=1)] = 100, session: SessionDep) -> list[ActivityPublic]:
    statement = select(Activity).where(Activity.account_id == account_id).offset(offset).limit(limit=limit)
    result = session.exec(statement).all()
    return result

@router.get("/spending/year/{account_id}") 
def get_spending_in_year(
    *, account_id: int, 
    category: Category | None = None,
    year: Annotated[int, Query(le=3000, ge=1800)],
    session: SessionDep
    ):

    today = date.today()
    
    if year > date.today().year:
        return SpendPublic(
            year=year,
            month=None, 
            day=None,
            totalSpend=0.0
        )
    
    year_start_date = date(year=year, month=1, day=1)
    year_end_date = date(year=year, month=12, day=31) if today.year > year else today
    
    statement = select(Activity).where(
        Activity.account_id == account_id, 
        Activity.startDate <= year_end_date,
        or_ (
            Activity.endDate == None, 
            Activity.endDate >= year_start_date
        )
        )
    
    if category is not None:
        statement = statement.where(Activity.category == category)

    activities = session.exec(statement=statement).all()

    totalSpend = 0.0
    for activity in activities:
        start_date = activity.startDate
        end_date = activity.endDate if activity.endDate is not None else year_end_date

        overlap_start = max (start_date, year_start_date)
        overlap_end = min (year_end_date, end_date)
        
        if activity.recurrenceType == RecurrenceType.ONCE:
            if activity.startDate == overlap_start:
                totalSpend += activity.expense
        else:
            occurrence = 0
            match activity.recurrenceType:
                case RecurrenceType.DAILY:
                    occurrence = (overlap_end - overlap_start).days + 1
                case RecurrenceType.WEEKLY:
                    time_delta = (overlap_end - overlap_start).days + 1
                    overlapdWeekday = overlap_start.weekday()
                    startdateWeekday = start_date.weekday()
                    gap = startdateWeekday - overlapdWeekday + 1 if startdateWeekday >= overlapdWeekday else startdateWeekday - overlapdWeekday + 8
                    occurrence = (time_delta - gap) // 7 + 1
                case RecurrenceType.MONTHLY:
                    if activity.startDate.day <= overlap_end.day:
                        occurrence = overlap_end.month - overlap_start.month + 1
                    else:
                        occurrence = overlap_end.month - overlap_start.month
                case RecurrenceType.YEARLY:
                    if start_date.month > overlap_end.month:
                        occurrence = 0
                    elif start_date.month < overlap_end.month:
                        occurrence = 1
                    elif start_date.day <= overlap_end.day:
                        occurrence = 1
                    else:
                        occurrence = 0
                case _: 
                    occurrence = 0

            totalSpend += occurrence * activity.expense
    return SpendPublic(
        year=year,
        month=None,
        day=None,
        totalSpend=totalSpend
    )
                    
    

@router.get("/spending/month/{account_id}", response_model=SpendPublic)
def get_spending_in_date(*,
    account_id: int,
    category: Category | None = None,
    year: Annotated[int, Query(le=3000, ge=1800)], 
    month: Annotated[int, Query(le=12, ge=1)],
    session: SessionDep
):
    start_of_month = date(year=year, month=month, day=1)
    if (start_of_month > date.today()):
        return SpendPublic(
        year=year,
        month=month,
        totalSpend=0.0
    )
    today = date.today()
    end_of_month = date(year=year, month=month, day=monthrange(year,month)[1])
    end_of_month = end_of_month if end_of_month <= today else today

    statement = select(Activity).where(
        Activity.account_id == account_id,
        Activity.startDate <= end_of_month,
        or_(
            Activity.endDate == None, Activity.endDate >= start_of_month
        )
        )

    if category is not None:
        statement = statement.where(Activity.category == category)

    activities = session.exec(statement=statement).all()

    totalSpending = 0.0
    for activity in activities:
        activity_start = activity.startDate
        activity_end = activity.endDate if activity.endDate is not None else end_of_month
        
        overlapped_start = max(activity_start, start_of_month)
        overlapped_end = min(activity_end, end_of_month)

        if activity.recurrenceType == RecurrenceType.ONCE:
            if overlapped_start == activity_start:
                totalSpending += activity.expense
        else:
            occurrence = 0
            match activity.recurrenceType:
                case RecurrenceType.DAILY:
                    occurrence = (overlapped_end - overlapped_start).days + 1
                case RecurrenceType.WEEKLY:
                    time_delta = (overlapped_end - overlapped_start).days + 1
                    overlappedWeekday = overlapped_start.weekday()
                    startdateWeekday = activity_start.weekday()
                    gap = startdateWeekday - overlappedWeekday + 1 if startdateWeekday >= overlappedWeekday else startdateWeekday - overlappedWeekday + 8
                    occurrence = (time_delta - gap) // 7 + 1
                case RecurrenceType.MONTHLY:
                    occurrence = 1 if activity_start.day <= overlapped_end.day else 0
                case RecurrenceType.YEARLY:
                    occurrence = 1 if activity_start.month == month and activity_start.day <= overlapped_end.day else 0
                case _:
                    occurrence = 0

            totalSpending += occurrence * activity.expense

    return SpendPublic(
        year=year,
        month=month,
        totalSpend=totalSpending
    )



@router.get("/spending/date/{account_id}")
def get_spending_in_date(*,
    account_id: int,
    category: Category | None = None,
    year: Annotated[int, Query(le=3000, ge=1800)], 
    month: Annotated[int, Query(le=12, ge=1)],
    day: int,
    session: SessionDep
):
    try:
        mydate = date(year=year, month=month, day=day)
    except ValueError:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    if mydate > date.today():
        return SpendPublic(
            year=year,
            month=month,
            day=day,
            totalSpend=0.0
        )
    
    statement = select(Activity).where(
        Activity.account_id == account_id, 
        Activity.startDate <= mydate,
        or_(
            Activity.endDate == None,
            Activity.endDate > mydate
        )
    )

    if category is not None:
        statement = statement.where(Activity.category == category)
    activities = session.exec(statement=statement).all()

    totalSpend = 0.0
    for activity in activities:
        match activity.recurrenceType:
            case RecurrenceType.ONCE:
                if mydate == activity.startDate:
                    totalSpend += activity.expense
            case RecurrenceType.DAILY:
                    totalSpend += activity.expense
            case RecurrenceType.WEEKLY:
                if activity.startDate.weekday() == mydate.weekday():
                    totalSpend += activity.expense
            case RecurrenceType.MONTHLY:
                if activity.startDate.day == mydate.day:
                    totalSpend += activity.expense
            case RecurrenceType.YEARLY:
                if activity.startDate.month == mydate.month and activity.startDate.day == mydate.day:
                    totalSpend += activity.expense
    return SpendPublic(
        year=year,
        month=month,
        day=day,
        totalSpend=totalSpend
    )

    

    
    
