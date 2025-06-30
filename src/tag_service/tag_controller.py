from uuid import UUID

from fastapi import HTTPException

from finances_shared.models.models import Tags, tags_to_statement_table
from sqlalchemy import insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from tag_service.schemas import TagOut, TagCreate, TagUpdate
from tag_service.logger import logger
from tag_service.services.statement import get_statement_by_id


async def read_all_tags(db: AsyncSession) -> list[TagOut]:
    """
    Fetch all tags from the database.

    :param db: Database session
    :return: List of TagOut schemas
    """
    tags = (await db.execute(select(Tags))).scalars().all()
    return [TagOut.model_validate(tag) for tag in tags]


async def read_tag_by_id(db: AsyncSession, tag_id: UUID) -> TagOut:
    """
    Fetch a tag by its ID.

    :param db: Database session
    :param tag_id: ID of the tag to fetch
    :return: TagOut schema of the tag
    """
    tag = (await db.execute(select(Tags).where(Tags.id == tag_id))).scalar_one_or_none()

    if not tag:
        raise HTTPException(status_code=404, detail=f"Tag with ID {tag_id} not found")

    return TagOut.model_validate(tag)


async def read_tag_by_name(db: AsyncSession, tag_name: str) -> TagOut:
    """
    Fetch a tag by its name.

    :param db: Database session
    :param tag_name: Name of the tag to fetch
    :return: TagOut schema of the tag
    """
    tag = (
        await db.execute(select(Tags).where(Tags.name == tag_name))
    ).scalar_one_or_none()

    if not tag:
        raise HTTPException(
            status_code=404, detail=f"Tag with name '{tag_name}' not found"
        )

    return TagOut.model_validate(tag)


async def create_tag(db: AsyncSession, tag_data: TagCreate) -> TagOut:
    """
    Create a new tag in the database.

    :param db: Database session
    :param tag_data: TagOut schema containing the tag data
    :return: Created TagOut schema
    """
    tag = Tags(name=tag_data.name, color=tag_data.color or "#000000")
    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    return TagOut.model_validate(tag)


async def update_tag(db: AsyncSession, tag: TagOut, tag_data: TagUpdate):
    """
    Update an existing tag in the database.

    :param db: Database session
    :param tag_id: ID of the tag to update
    :param tag_data: TagUpdate schema containing the updated tag data
    :return: Updated TagOut schema
    """
    tag_model = Tags(id=tag.id, name=tag.name, color=tag.color)
    tag_model.name = tag_data.name
    tag_model.color = tag_data.color

    stmt = (
        update(Tags)
        .where(Tags.id == tag_model.id)
        .values(name=tag_model.name, color=tag_model.color)
        .execution_options(synchronize_session="fetch")
    )

    await db.execute(stmt)
    await db.commit()

    return TagOut.model_validate(tag_model)


async def delete_tag(db: AsyncSession, tag_id: UUID) -> None:
    """
    Delete a tag from the database.

    :param db: Database session
    :param tag_id: ID of the tag to delete
    """

    stmt = delete(Tags).where(Tags.id == tag_id)

    await db.execute(stmt)

    await db.commit()


async def add_tag_to_statement(
    db: AsyncSession, statement_id: UUID, tag_id: UUID
) -> None:
    """
    Add a tag to a statement.
    Check if the tag exists, if the statement exists, and if the tag is not already associated with the statement.


    :param db: Database session
    :param statement_id: ID of the statement
    :param tag_id: ID of the tag to add
    """
    tag = await read_tag_by_id(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail=f"Tag with ID {tag_id} not found")

    tag = Tags(id=tag.id, name=tag.name, color=tag.color)

    statement = await get_statement_by_id(db, statement_id)
    if not statement:
        raise HTTPException(
            status_code=404, detail=f"Statement with ID {statement_id} not found"
        )

    if tag.name in [t.name for t in statement.tags]:
        raise HTTPException(
            status_code=400,
            detail=f"Tag '{tag.name}' is already associated with statement {statement_id}",
        )

    stmt = insert(tags_to_statement_table).values(
        tag_id=tag.id, statement_id=statement_id
    )
    await db.execute(stmt)
    await db.commit()

    logger.info(f"Successfully added tag {tag.name} to statement {statement_id}")
