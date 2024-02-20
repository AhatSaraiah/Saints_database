from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from config import SECRET_KEY, ALGORITHM
from mysql_connection import get_database_connection

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Middleware for getting the current user from the token in cookies
async def get_current_user_from_cookie(request: Request, call_next):
   token = request.cookies.get("access_token")
    
    # Add this print statement
   print("Token:", token)

   credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

   try:
        if token is None:
            raise credentials_exception  # Raise an exception if token is None
        else:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception

            # Fetch the role from the database based on the username
            connection = get_database_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.callproc("GetUser", (username,))
            result = next(cursor.stored_results())
            user_data = result.fetchone()
            connection.close()

            if user_data is None:
                raise credentials_exception

            token_data = {"username": username, "role": user_data["role"]}

   except JWTError:
       raise credentials_exception

   request.state.user_data = token_data 
   response = await call_next(request)
   return response


# Middleware for setting cookies
async def set_cookies(response: Response, call_next):
    # Your existing code for setting cookies, if any
    response = await call_next(response)
    return response
