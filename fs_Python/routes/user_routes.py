
from fastapi import APIRouter,Depends
from fastapi.templating import Jinja2Templates
from mysql_connection import get_database_connection
from middlewares import get_current_user_from_cookie  # Import the middleware


router = APIRouter()


templates = Jinja2Templates(directory="templates")


@router.get("/")
async def get_user(current_user: dict = Depends(get_current_user_from_cookie)):
    connection = get_database_connection()   
    return {"message": f"Hello, {current_user['role']} {current_user['username']}!"}


@router.post("/")
async def post_user():
    # Your code for handling POST requests
    return {"message": "Received a POST request to /user/"}


@router.get("/profile")
async def user_profile():
    return {"message": "User can view their profile"}











