from fastapi import APIRouter, Depends, Request, UploadFile, File
from psycopg2 import IntegrityError
from starlette.responses import Response, JSONResponse

from cfg import *
from db import DB
from models.items import *
from utilities import make_http_error

import hashlib
import shutil
import uuid
import time
from pathlib import Path

router = APIRouter()


@router.get("/get_item", status_code=200, description="Получить доп опциию по id")
async def get_item(request: Request):
    db = DB()

    token = str(request.headers.get("Authorization"))
    user = db.get_user_by_token(token)

    if not user:
        return make_http_error(403, "Токен некорректный")

    id = user['id']
    if not db.get_user_by_id(id):
        return make_http_error(404, "Пользователь не найден.")

    body = await request.json()

    try:
        GetItem.model_validate(body)
    except Exception as e:
        return make_http_error(400, "Ошибка в данных запроса")

    if not db.check_if_item_exists(body["id"]):
        return make_http_error(404, "Такая доп опция не существует.")

    db.postgre_cur.execute("SELECT * FROM items WHERE id=%s LIMIT 1", (body["id"],))
    result = db.postgre_cur.fetchall()

    db.end()

    return dict(result)


@router.get("/get_items", status_code=200, description="Получить все доп опции по категориям для строения")
async def get_items(request: Request):
    db = DB()

    token = str(request.headers.get("Authorization"))
    user = db.get_user_by_token(token)

    if not user:
        return make_http_error(403, "Токен некорректный")

    id = user['id']
    if not db.get_user_by_id(id):
        return make_http_error(404, "Пользователь не найден.")

    body = await request.json()

    try:
        GetItems.model_validate(body)
    except Exception as e:
        return make_http_error(400, "Ошибка в данных запроса")

    resp = {
        "Еда": [],
        "Оборудование": []
    }

    db.postgre_cur.execute("SELECT * FROM items WHERE building_id=%s", (body["building_id"],))
    result = db.postgre_cur.fetchall()

    for i in result:
        resp[result["category"]].append(dict(i))

    db.end()

    return resp


@router.post("/add_item", status_code=201, description="Добавить доп опцию для строения")
async def add_item(request: Request):
    db = DB()

    token = str(request.headers.get("Authorization"))
    user = db.get_user_by_token(token)

    if not user:
        return make_http_error(403, "Токен некорректный")

    id = user['id']
    if not db.get_user_by_id(id):
        return make_http_error(404, "Пользователь не найден.")
    
    if db.get_user_by_id(id)["role"] not in ADMIN_ROLES:
        return make_http_error(403, "Пользователь не админ")

    body = await request.json()

    try:
        PostItem.model_validate(body)
    except Exception as e:
        return make_http_error(400, "Ошибка в данных запроса")

    db.postgre_cur.execute("INSERT INTO items (name, price, pricetype, category, building_id) VALUES (%s, %s, %s, %s, %s) RETURNING id;", (body["name"], body["price"], body["pricetype"], body["category"], body["building_id"]))
    db.postgre_con.commit()

    db.end()

    return {
        "id": db.postgre_cur.fetchone()[0]
    }


@router.delete("/delete_item", status_code=200, description="Удалить доп опциию по id")
async def delete_item(request: Request):
    db = DB()

    token = str(request.headers.get("Authorization"))
    user = db.get_user_by_token(token)

    if not user:
        return make_http_error(403, "Токен некорректный")

    id = user['id']
    if not db.get_user_by_id(id):
        return make_http_error(404, "Пользователь не найден.")
    
    if db.get_user_by_id(id)["role"] not in ADMIN_ROLES:
        return make_http_error(403, "Пользователь не админ")

    body = await request.json()

    try:
        DeleteItem.model_validate(body)
    except Exception as e:
        return make_http_error(400, "Ошибка в данных запроса")

    if not db.check_if_item_exists(body["id"]):
        return make_http_error(404, "Такая доп опция не существует.")

    db.postgre_cur.execute("DELETE FROM items WHERE id=%s", (body["id"],))

    db.end()

    return Response(status_code=204)


@router.patch("/patch_item", status_code=200, description="Изменить доп опциию по id")
async def patch_item(request: Request):
    db = DB()

    token = str(request.headers.get("Authorization"))
    user = db.get_user_by_token(token)

    if not user:
        return make_http_error(403, "Токен некорректный")

    id = user['id']
    if not db.get_user_by_id(id):
        return make_http_error(404, "Пользователь не найден.")
    
    if db.get_user_by_id(id)["role"] not in ADMIN_ROLES:
        return make_http_error(403, "Пользователь не админ")

    body = await request.json()

    try:
        PatchItem.model_validate(body)
    except Exception as e:
        return make_http_error(400, "Ошибка в данных запроса")

    if not db.check_if_item_exists(body["id"]):
        return make_http_error(404, "Такая доп опция не существует.")

    fields = [
        "name",
        "price",
        "pricetype",
        "category"
    ]
    for i in fields:
        if body[i] != None:
            db.postgre_cur.execute(f"UPDATE items SET {i}=%s WHERE id=%s", (body["id"],))

    db.postgre_con.commit()

    db.end()

    return Response(status_code=204)

@router.post("/add_item_image/{token}/{item_id}")
async def add_item_image(request: Request, token:Optional[str]="", item_id:Optional[str]=None,
                  image: UploadFile = File(...)):
    db = DB()

    user = db.get_user_by_token(token)

    if not user:
        return make_http_error(403, "Токен некорректный")
    
    if db.get_user_by_id(id)["role"] not in ADMIN_ROLES:
        return make_http_error(403, "Пользователь не админ")

    user_id = user['id']
    if not db.get_user_by_id(user_id):
        return make_http_error(404, "Пользователь не найден.")

    try:
        item_id = str(UUID(item_id))
    except Exception as e:
        return make_http_error(400, "Ошибка в данных запроса")

    db.postgre_cur.execute("SELECT image FROM items WHERE id=%s", (item_id,))
    old_image = db.postgre_cur.fetchone()[0]

    if old_image != None:
        os.remove(os.path.join(UPLOAD_DIR_IMGS, old_image))

    image.filename = item_id + Path(image.filename).suffix
    os.makedirs(UPLOAD_DIR_IMGS, exist_ok=True)
    avatar_file_location = os.path.join(UPLOAD_DIR_IMGS, image.filename)
    with open(avatar_file_location, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    db.postgre_cur.execute(
        "UPDATE items SET image = %s WHERE id = %s",
        (image.filename, item_id))
    db.postgre_con.commit()

    db.end()

    return JSONResponse(status_code=200, content="изображение загружено")