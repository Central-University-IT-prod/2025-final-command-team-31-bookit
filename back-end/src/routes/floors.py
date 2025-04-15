from fastapi import  status, Request
from fastapi.responses import Response, FileResponse
from uuid import UUID
from typing import Annotated, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Path, Header

from db import DB
from cfg import *
from utilities import check_if_admin
from models.floors import FloorCreate, FloorUpdate


router = APIRouter()

@router.get("/{floor_id}", status_code=200)
async def get_floor(floor_id: Annotated[UUID, Path(description="UUID этажа")]):
    dbcon = DB()

    floor = dbcon.get_floor(str(floor_id))
    if not floor:
        raise HTTPException(status_code=404, detail="Этаж не найден")

    floor_data = dict(floor)
    return floor_data

@router.post("/add", status_code=201)
async def add_floor(
    Authorization: Annotated[str, Header(aliase="Authorization")],
    floor_create: FloorCreate,
    img: UploadFile = File(description="Изображение этажа")
):
    dbcon = DB()
    check_if_admin(Authorization, dbcon)
    if not dbcon.check_if_building_exists(str(floor_create.building_id)):
        raise HTTPException(status_code=404, detail="Указанное строение не найдено")
    if dbcon.check_if_floor_exists_in_building(floor_create.number, str(floor_create.building_id)):
        raise HTTPException(status_code=400, detail="Этаж с таким номером уже существует в указанном строении")
    floor_id = dbcon.add_floor(img, floor_create.number, str(floor_create.building_id))
    return {"uuid": floor_id}


@router.delete("/delete/{floor_id}", status_code=204)
async def delete_floor(
    Authorization: Annotated[str, Header(aliase="Authorization")],
    floor_id: Annotated[UUID, Path(description="UUID этажа")],
) -> None:
    dbcon = DB()
    check_if_admin(Authorization, dbcon)
    if not dbcon.check_if_floor_exists(str(floor_id)):
        raise HTTPException(status_code=404, detail="Этаж не найден")
    dbcon.delete_floor(str(floor_id))
    return

@router.patch("/update/{floor_id}", status_code=200)
async def update_floor(
    Authorization: Annotated[str, Header(aliase="Authorization")],
    floor_id: Annotated[UUID, Path(description="Идентификатор этажа")],
    floor_update: FloorUpdate,
    img: Optional[UploadFile | str] = None
):
    dbcon = DB()
    check_if_admin(Authorization, dbcon)
    if isinstance(img, str) and len(img) == 0:
        img = None

    floor_excluded = floor_update.model_dump(exclude_unset=True)

    if not dbcon.check_if_floor_exists(str(floor_id)):
        raise HTTPException(status_code=404, detail="Этаж не найден")
    if "building_id" in floor_excluded:
        if floor_update.building_id is None:
            raise HTTPException(status_code=400, detail="Поле building_id не может быть null. Допустимо отсутствие поля или корректное значение")
        if not dbcon.check_if_building_exists(str(floor_update.building_id)):
            raise HTTPException(status_code=404, detail="Указанное строение не найдено")
        if dbcon.check_if_floor_exists_in_building(floor_update.number, str(floor_update.building_id)):
            raise HTTPException(status_code=400, detail="Этаж с таким номером уже существует в указанном строении")
    dbcon.update_floor(
        floor_id=str(floor_id),
        floor_number=floor_update.number if "number" in floor_excluded else None,
        building_id=str(floor_update.building_id) if "building_id" in floor_excluded else None,
        img=img
    )
    floor = dbcon.get_floor(str(floor_id))
    return dict(floor)


@router.get("/by-building/{building_id}", status_code=200)
async def get_floors_by_building(building_id: Annotated[UUID, Path(description="UUID здания")]):
    dbcon = DB()

    if not dbcon.check_if_building_exists(str(building_id)):
        raise HTTPException(status_code=404, detail="Указанное строение не найдено")

    floors = dbcon.get_floors_by_building(str(building_id))

    return floors

@router.get("/image/{image}")
async def get_img(response: Response, image: Optional[str]=None):
    if not os.path.isfile(f"{UPLOAD_DIR_FLOORS}/{image}"):
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Изображение не найдено" }

    return FileResponse(f"{UPLOAD_DIR_FLOORS}/{image}")
