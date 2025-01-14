from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict
from datetime import datetime

# 루틴 이름이랑 여러 운동 데이터 저장용
# class RoutineCreateWithName(BaseModel):
#     user_id: int
#     routine_name: str
#     exercises: List[Dict[str, int]]  

# 단일 운동 데이터 저장용
class RoutineCreate(BaseModel):
    
    user_id: int
    exercise_id: int
    sets: int
    reps: int

class UserLoginRequest(BaseModel):

    kakao_id: str  # 프론트엔드의 kakao_id와 일치
    nickname: Optional[str]  # nickname과 일치
    profile_image: Optional[str]  # profile_image와 일치
    connected_at: Optional[str]  # connected_at과 일치


class UserLoginResponse(BaseModel):

    message: str
    user: dict

class OwnPhotoCreate(BaseModel) :
    photo_path: str

class PhotoUploadRequest(BaseModel):
    photo_id: int

class OwnPhotoResponse(BaseModel):
    id: int
    user_id: int
    datetime: datetime
    photo_path: str
    is_uploaded: bool

    class Config:
        orm_mode = True

class MealPhotoCreate(BaseModel):
    photo_path: str

class MealPhotoResponse(BaseModel):
    id: int
    user_id: int
    datetime: datetime
    photo_path: str

    class Config:
        orm_mode = True