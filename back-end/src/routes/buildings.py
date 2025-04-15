from uuid import UUID
from typing import Optional, Annotated
from fastapi.responses import Response, FileResponse
from fastapi import (
    APIRouter,
    HTTPException,
    UploadFile,
    File,
    Request,
    status,
    Path,
    Header
)

from db import DB
from cfg import *
from utilities import check_if_admin
from models.buildings import BuildingCreate, BuildingUpdate


router = APIRouter()

@router.get("/{building_id}", status_code=200)
async def get_building(building_id: Annotated[UUID, Path(description="UUID строения")]):
    dbcon = DB()

    building = dbcon.get_building(str(building_id))
    if not building:
        raise HTTPException(status_code=404, detail="Строение не найдено")

    return dict(building)

@router.post("/add", status_code=201)
async def add_building(
    Authorization: Annotated[str, Header(aliase="Authorization")],
    building_data: BuildingCreate,
    img: UploadFile = File(description="Изображение строения")
):
    dbcon = DB()
    check_if_admin(Authorization, dbcon)
    if not dbcon.check_if_address_exists(str(building_data.address_id)):
        raise HTTPException(status_code=404, detail="Указанный адрес не найден")
    building_id = dbcon.add_building(building_data.name, img, str(building_data.address_id), building_data.t_from, building_data.t_to)
    return {"uuid": building_id}


@router.patch("/{building_id}", status_code=200)
async def update_building(
    Authorization: Annotated[str, Header(aliase="Authorization")],
    building_id: Annotated[UUID, Path(description="UUID строения")],
    building_update: BuildingUpdate,
    img: Optional[UploadFile | str] = File(None, description="Новое изображение строения")
):
    dbcon = DB()
    check_if_admin(Authorization, dbcon)
    if isinstance(img, str) and len(img) == 0:
        img = None

    building_excluded = building_update.model_dump(exclude_unset=True)

    if not dbcon.check_if_building_exists(str(building_id)):
        raise HTTPException(status_code=404, detail="Строение не найдено")

    dbcon.update_building(
        building_id=str(building_id),
        name=building_update.name if "name" in building_excluded else None,
        t_from=building_update.t_from if "t_from" in building_excluded else None,
        t_to=building_update.t_to if "t_to" in building_excluded else None,
        img=img
    )
    building = dbcon.get_building(str(building_id))
    return dict(building)

@router.get("/by-address/{address_id}", status_code=200)
async def get_buildings_by_address(address_id: Annotated[UUID, Path(description="UUID адреса")]):
    dbcon = DB()

    if not dbcon.check_if_address_exists(str(address_id)):
        raise HTTPException(status_code=404, detail="Указанный адрес не найден")

    buildings = dbcon.get_buildings_by_address(str(address_id))

    return buildings


@router.delete("/{building_id}", status_code=204)
async def delete_building(
    Authorization: Annotated[str, Header(aliase="Authorization")],
    building_id: Annotated[UUID, Path(description="UUID строения")]
):
    dbcon = DB()
    check_if_admin(Authorization, dbcon)
    if not dbcon.check_if_building_exists(str(building_id)):
        raise HTTPException(status_code=404, detail="Строение не найдено")

    floors = dbcon.get_floors_by_building(str(building_id))

    for floor in floors:
        dbcon.delete_floor(str(floor["id"]))

    dbcon.delete_building(str(building_id))


@router.get("/image/{image}")
async def get_img(request:Request, response:Response, image:Optional[str]=None):
    if not os.path.isfile(f"{UPLOAD_DIR_BUILDINGS}/{image}"):
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Изображение не найдено" }

    return FileResponse(f"{UPLOAD_DIR_BUILDINGS}/{image}")