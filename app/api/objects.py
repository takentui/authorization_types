from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.params import Depends
from pydantic.v1 import BaseModel
from starlette import status

from app.auth import get_current_user
from app.db import ObjectModel, OBJECTS, DBObjectModel

router = APIRouter(prefix="/api", tags=["objects"])


@router.post("/objects")
async def create_object(
    object_model: ObjectModel, user_name: str = Depends(get_current_user)
):
    OBJECTS[len(OBJECTS.keys()) + 1] = DBObjectModel(
        field1=object_model.field1,
        field2=object_model.field2,
        username=user_name,
    )


@router.get("/objects/{object_id}", response_model=ObjectModel)
async def get_object(object_id: int, user_name: str = Depends(get_current_user)):
    if object_id not in OBJECTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown object",
        )

    obj = OBJECTS[object_id]
    if user_name != obj.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You're not an owner of this object",
        )

    return ObjectModel.model_validate(obj)
