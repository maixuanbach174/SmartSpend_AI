from fastapi import APIRouter
from sqlmodel import select

from ..core.db import SessionDep
from ..models import AbsoluteMonthlyActivityCreate, AbsoluteYearlyActivityCreate, Activity, ActivityPublic, DailyActivityCreate, OnceActivityCreate, RecurrencePattern, RecurrencePatternDay, RecurrencePatternDayPublic, RecurrencePatternPublic, RelativeMonthlyActivityCreate, RelativeYearlyActivityCreate, Schedule, RecurrenceType, SchedulePublic, WeeklyActivityCreate
# from ..models import Activity

router = APIRouter(
    prefix="/activity",
    tags=["Activity"],
)

@router.post("/once/{account_id}", response_model=ActivityPublic)
def create_new_once_activity(account_id: int, activity: OnceActivityCreate, session: SessionDep):
    activity_db = Activity.model_validate(activity)
    activity_db.account_id = account_id
    session.add(activity_db)
    session.commit()
    session.refresh(activity_db)
    return activity_db

@router.post("/daily/{account_id}", response_model=ActivityPublic)
def create_new_daily_activity(account_id: int, activity: DailyActivityCreate, session: SessionDep):
    # 1. Create RecurrencePattern
    recurrence_pattern_db = RecurrencePattern(
        **activity.schedule.schedule_pattern.model_dump(),
        type=RecurrenceType.DAILY
    )
    session.add(recurrence_pattern_db)
    session.flush()  # Generate pattern_id

    # 2. Create Schedule
    schedule_db = Schedule(
        **activity.schedule.model_dump(exclude={"schedule_pattern"}),
        account_id=account_id,
        pattern_id=recurrence_pattern_db.pattern_id
    )
    session.add(schedule_db)
    session.flush()

    # 3. Create Activity
    activity_db = Activity(
        **activity.model_dump(exclude={"schedule"}),
        account_id=account_id,
        schedule_id=schedule_db.schedule_id
    )
    session.add(activity_db)
    session.commit()

    # 4. Refresh all objects to load relationships
    session.refresh(recurrence_pattern_db)
    session.refresh(schedule_db)
    session.refresh(activity_db)

    # 5. Build the public response
    pattern_public = RecurrencePatternPublic(
        pattern_id=recurrence_pattern_db.pattern_id,
        type=recurrence_pattern_db.type,
        interval=recurrence_pattern_db.interval,
        daysOfWeek=None,  # Daily patterns don't need daysOfWeek
        month=recurrence_pattern_db.month,
        dayOfMonth=recurrence_pattern_db.dayOfMonth,
        index=recurrence_pattern_db.index
    )

    schedule_public = SchedulePublic(
        schedule_id=schedule_db.schedule_id,
        account_id=account_id,
        pattern_id=recurrence_pattern_db.pattern_id,
        is_active=schedule_db.is_active,
        start_date=schedule_db.start_date,
        end_date=schedule_db.end_date,
        start_time=schedule_db.start_time,
        end_time=schedule_db.end_time,
        pattern=pattern_public
    )

    return ActivityPublic(
        activity_id=activity_db.activity_id,
        account_id=account_id,
        name=activity_db.name,
        description=activity_db.description,
        expense=activity_db.expense,
        location=activity_db.location,
        category=activity_db.category,
        schedule_id=schedule_db.schedule_id,
        activity_schedule=schedule_public
    )

