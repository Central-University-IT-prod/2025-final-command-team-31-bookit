import uvicorn
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request
from cfg import *
import psycopg2
from fastapi.staticfiles import StaticFiles
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import time

from routes import user, suggestion, items, seats, admin, addresses, buildings, floors, frontend, user_docs, user_avatar, booking, testing
from utilities import make_http_error

def create_dirs():
    path = UPLOAD_DIR_AVATAR
    os.makedirs(path, exist_ok=True)
    path = UPLOAD_DIR_DOCS
    os.makedirs(path, exist_ok=True)

# SETUP DATABASE
while True:
    try:
        try:
            postgre_con = psycopg2.connect(dbname="postgres", user=POSTGRES_USERNAME, password=POSTGRES_PASSWORD, host=POSTGRES_HOST, port=POSTGRES_PORT)
            postgre_con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            postgre_cur = postgre_con.cursor()
            with open("prepare1.sql", "r") as f:
                postgre_cur.execute(f.read().format(POSTGRES_DATABASE))
                postgre_con.commit()
            postgre_cur.close()
            postgre_con.close()
        except Exception as e:
            pass

        postgre_con = psycopg2.connect(dbname=POSTGRES_DATABASE, user=POSTGRES_USERNAME, password=POSTGRES_PASSWORD, host=POSTGRES_HOST, port=POSTGRES_PORT)
        postgre_cur = postgre_con.cursor()
        with open("prepare2.sql", "r") as f:
            postgre_cur.execute(f.read())
            postgre_con.commit()
        postgre_cur.close()
        postgre_con.close()

        print("DB SETUP FINISHED")
        break

    except Exception as e:
        print(f"DB SETUP ERROR, RETRY\n{e}")
        time.sleep(5)

app = FastAPI()
@app.exception_handler(RequestValidationError)
async def raise_validation_error(request: Request, exc: RequestValidationError):
    print(exc)
    return make_http_error(400, "ошибка в данных запроса")

app.include_router(buildings.router, prefix="/api/buildings", tags=["Buildings"])
app.include_router(floors.router, prefix="/api/floors", tags=["Floors"])
app.include_router(addresses.router, prefix="/api/addresses", tags=["Addresses"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(user_avatar.router, prefix="/api", tags=["Avatars"])
app.include_router(user_docs.router, prefix="/api/documents", tags=["Documents"])
app.include_router(user.router, prefix="/api", tags=["Users"])
app.include_router(items.router, prefix="/api", tags=["Items"])
app.include_router(suggestion.router, prefix="/api", tags=["Suggestions"])
app.include_router(seats.router, prefix="/api", tags=["Seats"])
app.include_router(buildings.router, prefix="/api/buildings", tags=["Buildings"])
app.include_router(floors.router, prefix="/api/floors", tags=["Floors"])
app.include_router(addresses.router, prefix="/api/addresses", tags=["Addresses"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(user.router, prefix="/api", tags=["Users"])
app.include_router(items.router, prefix="/api", tags=["Items"])
app.include_router(suggestion.router, prefix="/api", tags=["Suggestions"])
app.include_router(seats.router, prefix="/api", tags=["Seats"])
app.include_router(booking.router, prefix="/api", tags=["Booking"])
app.include_router(testing.router, prefix="/api", tags=["Testing"])

create_dirs()

try:
    app.mount("/assets", StaticFiles(directory="dist/assets"), name="VUE /assets")
    app.mount("/img", StaticFiles(directory="dist/img"), name="VUE /img")
except:
    print("Ошибка фронтенда")

app.include_router(frontend.router, prefix="", tags=["Frontend"])

if __name__ == "__main__":
    server_address = MAINAPI_HOST
    host, port = server_address.split(":")
    uvicorn.run(app, host=host, port=int(port))