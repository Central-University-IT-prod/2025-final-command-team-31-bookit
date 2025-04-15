import jwt
from fastapi import APIRouter, Depends, Request
from psycopg2 import IntegrityError
from starlette.responses import Response, JSONResponse

from cfg import ADMIN_ROLES
from db import DB
from models.users import User, UserPatch
from utilities import make_http_error

router = APIRouter()

@router.post("/add_admin", status_code=201)
async def add_admin(admin: User, request: Request):
    db = DB()

    token = str(request.headers.get("Authorization"))
    user = db.get_user_by_token(token)

    if not user:
        return make_http_error(403, "Токен некорректный")

    id = user['id']
    if not db.get_user_by_id(id):
        return make_http_error(404, "Пользователь не найден.")

    if db.get_user_by_id(id)["role"] != "SUPER_ADMIN":
        return make_http_error(403, "Пользователь не cупер админ")

    try:
        token = db.add_user(admin)

    except IntegrityError:
        db.get_postgres_con().rollback()
        raise make_http_error(400, "Этот логин уже занят.")

    return JSONResponse(status_code=201, content={"user_token": token})

@router.get("/user_info_all")
async def user_info_all(request: Request, limit: int = 10, offset: int = 1):
    db = DB()

    token = str(request.headers.get("Authorization"))
    user = db.get_user_by_token(token)
    if not user:
        return make_http_error(404, "Пользователь не найден.")

    if user['role'] in ADMIN_ROLES:
        data = db.get_all_users(limit, offset)
        if not data:
            return make_http_error(404, "юзер не найден")

        return JSONResponse(status_code=200, content=data)
    else:
        return make_http_error(403, "недостаточно прав для просмотра этого пользователя")

@router.get("/user_info/{UserId}", description='Для получения информации по юзеру для админов')
async def user_info(request: Request, UserId: str):
    db = DB()

    token = str(request.headers.get("Authorization"))
    user = db.get_user_by_token(token)
    if not user:
        return make_http_error(404, "Пользователь не найден.")
    if user['role'] in ADMIN_ROLES:
        data = db.get_user_by_id(UserId)
        if not data:
            return make_http_error(404, "юзер не найден")
        data.pop("password_hash", None)
        return JSONResponse(status_code=200, content=data)

    else:
        return make_http_error(403, "недостаточно прав для просмотра этого пользователя")


@router.get("/verify/{UserId}", description='Для верификации юзера (для админов)')
async def user_info(request: Request, UserId: str):
    db = DB()

    token = str(request.headers.get("Authorization"))
    user = db.get_user_by_token(token)
    if not user:
        return make_http_error(404, "Пользователь не найден.")
    if user['role'] in ADMIN_ROLES:
        db.verify_user(UserId)
        return JSONResponse(status_code=201, content="успешно верифицирован")

    else:
        return make_http_error(403, "недостаточно прав для верификации этого пользователя")

@router.get("/user_info/documents/paths/{UserId}")
async def get_doc(request: Request, UserId: str):
    dbcon = DB()
    token = str(request.headers.get("Authorization"))
    admin = dbcon.get_user_by_token(token)

    if not dbcon.get_user_by_id(UserId):
        return make_http_error(404, "Пользователь не найден.")

    if not admin:
        return make_http_error(403, "Токен некорректный")

    if admin["role"] not in ADMIN_ROLES:
        return make_http_error(403, "Пользователь не имеет доступа к этому документу")

    docs_names = dbcon.get_docs_by_user_id(UserId)

    return docs_names


class UniqueViolation:
    pass


@router.patch("/edit_user_data/{UserId}")
async def sign_up(request: Request, new_user: UserPatch, UserId: str):
    dbcon = DB()
    if new_user.role == "ADMIN":
        return JSONResponse(status_code=403, content="недостаточно прав: вы не супер админ")

    admin_token = str(request.headers.get("Authorization"))

    if not admin_token:
        return make_http_error(400, "токен не передан")

    admin = dbcon.get_user_by_token(admin_token)

    if admin['role'] not in ADMIN_ROLES:
        return make_http_error(403, "недостаточно прав")

    try:
        patch_user = dbcon.patch_user(new_user, UserId)

    except UniqueViolation:
        dbcon.get_postgres_con().rollback()
        return JSONResponse(status_code=409, content="логин уже занят")

    return JSONResponse(status_code=200, content=patch_user)