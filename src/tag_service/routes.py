from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select

from finances_shared.db import get_db
from finances_shared.models.models import Tags
import tag_service.schemas as schemas

router = APIRouter()


# get tag by name, include all statements with this tag
# get all tags
# create tag
# update tag
# delete tag


@router.get("/tags/", response_model=list[schemas.TagOut])
async def read_tags(db=Depends(get_db)):
    tags = (await db.execute(select(Tags))).scalars().all()

    return tags


@router.get("/tags/{tag_id}", response_model=schemas.TagOut)
async def read_tag(tag_id: str, db=Depends(get_db)):
    tag = (await db.execute(select(Tags).where(Tags.id == tag_id))).scalar_one_or_none()

    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    return tag


@router.post("/tags/", response_model=schemas.TagOut)
async def create_tag(tag: schemas.TagCreate, db=Depends(get_db)):
    existing_tag = (
        await db.execute(select(Tags).where(Tags.name == tag.name))
    ).scalar_one_or_none()

    if existing_tag:
        raise HTTPException(
            status_code=400, detail=f"Tag with name '{tag.name}' already exists"
        )

    tag = Tags(name=tag.name, color=tag.color)
    if tag.color is None:
        tag.color = "#000000"

    # Add the new tag to the database
    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    return tag
