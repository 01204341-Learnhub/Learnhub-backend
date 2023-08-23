from fastapi import APIRouter


router = APIRouter(
        prefix="/programs",
        tags=['program'],
        )

@router.get("/", status_code=200)
async def list_programs():
    return {200: "OK"}
