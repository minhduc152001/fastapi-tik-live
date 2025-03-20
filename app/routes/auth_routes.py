from datetime import datetime
from typing import List

from fastapi import APIRouter, status, Header, Path
from app.controllers.auth_controller import signup, login, logout, get_me, list_users, update_user, delete_user, \
    update_user_admin, deactivate
from app.models.user_model import UserResponse, UserLogin, UserLoginResponse, UserUpdateRequest, UserSignUp, \
    AdminUpdateUserRequest

auth_router = APIRouter()

@auth_router.post("/signup", response_description="Create new user", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def signup_route(user: UserSignUp):
    user_data = {**user.model_dump(), "subscription_expired_at": datetime.now()}
    return await signup(user_data)

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

@auth_router.post("/deactivate_user", response_description="Deactivate User", status_code=status.HTTP_200_OK)
async def deactivate_user_route(authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    return await deactivate(token)

# ADMINS ONLY
@auth_router.delete("/{user_id}", response_description = "FOR ADMIN: Delete user", status_code=204, tags = ["admin"])
async def delete_user_route(user_id: str = Path(...), authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    return await delete_user(token, user_id)

@auth_router.post('/', response_description = "FOR ADMIN: Create new user", status_code=status.HTTP_201_CREATED, response_model=UserResponse, tags = ["admin"])
async def create_user_route(user: UserSignUp):
    return await signup(user.model_dump())

@auth_router.put(path = '/admin/update/{user_id}', response_description = "FOR ADMIN: Update user info", status_code=status.HTTP_200_OK, tags = ["admin"])
async def update_admin_user_route(user: AdminUpdateUserRequest, user_id: str = Path(...), authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    return await update_user_admin(token, user_id, user)