@router.post("/weekly/{account_id}", response_model=ActivityPublic)
def create_new_weekly_activity(account_id: int, activity: WeeklyActivityCreate, session: SessionDep):
    # 1. Create RecurrencePattern
    pattern_data = activity.schedule.schedule_pattern.model_dump(exclude={"daysOfWeek"})
    recurrence_pattern_db = RecurrencePattern(
        **pattern_data,
        type=RecurrenceType.WEEKLY
    )
    session.add(recurrence_pattern_db)
    session.flush()
    
    # 2. Add days of week
    days_of_week = []
    for day in activity.schedule.schedule_pattern.daysOfWeek:
        day_db = RecurrencePatternDay(
            pattern_id=recurrence_pattern_db.pattern_id,
            day=day.day
        )
        session.add(day_db)
        days_of_week.append(day_db)
    
    # 3. Create Schedule
    schedule_db = Schedule(
        **activity.schedule.model_dump(exclude={"schedule_pattern"}),
        account_id=account_id,
        pattern_id=recurrence_pattern_db.pattern_id
    )
    session.add(schedule_db)
    session.flush()

    # 4. Create Activity
    activity_db = Activity(
        **activity.model_dump(exclude={"schedule"}),
        account_id=account_id,
        schedule_id=schedule_db.schedule_id
    )
    session.add(activity_db)
    session.commit()

    # 5. Build response
    pattern_public = RecurrencePatternPublic(
        pattern_id=recurrence_pattern_db.pattern_id,
        type=recurrence_pattern_db.type,
        interval=recurrence_pattern_db.interval,
        daysOfWeek=[RecurrencePatternDayPublic(day=d.day, pattern_id=d.pattern_id) for d in days_of_week],
        month=recurrence_pattern_db.month,
        dayOfMonth=recurrence_pattern_db.dayOfMonth,
        index=recurrence_pattern_db.index
    )

    schedule_public = SchedulePublic(
        schedule_id=schedule_db.schedule_id,
        account_id=account_id,
        pattern_id=recurrence_pattern_db.pattern_id,
        is_active=schedule_db.is_active,
        start_date=schedule_db.start_date,
        end_date=schedule_db.end_date,
        start_time=schedule_db.start_time,
        end_time=schedule_db.end_time,
        pattern=pattern_public
    )

    return ActivityPublic(
        activity_id=activity_db.activity_id,
        account_id=account_id,
        name=activity_db.name,
        description=activity_db.description,
        expense=activity_db.expense,
        location=activity_db.location,
        category=activity_db.category,
        schedule_id=schedule_db.schedule_id,
        activity_schedule=schedule_public
    )

@router.post("/absolute-monthly/{account_id}")
def create_new_absolute_monthyly_activity(account_id: int, activity: AbsoluteMonthlyActivityCreate, session: SessionDep):
    # 1. Create RecurrencePattern
    recurrence_pattern_db = RecurrencePattern(
        **activity.schedule.schedule_pattern.model_dump(),
        type=RecurrenceType.ABSOLUTE_MONTHLY
    )

    session.add(recurrence_pattern_db)
    session.flush()
    
    # 2. Create Schedule
    schedule_db = Schedule(
        **activity.schedule.model_dump(exclude={"schedule_pattern"}),
        account_id=account_id,
        pattern_id=recurrence_pattern_db.pattern_id
    )

    session.add(schedule_db)
    session.flush()
    # 3. Create Activity
    activity_db = Activity(
        **activity.model_dump(exclude={"schedule"}),
        account_id=account_id,
        schedule_id=schedule_db.schedule_id
    )
    session.add(activity_db)
    session.commit()
    # 4. Refresh all objects to load relationships
    session.refresh(recurrence_pattern_db)
    session.refresh(schedule_db)
    session.refresh(activity_db)
    # 5. Build the public response
    pattern_public = RecurrencePatternPublic(
        pattern_id=recurrence_pattern_db.pattern_id,
        type=recurrence_pattern_db.type,
        interval=recurrence_pattern_db.interval,
        daysOfWeek=None,  # Monthly patterns don't need daysOfWeek
        month=recurrence_pattern_db.month,
        dayOfMonth=recurrence_pattern_db.dayOfMonth,
        index=recurrence_pattern_db.index
    )
    schedule_public = SchedulePublic(
        schedule_id=schedule_db.schedule_id,
        account_id=account_id,
        pattern_id=recurrence_pattern_db.pattern_id,
        is_active=schedule_db.is_active,
        start_date=schedule_db.start_date,
        end_date=schedule_db.end_date,
        start_time=schedule_db.start_time,
        end_time=schedule_db.end_time,
        pattern=pattern_public
    )
    return ActivityPublic(
        activity_id=activity_db.activity_id,
        account_id=account_id,
        name=activity_db.name,
        description=activity_db.description,
        expense=activity_db.expense,
        location=activity_db.location,
        category=activity_db.category,
        schedule_id=schedule_db.schedule_id,
        activity_schedule=schedule_public
    )


