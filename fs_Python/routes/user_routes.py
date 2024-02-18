
from fastapi import APIRouter


router = APIRouter()


@router.get("/dashboard")
async def user_dashboard():
    return {"message": "Welcome to the user dashboard"}


@router.get("/profile")
async def user_profile():
    return {"message": "User can view their profile"}











