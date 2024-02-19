from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM
from routes.default_routes import get_database_connection

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Middleware for getting the current user from the token in cookies
async def get_current_user_from_cookie(request: Request, call_next):
    token = request.cookies.get("access_token")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

        # Get the role from the database based on the username
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.callproc("GetUserByUsername", (username,))
        result = next(cursor.stored_results())
        user_data = result.fetchone()
        cursor.close()
        connection.close()

        role = user_data.get("role", "user")

        token_data = {"username": username, "role": role}
    except JWTError:
        raise credentials_exception

    request.state.user_data = token_data  # Store user_data in request state
    response = await call_next(request)
    return response

# Middleware for checking admin access
async def check_admin_access(request: Request, call_next):
    user_data = getattr(request.state, "user_data", {})
    if user_data.get("role") == "admin":
        response = await call_next(request)
        return response
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

# Middleware for setting cookies
async def set_cookies(response: Response, call_next):
    response = await call_next(response)
    return response