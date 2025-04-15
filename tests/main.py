# ПЕРЕД ПУСКОМ НУЖНО СНЕСТИ БД!

# Мы умеем писать тесты! у нас на это нет времени.

from utils import *
import os
import random
import json

disable_logger_info(True)

PROTO = "http"
BASE_URL = "REDACTED"
NAME = "Main API"

# SIGN_IN
test(METHOD_POST, f"{PROTO}://{BASE_URL}/api/sign_in", f"{NAME} - /sign_in - Норм", body={
    "login": "admin",
    "password": "admin",
    "remember_me": False,
})
token = get_last_return_body()["user_token"]

# SIGN_UP
test(METHOD_POST, f"{PROTO}://{BASE_URL}/api/sign_up", f"{NAME} - /sign_up - Норм", body={
  "role": "EMPLOYEE",
  "login": "89899-0",
  "name": "John",
  "surname": "Doe",
  "second_name": "Middle",
  "email": "ззз",
  "password": "string",
  "contacts": "some contact info"
}, expected_code=201)

try:
    token_for_logout_test = get_last_return_body()["user_token"]
except:
    print("тест на завершении не прошел, попробуйте позже.")

test(METHOD_POST, f"{PROTO}://{BASE_URL}/api/sign_up", f"{NAME} - /sign_up - Повтор логина", body={
  "role": "EMPLOYEE",
  "login": "89899-0",
  "name": "Chill",
  "surname": "Guy",
  "second_name": "Middle",
  "email": "ззз",
  "password": "string",
  "contacts": "some contact info"
}, expected_code=409)

test(METHOD_POST, f"{PROTO}://{BASE_URL}/api/sign_up", f"{NAME} - /sign_up - Логин под супер админом", body={
  "role": "SUPER_ADMIN",
  "login": "coolhacker",
  "name": "кулхацкер",
  "surname": "пытаюсь регаться под супер админом))00))",
  "second_name": "Middle",
  "email": "ззз",
  "password": "string",
  "contacts": "some contact info"
}, expected_code=403)

test(METHOD_POST, f"{PROTO}://{BASE_URL}/api/sign_up", f"{NAME} - /sign_up - Логин под админом", body={
  "role": "ADMIN",
  "login": "coolhacker",
  "name": "кулхацкер",
  "surname": "пытаюсь регаться под админом))00))",
  "second_name": "Middle",
  "email": "ззз",
  "password": "string",
  "contacts": "some contact info"
}, expected_code=403)
# token = get_last_return_body()["user_token"]

#LOGOUT
test(METHOD_POST, f"{PROTO}://{BASE_URL}/api/sign_out", f"{NAME} - /sign_out - выход", body={}, headers={"Authorization": token_for_logout_test}, expected_code=200)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/api/sign_out", f"{NAME} - /sign_out - выход по токену который уже вышел", body={}, headers={"Authorization": token_for_logout_test}, expected_code=404)

# ADDRESSES
test(METHOD_POST, f"{PROTO}://{BASE_URL}/api/addresses/add", f"{NAME} - /addresses/add - Без данных", expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/api/addresses/add", f"{NAME} - /addresses/add - Пустые данные", body={}, expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/api/addresses/add", f"{NAME} - /addresses/add - Плохие данные", body={
    "name": None,
    "lat": None,
    "lon": None
}, expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/api/addresses/add", f"{NAME} - /addresses/add - Верный запрос", body={
    "name": "Коворк 1",
    "lat": 60,
    "lon": 50
}, expected_code=201)

test(METHOD_GET, f"{PROTO}://{BASE_URL}/api/addresses/all", f"{NAME} - /addresses/all - Верный запрос", expected_body=[{
    "name": "Коворк 1",
    "lat": 60,
    "lon": 50
}], expected_code=200)
adr_id = get_last_return_body()[0]["id"]

# BUILDINGS
test(METHOD_POST, f"{PROTO}://{BASE_URL}/api/buildings/add", f"{NAME} - /addresses/add - Без данных", expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/api/buildings/add", f"{NAME} - /addresses/add - Пустые данные", body={}, expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/api/buildings/add", f"{NAME} - /addresses/add - Плохие данные", data={"building_data": json.dumps({
    "name": "Тест",
    "address_id": get_random_uuid(),
    "t_from": [0,0,0,0,0,0,0],
    "t_to": [1,1,1,1,1,1,1]
})}, files={
    "img": open("Screenshot_140.png", "rb")
}, expected_code=404)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/api/buildings/add", f"{NAME} - /addresses/add - Плохие данные", data={"building_data": json.dumps({
    "name": "Тест",
    "address_id": get_random_uuid(),
    "t_from": [0,0,0,0,0,0,0],
    "t_to": [1,1,1,1,1,1]
})}, files={
    "img": open("Screenshot_140.png", "rb")
}, expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/api/buildings/add", f"{NAME} - /addresses/add - Плохие данные", data={"building_data": json.dumps({
    "name": "Тест",
    "address_id": adr_id,
    "t_from": [0,0,0,0,0,0,0],
    "t_to": [1,1,1,1,1,1,1]
})}, files={
    "img": open("Screenshot_140.png", "rb")
}, expected_code=201)
b_id = get_last_return_body()["uuid"]

