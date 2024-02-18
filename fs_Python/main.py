

from fastapi import FastAPI, Depends, HTTPException, status, Response, Request, Cookie
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dependencies import get_current_user_from_cookie
from routes import admin_routes, user_routes

SECRET_KEY = "your-secret-key-here"  
ALGORITHM = "HS256"  
ACCESS_TOKEN_EXPIRE_MINUTES = 30 

templates = Jinja2Templates(directory="templates")

app = FastAPI()

# For simplicity, using a hardcoded user for authentication
fake_users_db = {
    "admin": {
        "username": "admin",
        "password": "adminpassword",
        "role": "admin",
    },
    "user": {
        "username": "user",
        "password": "userpassword",
        "role": "user",
    },
}


# # Dependency for getting the current user from the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = fake_users_db.get(token)
    if user is None:
        raise credentials_exception
    return user

# Dependency for checking if the current user is an admin
def is_admin(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


# Login route
@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/token")
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if user is None or user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create a JWT token
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_expires = datetime.utcnow() + expires_delta
    to_encode = {"sub": form_data.username, "exp": access_token_expires}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # Set the JWT token as a cookie
    response.set_cookie(key="Authorization", value=f"Bearer {encoded_jwt}", expires=expires_delta, secure=True, httponly=True, samesite="Lax")

    # Redirect to the appropriate route based on the user's role
    if user["role"] == "admin":
        return RedirectResponse("/admin/dashboard")
    elif user["role"] == "user":
        return RedirectResponse("/user_dashboard")
    else:
        raise HTTPException(status_code=403, detail="Forbidden")



@app.get("/")
async def read_root():
    return {"message": "Hello, this is the main page"}


app.include_router(admin_routes.router, prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_user)])
app.include_router(user_routes.router, prefix="/user", tags=["user"], dependencies=[Depends(get_current_user)])