@router.post("/relative-monthly/{account_id}", response_model=ActivityPublic)
def create_new_relative_monthly_activity(
    account_id: int,
    activity: RelativeMonthlyActivityCreate,
    session: SessionDep
):
   # 1. Create RecurrencePattern (monthly relative)
    pattern_data = activity.schedule.schedule_pattern.model_dump()
    recurrence_pattern_db = RecurrencePattern(
        **{k: v for k, v in pattern_data.items() if k != 'daysOfWeek'},  # Exclude daysOfWeek
        type=RecurrenceType.RELATIVE_MONTHLY,
        month=None,  # Not used for relative monthly
        dayOfMonth=None  # Not used for relative monthly
    )
    session.add(recurrence_pattern_db)
    session.flush()

    # 2. Create days of week records
    for day in activity.schedule.schedule_pattern.daysOfWeek:
        day_db = RecurrencePatternDay(
            pattern_id=recurrence_pattern_db.pattern_id,
            day=day.day
        )
        session.add(day_db)

    # 3. Create Schedule
    schedule_db = Schedule(
        **activity.schedule.model_dump(exclude={"schedule_pattern"}),
        account_id=account_id,
        pattern_id=recurrence_pattern_db.pattern_id
    )
    session.add(schedule_db)
    session.flush()

    # 4. Create Activity
    activity_db = Activity(
        **activity.model_dump(exclude={"schedule"}),
        account_id=account_id,
        schedule_id=schedule_db.schedule_id
    )
    session.add(activity_db)
    session.commit()

    # 5. Refresh all objects and load relationships
    session.refresh(recurrence_pattern_db)
    session.refresh(schedule_db)
    session.refresh(activity_db)
    recurrence_pattern_db.daysOfWeek = session.exec(
        select(RecurrencePatternDay).where(
            RecurrencePatternDay.pattern_id == recurrence_pattern_db.pattern_id
        )
    ).all()

    # 6. Build the public response
    pattern_public = RecurrencePatternPublic(
        pattern_id=recurrence_pattern_db.pattern_id,
        type=recurrence_pattern_db.type,
        interval=recurrence_pattern_db.interval,
        index=recurrence_pattern_db.index,  # e.g., WeekIndex.SECOND
        daysOfWeek=recurrence_pattern_db.daysOfWeek,  # List of days (e.g., [TUESDAY])
        month=None,
        dayOfMonth=None
    )

    schedule_public = SchedulePublic(
        schedule_id=schedule_db.schedule_id,
        account_id=account_id,
        pattern_id=recurrence_pattern_db.pattern_id,
        is_active=schedule_db.is_active,
        start_date=schedule_db.start_date,
        end_date=schedule_db.end_date,
        start_time=schedule_db.start_time,
        end_time=schedule_db.end_time,
        pattern=pattern_public
    )

    return ActivityPublic(
        activity_id=activity_db.activity_id,
        account_id=account_id,
        name=activity_db.name,
        description=activity_db.description,
        expense=activity_db.expense,
        location=activity_db.location,
        category=activity_db.category,
        schedule_id=schedule_db.schedule_id,
        activity_schedule=schedule_public
    )
    

@router.post("/absolute-yearly/{account_id}", response_model=ActivityPublic)
def create_new_absolute_yearly_activity(
    account_id: int,
    activity: AbsoluteYearlyActivityCreate, 
    session: SessionDep
):
    # 1. Create RecurrencePattern (yearly absolute)
    pattern_data = activity.schedule.schedule_pattern.model_dump()
    recurrence_pattern_db = RecurrencePattern(
        **pattern_data,
        type=RecurrenceType.ABSOLUTE_YEARLY,
        index=None,  # Not used for absolute yearly
        daysOfWeek=None  # Not used for absolute yearly
    )
    session.add(recurrence_pattern_db)
    session.flush()

    # 2. Create Schedule
    schedule_db = Schedule(
        **activity.schedule.model_dump(exclude={"schedule_pattern"}),
        account_id=account_id,
        pattern_id=recurrence_pattern_db.pattern_id
    )
    session.add(schedule_db)
    session.flush()

    # 3. Create Activity
    activity_db = Activity(
        **activity.model_dump(exclude={"schedule"}),
        account_id=account_id,
        schedule_id=schedule_db.schedule_id
    )
    session.add(activity_db)
    session.commit()

    # 4. Refresh all objects
    session.refresh(recurrence_pattern_db)
    session.refresh(schedule_db)
    session.refresh(activity_db)

    # 5. Build the public response
    pattern_public = RecurrencePatternPublic(
        pattern_id=recurrence_pattern_db.pattern_id,
        type=recurrence_pattern_db.type,
        interval=recurrence_pattern_db.interval,
        month=recurrence_pattern_db.month,  # Specific month (1-12)
        dayOfMonth=recurrence_pattern_db.dayOfMonth,  # Specific day (1-31)
        index=None,
        daysOfWeek=None
    )

    schedule_public = SchedulePublic(
        schedule_id=schedule_db.schedule_id,
        account_id=account_id,
        pattern_id=recurrence_pattern_db.pattern_id,
        is_active=schedule_db.is_active,
        start_date=schedule_db.start_date,
        end_date=schedule_db.end_date,
        start_time=schedule_db.start_time,
        end_time=schedule_db.end_time,
        pattern=pattern_public
    )

    return ActivityPublic(
        activity_id=activity_db.activity_id,
        account_id=account_id,
        name=activity_db.name,
        description=activity_db.description,
        expense=activity_db.expense,
        location=activity_db.location,
        category=activity_db.category,
        schedule_id=schedule_db.schedule_id,
        activity_schedule=schedule_public
    )

