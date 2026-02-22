from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.Users import UserCreate, UserResponse,UserLogin
from app.services.auth import register, login, is_authenticated

auth_router = APIRouter()

@auth_router.post('/register',response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_new_user(newuser:UserCreate, db: Session=Depends(get_db)):
    return register(newuser=newuser, db=db)

@auth_router.post('/login', status_code=status.HTTP_200_OK)
def login_user(userdata:UserLogin,db:Session=Depends(get_db)):
    return login(userdata=userdata, db=db)

@auth_router.post("/is_auth", status_code=status.HTTP_200_OK, response_model=UserResponse)
def is_auth(request: Request, db:Session=Depends(get_db)):
    return is_authenticated(request=request, db=db)
