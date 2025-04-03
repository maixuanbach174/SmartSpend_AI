from fastapi import APIRouter, HTTPException
from sqlmodel import select
from typing import Annotated
from app.models import Hero, HeroCreate, HeroPublic, HeroUpdate
from app.core.db import SessionDep
from fastapi import Query

router = APIRouter()

@router.post("/heroes/", response_model=HeroPublic)
async def create_hero(hero: HeroCreate, session: SessionDep):
    hero = Hero.model_validate(hero)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero

@router.get("/heroes/", response_model=list[HeroPublic])
async def read_heroes(
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=0, le=100)] = 10
):
    statement = select(Hero).offset(offset).limit(limit)
    results = session.exec(statement).all()
    return results

@router.get("/heroes/{hero_id}", response_model=HeroPublic)
async def read_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

@router.delete("/heroes/{hero_id}", status_code=204)
async def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"OK": True}

@router.patch("/heroes/{hero_id}", response_model=HeroPublic)
async def update_hero(hero_id: int, hero_update: HeroUpdate, session: SessionDep):
    db_hero = session.get(Hero, hero_id)
    if not db_hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    hero_data = hero_update.model_dump(exclude_unset=True)
    db_hero = db_hero.sqlmodel_update(hero_data)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero