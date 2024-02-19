# main.py
from fastapi import Depends, FastAPI,APIRouter, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from routes import admin_routes, user_routes,default_routes
from config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES,ALGORITHM 
from middlewares import get_current_user_from_cookie, check_admin_access, set_cookies
from fastapi.responses import HTMLResponse
from routes.default_routes import connect_database ,get_database_connection

app = FastAPI()


connect_database()

# Register middlewares
app.middleware("http")(set_cookies)
app.middleware("http")(get_current_user_from_cookie)
app.middleware("http")(check_admin_access)



# Dependency for getting the current user from the token in cookies
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

templates = Jinja2Templates(directory="templates")

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def show_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
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
            # Redirect based on role
            if user["role"] == "admin":
                return {"message": "Admin login successful", "role": user["role"], "redirect": "/admin/dashboard"}
            else:
                return {"message": "User login successful", "role": user["role"], "redirect": "/user/dashboard"}
        else:
            # Authentication failed
            raise HTTPException(status_code=401, detail="Invalid credentials")
    finally:
        cursor.close()
        connection.close()

app.include_router(admin_routes.router, prefix="/admin", tags=["admin"])
app.include_router(user_routes.router, prefix="/user", tags=["user"])