test(METHOD_GET, f"{PROTO}://{BASE_URL}/api/buildings/{b_id}", f"{NAME} - /addresses/id - Норм", expected_body={
    "id": b_id,
    "name": "Тест",
    "addr_id": adr_id,
    "t_from": [0,0,0,0,0,0,0],
    "t_to": [1,1,1,1,1,1,1]
}, expected_code=200)
b_img = get_last_return_body()["img"]

test(METHOD_GET, f"{PROTO}://{BASE_URL}/api/buildings/image/{b_img}", f"{NAME} - /addresses/image - Норм", expected_code=200)

# FLOORS
test(METHOD_POST, f"{PROTO}://{BASE_URL}/api/floors/add", f"{NAME} - /floors/add - Норм", data={"floor_create": json.dumps({
    "building_id": b_id,
    "number": 1
})}, files={
    "img": open("testplan.jpg", "rb")
}, expected_code=201)
fl_id = get_last_return_body()["uuid"]

test(METHOD_GET, f"{PROTO}://{BASE_URL}/api/floors/{fl_id}", f"{NAME} - /floors/get - Норм", expected_body={
    "building_id": b_id,
    "number": 1
}, expected_code=200)
img = get_last_return_body()["img"]

test(METHOD_GET, f"{PROTO}://{BASE_URL}/api/floors/image/{img}", f"{NAME} - /floors/img - Норм", expected_code=200)

test(METHOD_DELETE, f"{PROTO}://{BASE_URL}/api/floors/delete/{fl_id}", f"{NAME} - /floors/delete - Норм", expected_code=204)

test(METHOD_GET, f"{PROTO}://{BASE_URL}/api/floors/{fl_id}", f"{NAME} - /floors/get - Норм", expected_code=404)

test(METHOD_POST, f"{PROTO}://{BASE_URL}/api/floors/add", f"{NAME} - /floors/add - Норм", data={"floor_create": json.dumps({
    "building_id": b_id,
    "number": 1
})}, files={
    "img": open("testplan.jpg", "rb")
}, expected_code=201)
fl_id = get_last_return_body()["uuid"]

# SUGGESTIONS
test(METHOD_GET, f"{PROTO}://{BASE_URL}/api/get_suggestions", f"{NAME} - /get_suggestions - Норм", body={
    "building_id": b_id
}, expected_body=[], expected_code=200)

sug = [
    "тест 1",
    "тест 2",
    "тест 3",
]

test(METHOD_PUT, f"{PROTO}://{BASE_URL}/api/put_suggestions", f"{NAME} - /put_suggestions - Норм", body={
    "building_id": b_id,
    "txt": sug,
}, expected_body=sug, headers={
    "Authorization": token
}, expected_code=200)

test(METHOD_GET, f"{PROTO}://{BASE_URL}/api/get_suggestions", f"{NAME} - /get_suggestions - Норм", body={
    "building_id": b_id
}, expected_body=sug, expected_code=200)

# SEATS
test(METHOD_GET, f"{PROTO}://{BASE_URL}/api/admin/get_markers", f"{NAME} - /get_markers - Норм", body={
    "floor_id": fl_id
}, headers={
    "Authorization": token
}, expected_body=[], expected_code=200)

test(METHOD_PUT, f"{PROTO}://{BASE_URL}/api/admin/put_markers", f"{NAME} - /put_markers - Норм", body={
    "floor_id": fl_id,
    "seats": [
        {
            "posx": .6,
            "posy": .6,
            "name": "Место 1",
            "onlyempl": False,
            "price_g": 100,
            "price_e": 50,
        },
        {
            "posx": .7,
            "posy": .7,
            "name": "Место 2",
            "onlyempl": False,
            "price_g": 100,
            "price_e": 50,
        }
    ]
}, headers={
    "Authorization": token
}, expected_code=204)

test(METHOD_GET, f"{PROTO}://{BASE_URL}/api/admin/get_markers", f"{NAME} - /get_markers - Норм", body={
    "floor_id": fl_id
}, headers={
    "Authorization": token
}, expected_body=[
    {
        "posx": .6,
        "posy": .6,
        "name": "Место 1",
        "onlyempl": False,
        "price_g": 100,
        "price_e": 50,
    },
    {
        "posx": .7,
        "posy": .7,
        "name": "Место 2",
        "onlyempl": False,
        "price_g": 100,
        "price_e": 50,
    }
], expected_code=200)

summary()