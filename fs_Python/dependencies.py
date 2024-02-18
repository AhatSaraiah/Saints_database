from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional

SECRET_KEY = "your-secret-key-here"  
ALGORITHM = "HS256"  

# Define the structure of the JWT token data using Pydantic BaseModel
class TokenData(BaseModel):
    username: Optional[str] = None

# Dependency for getting the current user from the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Custom dependency to get the current user from a JWT cookie
def get_current_user_from_cookie(token: str = Depends(oauth2_scheme)):
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
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    return token_data
