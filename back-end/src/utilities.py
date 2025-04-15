from fastapi import Request, HTTPException, Header
from starlette.responses import JSONResponse

from db import DB


def check_if_admin(token: str, db: DB) -> bool:

    user = db.get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=404, detail="юзер не найден")

    if user["role"] not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="недостаточно прав для добавления адреса")

    return True


def make_http_error(code, text):
    return JSONResponse(
        status_code=code,
        content={
            "message": text
        })