@router.post("/relative-yearly/{account_id}", response_model=ActivityPublic)
def create_new_relative_yearly_activity(
    account_id: int,
    activity: RelativeYearlyActivityCreate,
    session: SessionDep
):
    # 1. Create RecurrencePattern (yearly relative)
    pattern_data = activity.schedule.schedule_pattern.model_dump()
    recurrence_pattern_db = RecurrencePattern(
        **{k: v for k, v in pattern_data.items() if k != 'daysOfWeek'},  # Exclude daysOfWeek
        type=RecurrenceType.RELATIVE_YEARLY,
        dayOfMonth=None,  # Not used for relative yearly
    )
    session.add(recurrence_pattern_db)
    session.flush()

    # 2. Create days of week records
    for day in activity.schedule.schedule_pattern.daysOfWeek:
        day_db = RecurrencePatternDay(
            pattern_id=recurrence_pattern_db.pattern_id,
            day=day.day
        )
        session.add(day_db)

    # 3. Create Schedule
    schedule_db = Schedule(
        **activity.schedule.model_dump(exclude={"schedule_pattern"}),
        account_id=account_id,
        pattern_id=recurrence_pattern_db.pattern_id
    )
    session.add(schedule_db)
    session.flush()

    # 4. Create Activity
    activity_db = Activity(
        **activity.model_dump(exclude={"schedule"}),
        account_id=account_id,
        schedule_id=schedule_db.schedule_id
    )
    session.add(activity_db)
    session.commit()

    # 5. Refresh all objects and load relationships
    session.refresh(recurrence_pattern_db)
    session.refresh(schedule_db)
    session.refresh(activity_db)
    recurrence_pattern_db.daysOfWeek = session.exec(
        select(RecurrencePatternDay).where(
            RecurrencePatternDay.pattern_id == recurrence_pattern_db.pattern_id
        )
    ).all()

    # 6. Build the public response
    pattern_public = RecurrencePatternPublic(
        pattern_id=recurrence_pattern_db.pattern_id,
        type=recurrence_pattern_db.type,
        interval=recurrence_pattern_db.interval,
        month=recurrence_pattern_db.month,  # Specific month (1-12)
        index=recurrence_pattern_db.index,  # e.g., WeekIndex.LAST
        daysOfWeek=recurrence_pattern_db.daysOfWeek,  # List of days (e.g., [FRIDAY])
        dayOfMonth=None
    )

    schedule_public = SchedulePublic(
        schedule_id=schedule_db.schedule_id,
        account_id=account_id,
        pattern_id=recurrence_pattern_db.pattern_id,
        is_active=schedule_db.is_active,
        start_date=schedule_db.start_date,
        end_date=schedule_db.end_date,
        start_time=schedule_db.start_time,
        end_time=schedule_db.end_time,
        pattern=pattern_public
    )

    return ActivityPublic(
        activity_id=activity_db.activity_id,
        account_id=account_id,
        name=activity_db.name,
        description=activity_db.description,
        expense=activity_db.expense,
        location=activity_db.location,
        category=activity_db.category,
        schedule_id=schedule_db.schedule_id,
        activity_schedule=schedule_public
    )