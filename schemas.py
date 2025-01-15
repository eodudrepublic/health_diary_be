from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict
from datetime import datetime, date

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
    id: Optional[int] = None
    kakao_id: str  # 프론트엔드의 kakao_id와 일치
    nickname: Optional[str]  # nickname과 일치
    profile_image: Optional[str]  # profile_image와 일치
    # connected_at: Optional[str]  # connected_at과 일치


class UserLoginResponse(BaseModel):

    message: str
    user: dict

class PhotoUploadRequest(BaseModel):
    photo_id: int
    base64_image: str 

class PhotoUploadResponse(BaseModel):
    id: int
    photo_path: str

    class Config:
        orm_mode = True

class OwnPhotoCreate(BaseModel) :
    photo_path: str


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

class SocialPhotoResponse(BaseModel):
    id: int
    user_id: int
    photo_path: str
    datetime: datetime
    is_uploaded: bool

    class Config:
        orm_mode = True

class SocialPhotosResponse(BaseModel):
    photos: List[SocialPhotoResponse]

class BodyMetricsCreate(BaseModel):
    record_date: date  # 기록 날짜
    weight: float  # 체중
    muscle_mass: float  # 골격근량
    body_fat_percentage: float  # 체지방률

class BodyMetricsResponse(BaseModel):
    id: int  # 기록 ID
    user_id: int  # 사용자 ID
    record_date: date  # 기록 날짜
    weight: float  # 체중
    muscle_mass: float  # 골격근량
    body_fat_percentage: float  # 체지방률

    class Config:
        # orm_mode = True
         from_attributes = True 

class ExerciseUpdateRequest(BaseModel):
    exercise_id: int
    sets: int
    reps: int

class RoutineUpdateRequest(BaseModel):
    routine_id: int
    routine_name: Optional[str] = None
    exercises: List[ExerciseUpdateRequest]

class RoutineResponse(BaseModel):
    id: int
    user_id: int
    routine_name: Optional[str]
    exercises: List[ExerciseUpdateRequest]

    class Config:
        from_attributes = True

class RoutineNameUpdateRequest(BaseModel):
    routine_name: str