
from fastapi import APIRouter, Path, Request, Query,HTTPException,status,Depends,Form
from fastapi.templating import Jinja2Templates
from mysql_connection import get_database_connection,initialize_db
from routes.default_routes import connect_database
from middlewares import get_current_user_from_cookie  # Import the middleware


router = APIRouter()


templates = Jinja2Templates(directory="templates")

def get_db_connection():
    connection = get_database_connection()
    try:
        yield connection
    finally:
        connection.close()


@router.get("/admin")
async def get_admin(current_user: dict = Depends(get_current_user_from_cookie), db: mysql.connector.connection.MySQLConnection = Depends(get_db_connection)):
    # Your existing code for the route
    return {"message": f"Hello, {current_user['role']} {current_user['username']}!"}


@router.get("/user")
async def get_user(current_user: dict = Depends(get_current_user_from_cookie)):
    return {"message": f"Hello, {current_user['role']} {current_user['username']}!"}



@router.get("/profile")
async def user_profile():
    return {"message": "User can view their profile"}











