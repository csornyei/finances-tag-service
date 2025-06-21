from fastapi import APIRouter

router = APIRouter()


@router.get("/example")
async def create_statement():
    """
    Example endpoint to create a statement.
    """
    return {"message": "Hello, World!"}
