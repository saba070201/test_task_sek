from typing import List
from fastapi import Query
from pydantic import BaseModel, model_validator
from fastapi import exceptions 

class GetOrganizationRequestSchema(BaseModel):
    building_name: str | None = Query(default=None, description="Имя или id строения")
    organization_name: str | None = Query(
        default=None, description="Имя или id организации"
    )
    activity_name: str | None = Query(
        default=None, description="Имя или id вида деятельности"
    )
    radius_size: int | None = Query(
        default=None,
        description="Радиус поиска организации в метрах от текущего местоположения",
    )

    @model_validator(mode="after")
    def check_exactly_one_field_is_not_none(self) -> "GetOrganizationRequestSchema":
        non_none_fields = [
            field for field, value in self.model_dump().items() if value is not None
        ]
        if len(non_none_fields) > 1:
            raise exceptions.HTTPException(
                status_code=400,
                detail="Максимум одно поле должно быть не None"
            )
        return self


class ActivityTreeSchema(BaseModel):
    id: int
    name: str
    children: List["ActivityTreeSchema"] = []


class BuildingSchema(BaseModel):
    id: int
    address: str
    latitude: float
    longitude: float


class OrganizationResponseSchema(BaseModel):
    id: int
    name: str
    building: BuildingSchema
    activity_tree: List[ActivityTreeSchema]
    phone_number: str

    class Config:
        from_attributes = True


class GetOrganizationListResponseSchema(BaseModel):
    organizations: List[OrganizationResponseSchema]
