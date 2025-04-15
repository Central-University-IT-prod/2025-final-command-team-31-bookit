from fastapi import APIRouter, Request
from starlette.responses import Response

from cfg import *
from db import DB
from models.seats import *
from utilities import make_http_error

router = APIRouter()

@router.get("/admin/get_markers", status_code=200, description="Получить все места на этаже для админа")
async def admin_get_markers(request: Request):
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
        GetSeats.model_validate(body)
    except Exception as e:
        return make_http_error(400, "Ошибка в данных запроса")

    if not db.check_if_floor_exists(body["floor_id"]):
        return make_http_error(404, "Этот этаж не существует.")

    db.postgre_cur.execute("SELECT * FROM seats WHERE floor_id=%s", (body["floor_id"],))
    result = db.postgre_cur.fetchall()

    db.end()

    return [
        dict(i) for i in result
    ]


def check_uuid(uuid):
    try:
        if not UUID(uuid):
            return False
        return True
    except Exception as e:
        return False

@router.put("/admin/put_markers", status_code=204, description="Получить все места на этаже для админа")
async def admin_put_markers(request: Request):
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
        PutSeats.model_validate(body)
    except Exception as e:
        return make_http_error(400, "Ошибка в данных запроса")

    if not db.check_if_floor_exists(body["floor_id"]):
        return make_http_error(404, "Этот этаж не существует.")

    for i in body["seats"]:
        if "id" in i.keys() and i["id"] != None and db.check_if_seat_exists(i["id"]):
            db.postgre_cur.execute("UPDATE seats SET posx=%s, posy=%s, name=%s, onlyempl=%s, price_g=%s, price_e=%s WHERE id=%s",
                                   (i["posx"], i["posy"], i["name"], i["onlyempl"], i["price_g"], i["price_e"], i["id"]))
        else:
            db.postgre_cur.execute("INSERT INTO seats (posx, posy, name, onlyempl, price_g, price_e, floor_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                   (i["posx"], i["posy"], i["name"], i["onlyempl"], i["price_g"], i["price_e"], body["floor_id"]))

    db.postgre_con.commit()

    db.end()

    return Response(status_code=204)