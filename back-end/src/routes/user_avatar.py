import os

from fastapi import Request, UploadFile, File, APIRouter, status
from starlette.responses import JSONResponse, FileResponse, Response
from typing import Optional

from cfg import *
from db import DB
from utilities import make_http_error

router = APIRouter()

@router.get("/avatar", description='Для получения аватара по токену для юзера')
async def user_info(request: Request):
    dbcon = DB()
    token = str(request.headers.get("Authorization"))
    user = dbcon.get_user_by_token(token)
    if not user:
        return make_http_error(404, "Пользователь не найден.")

    file_path = UPLOAD_DIR_AVATAR + "/" + dbcon.get_avatar_by_user_id(user['id'])[0]
    if not os.path.isfile(file_path):
        return make_http_error(404, "аватар не загружен")

    return FileResponse(file_path, filename=os.path.basename(file_path))

@router.post("/avatar")
async def sign_up_avatar(request: Request,
                  avatar: UploadFile = File(...)):
    dbcon = DB()
    token = str(request.headers.get("Authorization"))
    user = dbcon.get_user_by_token(token)

    if not user:
        return make_http_error(403, "Токен некорректный")

    user_id = user['id']
    if not dbcon.get_user_by_id(user_id):
        return make_http_error(404, "Пользователь не найден.")

    dbcon.add_avatar(avatar, user_id)
    return JSONResponse(status_code=200, content="аватар загружен")

@router.get("/docs/{token}/{image}")
async def get_doc(request:Request, response:Response, token:Optional[str]="", image:Optional[str]=None):
    dbcon = DB()
    user = dbcon.get_user_by_token(token)

    if not user:
        return make_http_error(403, "Токен некорректный")

    user_id = user['id']
    if not dbcon.get_user_by_id(user_id):
        return make_http_error(404, "Пользователь не найден.")

    if user["image"] != image and user["role"] not in ADMIN_ROLES:
        return make_http_error(403, "Нет доступа к этому аватару")
    
    if not os.path.isfile(f"{UPLOAD_DIR_AVATAR}/{image}"):
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Аватар не найден." }
    
    return FileResponse(f"{UPLOAD_DIR_AVATAR}/{image}")