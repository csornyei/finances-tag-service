from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from finances_shared.models import Statements


async def get_statement_by_id(db: AsyncSession, statement_id: UUID) -> Statements:
    """
    Fetch a statement by its ID from the external statements service.

    :param statement_id: ID of the statement to fetch
    :return: Statement object
    """

    statement = (
        await db.execute(
            select(Statements)
            .where(Statements.id == statement_id)
            .options(
                selectinload(Statements.tags),
            )
        )
    ).scalar_one_or_none()

    if not statement:
        raise ValueError(f"Statement with ID {statement_id} not found")

    return statement
