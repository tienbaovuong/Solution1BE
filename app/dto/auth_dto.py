from datetime import datetime
from pydantic import BaseModel

from app.dto.common import BaseResponseData

class LoginRequest(BaseModel):
    email: str
    password: str

class SignUpRequest(BaseModel):
    user_name: str
    password: str
    email: str

class UserProfileRequest(BaseModel):
    user_name: str
    email: str

class LoginResponseData(BaseModel):
    access_token: str

class LoginResponse(BaseResponseData):
    data: LoginResponseData

class UserResponseData(BaseModel):
    id: str
    user_name: str
    email: str
    created_at: datetime
    updated_at: datetime
    role: str

class UserResponse(BaseResponseData):
    data: UserResponseData