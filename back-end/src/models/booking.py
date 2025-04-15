from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, model_validator
from uuid import UUID

class GetSeatsTime(BaseModel):
    t_from: int
    t_to: int

class GetSeats(BaseModel):
    floor_id: UUID
    times: List[GetSeatsTime]

class BookItems(BaseModel):
    item_id: UUID
    qty: int

class BookOne(BaseModel):
    floor_id: UUID
    seat_id: UUID
    times: List[GetSeatsTime]
    items: List[BookItems]
    comment: str

class GroupSeat(BaseModel):
    seat_id: UUID
    user_id: UUID

class BookGroup(BaseModel):
    floor_id: UUID
    seats: List[GroupSeat]
    times: List[GetSeatsTime]
    items: List[BookItems]
    group_id: UUID
    comment: str

class CalcPrice(BaseModel):
    times: List[GetSeatsTime]
    seats: List[GroupSeat]
    items: List[BookItems]