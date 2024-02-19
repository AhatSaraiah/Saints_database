# main.py
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from routes import admin_routes, user_routes,default_routes
from config import SECRET_KEY,ALGORITHM 
from middlewares import get_current_user_from_cookie, set_cookies
from fastapi.responses import HTMLResponse, RedirectResponse
from mysql_connection import get_database_connection,get_database_connection
from jose import jwt

app = FastAPI()


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
        cursor = connection.cursor(dictionary=True)
        cursor.callproc("GetAllUsers")
        result = next(cursor.stored_results())
        users_data = result.fetchall()
        user = next((u for u in users_data if u["user_name"] == form_data.username), None)

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
            raise HTTPException(status_code=401, detail="Invalid credentials")
    finally:
        cursor.close()
        connection.close()


app.include_router(admin_routes.router, prefix="/admin", tags=["admin"])
app.include_router(user_routes.router, prefix="/user", tags=["user"])