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

hour = 60 * 60

@router.post("/testing_stuff", status_code=200, description="Заполнить тестовые данные")
async def testing_stuff(request: Request):
    db = DB()

    db.postgre_cur.execute("INSERT INTO adresses (name, lon, lat) VALUES ('Коворк 1', 60, 60) RETURNING id")
    adr1_id = db.postgre_cur.fetchone()[0]

    db.postgre_cur.execute("INSERT INTO adresses (name, lon, lat) VALUES ('Коворк 2', 70, 70) RETURNING id")
    adr2_id = db.postgre_cur.fetchone()[0]

    db.postgre_cur.execute("INSERT INTO buildings (name, img, uuid, t_from, t_to) VALUES (%s,%s,%s,%s,%s) RETURNING id", ("Строение 1", "", adr1_id, 
                                                                                     [hour*7,hour*7,hour*7,hour*7,hour*7,hour*7,hour*7],
                                                                                     [hour*21,hour*21,hour*21,hour*21,hour*21,hour*21,hour*21]))
    b_id = db.postgre_cur.fetchone()[0]

    db.postgre_cur.execute("INSERT INTO floors (img, number, building_id) VALUES (%s,%s,%s) RETURNING id", "testplan.jpg", 1, b_id)
    f_id = db.postgre_cur.fetchone()[0]

    db.postgre_cur.execute("INSERT INTO seats (floor_id, posx, posy, name, onlyempl, price_f, price_e) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                           (f_id, .5, .5, "Место 1", False, 200, 100))
    
    db.postgre_con.commit()