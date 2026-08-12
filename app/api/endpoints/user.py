from fastapi import APIRouter

from app.core.user import auth_backend, fastapi_users
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/jwt',
    tags=['auth'],
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    tags=['auth'],
)

users_router = fastapi_users.get_users_router(UserRead, UserUpdate)
users_router.routes = [
    route for route in users_router.routes
    if route.name != 'users:delete_user'
]

router.include_router(users_router, tags=['users'])
