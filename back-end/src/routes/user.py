import json
from psycopg2.errors import UniqueViolation
from fastapi import APIRouter, Request, UploadFile, File, Query
from starlette.responses import JSONResponse

from db import DB
from models.users import SignIn, User, UserPatch
from utilities import make_http_error

from typing import Optional
from io import BytesIO
import qrcode
from starlette.responses import StreamingResponse

router = APIRouter()

@router.post("/sign_in")
async def sign_in(sign_in: SignIn, remember_me: bool = Query(default=False, alias="remember_me")):
    dbcon = DB()
    res = dbcon.get_user_by_logpass(sign_in.login, sign_in.password, remember_me)
    if res:
        token, user = res
        role = user["role"]
        return JSONResponse(status_code=200, content={"user_token": token, "role": role})

    else:
        return make_http_error(401, "Неверный email или пароль.")

@router.post("/sign_up")
async def sign_up(user: User):
    dbcon = DB()
    if user.role == "SUPER_ADMIN" or user.role == "ADMIN":
        return JSONResponse(status_code=403, content="админы не могут зарегистрироваться сами")

    try:
        token = dbcon.add_user(user)
    except UniqueViolation:
        dbcon.get_postgres_con().rollback()
        return JSONResponse(status_code=409, content="логин уже занят.")

    return JSONResponse(status_code=201, content={"user_token": token, "user_id": dbcon.get_user_by_token(token)["id"]})

@router.get("/user_info", description='Для получения информации по юзеру по токену для юзера')
async def user_info(request: Request):
    dbcon = DB()
    token = str(request.headers.get("Authorization"))
    user = dbcon.get_user_by_token(token)
    if not user:
        return make_http_error(404, "Пользователь не найден.")

    data = dbcon.get_user_by_id(user['id'])
    if not data:
        return make_http_error(404, "юзер не найден")
    data.pop("password_hash", None)
    return JSONResponse(status_code=200, content=data)

@router.post("/group")
async def create_group(user_logins: list[str], group_name: str, request: Request):
    dbcon = DB()
    owner_token = str(request.headers.get("Authorization"))
    owner = dbcon.get_user_by_token(owner_token)
    if not owner:
        return make_http_error(404, "пользователь с таким токеном не найден")
    owner_id = owner['id']
    group_id = dbcon.add_group(owner_id, user_logins, group_name)
    if group_id:
        return JSONResponse(status_code=201, content={'group_id': group_id})
    else:
        return make_http_error(400, "Невозможно создать группу с такими логинами.")

@router.get("/group/{group_id}")
async def get_group(group_id: str, request: Request):
    dbcon = DB()
    owner_token = str(request.headers.get("Authorization"))
    owner = dbcon.get_user_by_token(owner_token)
    group_str = dbcon.get_group_by_id(group_id)
    if not group_str:
        return make_http_error(404, "Группа не найдена.")
    if not owner:
        return make_http_error(404, "Юзер не найден (токен некорректный или просрочен)")
    group = json.loads(group_str)
    if owner['id'] == group['group_owner']['id'] or owner['role'] == 'ADMIN' or owner['role'] == 'SUPER_ADMIN':
        return JSONResponse(status_code=200, content=group)

@router.post("/sign_out")
async def sign_in(request: Request):
    dbcon = DB()

    user_token = str(request.headers.get("Authorization"))
    if not user_token:
        return make_http_error(400, "токен не передан")

    res = dbcon.sign_out(user_token)
    print(res)
    if not res:
        return make_http_error(404, "пользователь с таким токеном не найден")

    return JSONResponse(status_code=200, content={"message": "выход из системы успешный"})

@router.patch("/edit_user_data")
async def sign_up(request: Request, new_user: UserPatch):
    dbcon = DB()
    if new_user.role == "SUPER_ADMIN" or new_user.role == "ADMIN":
        return JSONResponse(status_code=403, content="админы не могут зарегистрироваться сами")

    user_token = str(request.headers.get("Authorization"))

    if not user_token:
        return make_http_error(400, "токен не передан")
    user = dbcon.get_user_by_token(user_token)

    if not user:
        return make_http_error(404, "пользователь с таким токеном не найден")

    try:
        patch_user = dbcon.patch_user(new_user, user['id'])

    except UniqueViolation:
        dbcon.get_postgres_con().rollback()
        return JSONResponse(status_code=409, content="логин уже занят.")
    # patch_user["second_name"] = patch_user.pop("secondname")
    return JSONResponse(status_code=200, content=patch_user)

@router.get("/qrcode")
async def get_qrcode(request: Request):
    db = DB()
    token = str(request.headers.get("Authorization"))
    user = db.get_user_by_token(token)

    if not user:
        return make_http_error(403, "Токен некорректный")

    id = user['id']
    if not db.get_user_by_id(id):
        return make_http_error(404, "Пользователь не найден.")
    
    db.end()

    img = qrcode.make(user["qr_code"])
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/jpeg")