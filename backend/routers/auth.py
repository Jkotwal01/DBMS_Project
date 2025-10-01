from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import os

import models, schemas, crud
from deps import get_db, get_current_user
from auth import create_access_token

router = APIRouter(prefix="", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        user = crud.create_user(db, user_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return user


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440)))
    token = create_access_token({"user_id": user.user_id, "role": user.role.value}, expires_delta=access_token_expires)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/auth/me", response_model=schemas.UserOut)
def verify_token(current_user: models.User = Depends(get_current_user)):
    return current_user

