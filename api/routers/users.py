from fastapi import APIRouter, Query, Path, Depends, Body, Form, HTTPException
from peewee import *

from models import Token, UserDto
from auth.jwt_handler import pwd_context, create_access_token, oauth2_scheme, validate_token, get_password_hash, verify_password, authenticate_user
from database_modules.entities import User

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get('/me', tags=['users'])
async def get_me(user: UserDto = Depends(validate_token)):
    '''
    Get the current user
    '''
    return user