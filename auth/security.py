from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Simulated user DB
fake_users_db = {
    "admin": {"username": "admin", "password": "secret", "role": "admin"},
    "user": {"username": "user", "password": "secret", "role": "user"},
}

def fake_decode_token(token: str):
    user = fake_users_db.get(token)
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    return user

def role_required(role: str):
    async def role_checker(user = Depends(get_current_user)):
        if user['role'] != role:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return user
    return role_checker