from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from middlewares import check_admin_access
from config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES,ALGORITHM 


# Dependency for checking if the current user is an admin
def is_admin(current_user: dict = Depends(check_admin_access)):
    return current_user