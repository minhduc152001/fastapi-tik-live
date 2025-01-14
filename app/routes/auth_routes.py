from typing import List

from fastapi import APIRouter, status, Header
from app.controllers.auth_controller import signup, login, logout, get_me, list_users, update_user
from app.models.user_model import UserResponse, UserLogin, UserLoginResponse, UserUpdateRequest, UserSignUp

auth_router = APIRouter()

@auth_router.post("/signup", response_description="Create new user", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def signup_route(user: UserSignUp):
    return await signup(user)

@auth_router.post("/login", response_description="Login user", status_code=status.HTTP_200_OK,response_model=UserLoginResponse)
async def login_route(body: UserLogin):
    return await login(body)

@auth_router.post("/logout", response_description="Logout user", status_code=status.HTTP_200_OK)
async def logout_route(authorization: str = Header(...)):
    # Extract the token from the "Authorization" header
    token = authorization.split(" ")[1]
    return await logout(token)

@auth_router.get("/me", response_description="Get current user info", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_me_route(authorization: str = Header(...)):
    # Extract the token from the "Authorization" header
    token = authorization.split(" ")[1]
    return await get_me(token)

@auth_router.get("/", response_description="Get all users (Admin only)", status_code=status.HTTP_200_OK, response_model=List[UserResponse])
async def get_users_route(authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    return await list_users(token)

@auth_router.put("/", response_description="Update current user info", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def update_user_route(user_update: UserUpdateRequest, authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    return await update_user(token, user_update)
