from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, HTTPException, Path, Request, Header

from db import DB
from utilities import check_if_admin
from models.addresses import AddressCreate

router = APIRouter()

@router.post("/add", status_code=201)
async def add_address(Authorization: Annotated[str, Header(aliase="Authorization")], address: AddressCreate):
    db = DB()
    check_if_admin(Authorization, db)
    address_id = db.add_address(address.name, address.lon, address.lat)
    return {"uuid": address_id}


@router.get("/all", status_code=200)
async def get_all_addresses():
    db = DB()
    addresses = db.get_all_addresses()
    return addresses


@router.delete("/{address_id}", status_code=204)
async def delete_address(Authorization: Annotated[str, Header(aliase="Authorization")], address_id: Annotated[UUID, Path(description="UUID адреса")]):
    db = DB()
    check_if_admin(Authorization, db)
    if not db.check_if_address_exists(str(address_id)):
        raise HTTPException(status_code=404, detail="Адрес не найден")

    buildings = db.get_buildings_by_address(str(address_id))

    for building in buildings:
        building_id = building["id"]

        floors = db.get_floors_by_building(building_id)

        for floor in floors:
            db.delete_floor(floor["id"])

        db.delete_building(building_id)

    db.delete_address(str(address_id))