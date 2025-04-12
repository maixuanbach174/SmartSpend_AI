from typing import Annotated

from fastapi import Header, HTTPException


async def get_token_header(admin_token: Annotated[str, Header()]):
    if admin_token != "leducphu":
        raise HTTPException(status_code=400, detail=f"No token named {admin_token} provided")


async def get_query_token(token: str):
    if token != "maixuanbach":
        raise HTTPException(status_code=400, detail=f"No token named {token} provided")