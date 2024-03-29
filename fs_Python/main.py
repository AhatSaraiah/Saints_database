# main.py
import datetime
import os
from fastapi import Depends, FastAPI, HTTPException, Request,Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routes import admin_routes, user_routes,default_routes
from config import SECRET_KEY,ALGORITHM 
from middlewares import get_current_user_from_cookie, set_cookies
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from mysql_connection import get_database_connection,get_database_connection
from jose import jwt

app = FastAPI()


class CustomHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)
        self.custom_detail = detail

# Custom exception handler
async def custom_exception_handler(request: Request, exc: CustomHTTPException):
    return JSONResponse(
        content={"status": exc.status_code, "message": exc.custom_detail, "date": str(datetime.now())},
        status_code=exc.status_code,
    )



templates = Jinja2Templates(directory="templates")
# Register middlewares
app.middleware("http")(set_cookies)
app.middleware("http")(get_current_user_from_cookie)


@app.get("/login", response_class=HTMLResponse)
async def show_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Get the database connection
    connection = get_database_connection()

    try:
        # Create a cursor object to interact with the database
        cursor, user = getAllUsers(form_data, connection)

        if user and form_data.password == user["password"]:
            # Authentication successful
            # Generate JWT with only the username in the payload
            token_data = {"sub": user["user_name"]}
            access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        # Redirect based on role
            response = RedirectResponse(url=f"/{user['role'].lower()}")
            response.set_cookie(key="access_token", value=access_token, httponly=True)
            return response
        else:
            # Authentication failed
            raise CustomHTTPException(status_code=401, detail="Invalid credentials")

    finally:
        cursor.close()
        connection.close()

        

def getAllUsers(form_data, connection):
    cursor = connection.cursor(dictionary=True)
    cursor.callproc("GetAllUsers")
    result = next(cursor.stored_results())
    users_data = result.fetchall()
    user = next((u for u in users_data if u["user_name"] == form_data.username), None)
    return cursor,user


app.include_router(admin_routes.router, prefix="/admin", tags=["admin"])
app.include_router(user_routes.router, prefix="/user", tags=["user"])
app.include_router(default_routes.router, prefix="/default", tags=["default"])