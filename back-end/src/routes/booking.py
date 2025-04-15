from fastapi import APIRouter, Depends, Request, UploadFile, File
from psycopg2 import IntegrityError
from starlette.responses import Response, JSONResponse

from cfg import *
from db import DB
from models.booking import *
from utilities import make_http_error

import hashlib
import shutil
import uuid
import time
from pathlib import Path

router = APIRouter()

def check_collision(t1start, t1end, t2start, t2end):
    return (
        (t2start < t1start and t1start < t2end) or
        (t2start < t1end and t1end < t2end) or
        (t1start < t2start and t2start < t1end) or
        (t1start < t2end and t2end < t1end)
    )

def get_collisions(booked, trying):
    collisions = []
    for i in trying:
        for j in booked:
            t1start = i[0]
            t1end = i[1]
            t2start = j[0]
            t2end = j[1]
            if check_collision(t1start, t1end, t2start, t2end):
                collisions.append([t2start, t2end])
    return collisions

@router.post("/booking/get_seats", status_code=200, description="Получить все места с статусом доступности для конкретных временных периудов")
async def get_seats(request: Request):
    try:
        db = DB()

        token = str(request.headers.get("Authorization"))
        user = db.get_user_by_token(token)

        if not user:
            return make_http_error(403, "Токен некорректный")

        id = user['id']
        if not db.get_user_by_id(id):
            return make_http_error(404, "Пользователь не найден.")

        try:
            body = await request.json()
        except Exception as e:
            return make_http_error(400, "Ошибка в данных запроса")

        try:
            GetSeats.model_validate(body)
        except Exception as e:
            return make_http_error(400, "Ошибка в данных запроса")
        
        db.postgre_cur.execute("SELECT * FROM seats WHERE floor_id=%s", (body["floor_id"],))
        seats = db.postgre_cur.fetchall()

        resp = []

        for i in seats:
            if i["onlyempl"] and user["role"] == "GUEST": continue
            db.postgre_cur.execute("SELECT t_from, t_to FROM book_items WHERE seat_id=%s", (i["id"]))
            booked = db.postgre_cur.fetchall()
            col = get_collisions(booked, [ [j["t_from"], j["t_to"]] for j in body["times"] ])
            stat = "empty" if len(col) == 0 else "full"
            seats.append({
                "id": i["id"],
                "posx": i["posx"],
                "posy": i["posy"],
                "name": i["name"],
                "price": i[db.role_to_price_field[user["role"]]],
                "status": stat,
                "collisions": col
            })

        return resp
    except Exception as e:
        return make_http_error(400, "Ошибка в данных запроса")

