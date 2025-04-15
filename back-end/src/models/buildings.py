import json
from uuid import UUID
from fastapi import Form
from typing import List, Annotated, Any, Optional
from pydantic import BaseModel, ModelWrapValidatorHandler, ValidationError, model_validator


class BuildingBase(BaseModel):
    name: Annotated[str, Form(description="Название здания")]
    t_from: Annotated[List[int], Form(description="JSON с данными о здании", min_length=7, max_length=7)]
    t_to: Annotated[List[int], Form(description="JSON с данными о здании", min_length=7, max_length=7)]

    @model_validator(mode='before')
    @classmethod
    def validate(cls, data: Any) -> Any:
        try:
            if isinstance(data, str):
                data = json.loads(data)
            return data
        except ValidationError:
            raise
        except json.JSONDecodeError:
            raise

class BuildingCreate(BuildingBase):
    address_id: Annotated[UUID, Form(description="UUID адреса")]

class BuildingUpdate(BuildingBase):
    name: Annotated[Optional[str], Form(description="Название здания")] = None
    t_from: Annotated[Optional[List[int]], Form(description="JSON с данными о здании", min_length=7, max_length=7)] = None
    t_to: Annotated[Optional[List[int]], Form(description="JSON с данными о здании", min_length=7, max_length=7)] = None