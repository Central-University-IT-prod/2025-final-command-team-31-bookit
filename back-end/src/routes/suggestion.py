from fastapi import APIRouter, Request

from cfg import *
from db import DB
from models.suggestions import *
from utilities import make_http_error

router = APIRouter()

@router.get("/get_suggestions", status_code=200, description="Получить все предложения по комментариям для строения")
async def get_suggestions(request: Request):
    db = DB()

    body = await request.json()

    try:
        GetSuggestion.model_validate(body)
    except Exception as e:
        return make_http_error(400, "Ошибка в данных запроса")

    db = DB()

    db.postgre_cur.execute("SELECT * FROM suggestions WHERE building_id=%s", (body["building_id"],))
    result = db.postgre_cur.fetchall()

    db.end()

    return [
        i["txt"] for i in result
    ]

@router.put("/put_suggestions", status_code=200, description="Обновить предложения по комментариям для строения")
async def put_suggestions(request: Request):
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
        PutSuggestions.model_validate(body)
    except Exception as e:
        return make_http_error(400, "Ошибка в данных запроса")

    db.postgre_cur.execute("DELETE FROM suggestions WHERE building_id=%s", (body["building_id"],))

    for i in body["txt"]:
        db.postgre_cur.execute("INSERT INTO suggestions (building_id, txt) VALUES (%s, %s)", (body["building_id"], i))

    db.postgre_con.commit()

    db.postgre_cur.execute("SELECT * FROM suggestions WHERE building_id=%s", (body["building_id"],))
    result = db.postgre_cur.fetchall()

    db.end()

    return [
        i["txt"] for i in result
    ]