@router.post("/booking/book_one", status_code=200, description="Забронировать 1 место")
async def book_one(request: Request):
    try:
        # TODO: ВАЛИДАЦИЯ!!!
        db = DB()

        token = str(request.headers.get("Authorization"))
        user = db.get_user_by_token(token)

        if not user:
            return make_http_error(403, "Токен некорректный")

        id = user['id']
        if not db.get_user_by_id(id):
            return make_http_error(404, "Пользователь не найден.")

        try:
            body = await request.json()
        except Exception as e:
            return make_http_error(400, "Ошибка в данных запроса")

        try:
            BookOne.model_validate(body)
        except Exception as e:
            return make_http_error(400, "Ошибка в данных запроса")
        
        db.postgre_cur.execute("SELECT * FROM seats WHERE id=%s", (body["seat_id"],))
        seat = db.postgre_cur.fetchone()

        order_details = []

        book_time = 0
        for i in body["times"]:
            t_s = i["t_to"] - i["t_from"]
            book_time += t_s / 3600
        
        seat_price = book_time * seat[db.role_to_price_field[user["role"]]]
        seat_price = round(seat_price)

        order_details.append({
            "name": "Бронирование места",
            "price": seat_price,
            "pricetype": "perhour",
            "quantity": 1,
        })

        items_price = 0
        for i in body["items"]:
            db.postgre_cur.execute("SELECT * FROM items WHERE id=%s", (i["item_id"],))
            item = db.postgre_cur.fetchone()
            item_price = item["price"] * i["qty"]
            if item["pricetype"] == "perhour":
                item_price *= book_time
            item_price = round(item_price)

            order_details.append({
                "name": item["name"],
                "price": item_price,
                "pricetype": item["pricetype"],
                "quantity": i["qty"],
            })

            items_price += item_price
        
        price = seat_price + items_price

        db.postgre_cur.execute("INSERT INTO bookings (user_id, seat_id, comment, active, price) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                            (user["id"], [body["seat_id"]], body["comment"], True, price))
        booking_id = db.postgre_cur.fetchone()[0]

        for i in body["times"]:
            db.postgre_cur.execute("INSERT INTO book_times (booking_id, t_from, t_to, seat_id) VALUES (%s, %s, %s, %s)",
                                    (booking_id, i["t_from"], i["t_to"], body["seat_id"]))
        
        for i in order_details:
            db.postgre_cur.execute("INSERT INTO order_details (name, booking_id, price, pricetype, quantity) VALUES (%s, %s, %s, %s, %s)",
                                (i["name"], booking_id, i["price"], i["pricetype"], i["quantity"]))
        
        db.postgre_cur.execute("""INSERT INTO history (t_from, t_to, price, comment, user_id, seat_id, group_users, group_id, items_id) VALUES
                            (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                [ i["t_from"] for i in body["times"] ],
                [ i["t_to"] for i in body["times"] ],
                price,
                body["comment"],
                body["user_id"],
                body["seat_id"],
                None,
                None,
                [ i["item_id"] for i in body["items"] ]
            )
        )

        db.postgre_con.commit()

        return booking_id
    except Exception as e:
        return make_http_error(400, "Ошибка в данных запроса")

@router.post("/booking/book_group", status_code=200, description="Забронировать места на группу")
async def book_group(request: Request):
    try:
        # TODO: ВАЛИДАЦИЯ!!!
        db = DB()

        token = str(request.headers.get("Authorization"))
        user = db.get_user_by_token(token)

        if not user:
            return make_http_error(403, "Токен некорректный")

        id = user['id']
        if not db.get_user_by_id(id):
            return make_http_error(404, "Пользователь не найден.")

        try:
            body = await request.json()
        except Exception as e:
            return make_http_error(400, "Ошибка в данных запроса")

        try:
            BookGroup.model_validate(body)
        except Exception as e:
            return make_http_error(400, "Ошибка в данных запроса")

        order_details = []

        book_time = 0
        for i in body["times"]:
            t_s = i["t_to"] - i["t_from"]
            book_time += t_s / 3600

        seats_price = 0
        
        for i in body["seats"]:
            db.postgre_cur.execute("SELECT * FROM seats WHERE id=%s", (i["seat_id"],))
            seat = db.postgre_cur.fetchone()

            suser = db.get_user_by_id(i["user_id"])

            seat_price = book_time * seat[db.role_to_price_field[suser["role"]]]
            seat_price = round(seat_price)

            order_details.append({
                "name": f"Бронирование места {seat['name']}",
                "price": seat_price,
                "pricetype": "perhour",
                "quantity": 1,
            })

            seats_price += seat_price

        items_price = 0
        for i in body["items"]:
            db.postgre_cur.execute("SELECT * FROM items WHERE id=%s", (i["item_id"],))
            item = db.postgre_cur.fetchone()
            item_price = item["price"] * i["qty"]
            if item["pricetype"] == "perhour":
                item_price *= book_time
            item_price = round(item_price)

            order_details.append({
                "name": item["name"],
                "price": item_price,
                "pricetype": item["pricetype"],
                "quantity": i["qty"],
            })

            items_price += item_price
        
        price = seats_price + items_price

        db.postgre_cur.execute("SELECT * FROM groups_members WHERE group_id=%s",
                            (body["group_id"],))
        group_members = db.postgre_cur.fetchall()

        db.postgre_cur.execute("INSERT INTO bookings (user_id, seat_id, comment, active, price) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                            (user["id"], [body["seat_id"]], body["comment"], True, price))
        booking_id = db.postgre_cur.fetchone()[0]

        for j in body["seats"]:
            for i in body["times"]:
                db.postgre_cur.execute("INSERT INTO book_times (booking_id, t_from, t_to, seat_id) VALUES (%s, %s, %s, %s)",
                                        (booking_id, i["t_from"], i["t_to"], j["seat_id"]))
        
        for i in order_details:
            db.postgre_cur.execute("INSERT INTO order_details (name, booking_id, price, pricetype, quantity) VALUES (%s, %s, %s, %s, %s)",
                                (i["name"], booking_id, i["price"], i["pricetype"], i["quantity"]))
        
        db.postgre_cur.execute("""INSERT INTO history (t_from, t_to, price, comment, user_id, seat_id, group_users, group_id, items_id) VALUES
                            (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                [ i["t_from"] for i in body["times"] ],
                [ i["t_to"] for i in body["times"] ],
                price,
                body["comment"],
                body["user_id"],
                body["seat_id"],
                [ i["user_id"] for i in group_members ],
                body["group_id"],
                [ i["item_id"] for i in body["items"] ]
            )
        )

        for i in group_members:
            if i["user_id"] == id: continue
            db.postgre_cur.execute("""INSERT INTO bookings (user_id, seat_id, is_group, parent) VALUES (%s, %s, %s, %s)""",
                                    (
                                        i["user_id"],
                                        i["seat_id"],
                                        True,
                                        booking_id
                                    ))

        db.postgre_con.commit()

        return booking_id
    except Exception as e:
        return make_http_error(400, "Ошибка в данных запроса")

@router.post("/booking/calc_price", status_code=200, description="Посчитать цену на бронирование")
async def calc_price(request: Request):
    try:
        # TODO: ВАЛИДАЦИЯ!!!
        db = DB()

        token = str(request.headers.get("Authorization"))
        user = db.get_user_by_token(token)

        if not user:
            return make_http_error(403, "Токен некорректный")

        id = user['id']
        if not db.get_user_by_id(id):
            return make_http_error(404, "Пользователь не найден.")

        try:
            body = await request.json()
        except Exception as e:
            return make_http_error(400, "Ошибка в данных запроса")

        try:
            BookGroup.model_validate(body)
        except Exception as e:
            return make_http_error(400, "Ошибка в данных запроса")
        
        book_time = 0
        for i in body["times"]:
            t_s = i["t_to"] - i["t_from"]
            book_time += t_s / 3600

        seats_price = 0
        
        for i in body["seats"]:
            db.postgre_cur.execute("SELECT * FROM seats WHERE id=%s", (i["seat_id"],))
            seat = db.postgre_cur.fetchone()

            suser = db.get_user_by_id(i["user_id"])

            seat_price = book_time * seat[db.role_to_price_field[suser["role"]]]
            seat_price = round(seat_price)

            seats_price += seat_price

        items_price = 0
        for i in body["items"]:
            db.postgre_cur.execute("SELECT * FROM items WHERE id=%s", (i["item_id"],))
            item = db.postgre_cur.fetchone()
            item_price = item["price"] * i["qty"]
            if item["pricetype"] == "perhour":
                item_price *= book_time
            item_price = round(item_price)

            items_price += item_price
        
        price = seats_price + items_price

        return {
            "price": price
        }
    except Exception as e:
        return make_http_error(400, "Ошибка в данных запроса")