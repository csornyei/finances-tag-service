from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from finances_shared.db import get_db

from tag_service.logger import logger
import tag_service.schemas as schemas
import tag_service.tag_controller as tag_controller
from tag_service.tag_controller import (
    add_tag_to_statement as add_tag_to_statement_service,
)
from tag_service.tag_controller import read_all_tags, read_tag_by_id, read_tag_by_name
from tag_service.utils import is_uuid

router = APIRouter()


@router.get("/tags/", response_model=list[schemas.TagOut])
async def read_tags(db=Depends(get_db)):
    try:
        tags = await read_all_tags(db)

        return tags
    except Exception as e:
        logger.error(f"Error reading tags: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tags/{tag_id_or_name}", response_model=schemas.TagOut)
async def read_tag(tag_id_or_name: str, db=Depends(get_db)):
    try:
        if is_uuid(tag_id_or_name):
            tag_id = UUID(tag_id_or_name)
            tag = await read_tag_by_id(db, tag_id)
        else:
            tag = await read_tag_by_name(db, tag_id_or_name)
        return tag
    except Exception as e:
        logger.error(f"Error reading tag: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/tags/", response_model=schemas.TagOut)
async def create_tag(tag: schemas.TagCreate, db=Depends(get_db)):
    try:
        existing_tag = await read_tag_by_name(db, tag.name)
    except HTTPException:
        existing_tag = None

    if existing_tag:
        logger.error(f"Tag with name '{tag.name}' already exists")
        raise HTTPException(
            status_code=400, detail=f"Tag with name '{tag.name}' already exists"
        )

    tag = await tag_controller.create_tag(db, tag)

    return tag


@router.put("/tags/{tag_id}", response_model=schemas.TagOut)
async def update_tag(tag_id: str, tag: schemas.TagUpdate, db=Depends(get_db)):
    existing_tag = await read_tag_by_id(db, tag_id=tag_id)

    if not existing_tag:
        logger.error(f"Tag with ID '{tag_id}' not found")
        raise HTTPException(status_code=404, detail="Tag not found")

    updated_tag = await tag_controller.update_tag(db, existing_tag, tag)

    return updated_tag


@router.delete("/tags/{tag_id}", response_model=dict)
async def delete_tag(tag_id: str, db=Depends(get_db)):
    existing_tag = await read_tag_by_id(db, tag_id=tag_id)

    if not existing_tag:
        logger.error(f"Tag with ID '{tag_id}' not found")
        raise HTTPException(status_code=404, detail="Tag not found")

    await tag_controller.delete_tag(db, UUID(tag_id))

    return {"message": f"Tag with ID {tag_id} deleted successfully"}


@router.post("/tags/{tag_id}/statements/{statement_id}")
async def add_tag_to_statement(tag_id: str, statement_id: str, db=Depends(get_db)):
    if not is_uuid(tag_id):
        raise HTTPException(status_code=400, detail="Invalid tag ID format")
    if not is_uuid(statement_id):
        raise HTTPException(status_code=400, detail="Invalid statement ID format")

    try:
        await add_tag_to_statement_service(db, UUID(statement_id), UUID(tag_id))

        return {"message": "Tag added to statement successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
