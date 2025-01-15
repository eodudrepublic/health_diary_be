from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict
from datetime import datetime, date  

# 단일 운동 데이터 저장용
class RoutineCreate(BaseModel):
    routine_id: int  # 동일한 루틴 ID를 사용하는 운동들
    user_id: int     # 사용자 ID
    exercise_id: int # 운동 ID
    sets: int        # 세트 수
    reps: int        # 반복 횟수

class RoutineCreateList(BaseModel):
    routines: List[RoutineCreate] 

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
class OwnPhotoResponse(BaseModel):
    id: int
    user_id: int
    photo_path: Optional[str]
    is_uploaded: bool
    # base64: Optional[str] = None  # Base64 데이터 추가

    class Config:
        orm_mode = True

class OwnPhotoResponse(BaseModel):
    id: int
    user_id: int
    datetime: datetime 
    photo_path: str
    is_uploaded: bool
    # base64_image: Optional[str]  # Base64 이미지 필드 추가 (선택적)

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

    class Config:
        orm_mode = True

class RoutineResponse(BaseModel):
    id: int
    user_id: int
    routine_name: Optional[str]
    exercises: List[ExerciseUpdateRequest]

    class Config:
        from_attributes = True

# 운동별 세트 및 횟수 수정
class ExerciseUpdateRequest(BaseModel):
    exercise_id: int  # 운동 ID
    sets: int         # 세트 수
    reps: int         # 반복 횟수

# 루틴 이름과 운동 세트/횟수 업데이트 요청
class RoutineUpdateRequest(BaseModel):
    routine_id: int             # 수정할 루틴 ID
    routine_name: Optional[str] = None  # 수정할 루틴 이름 (선택 사항)
    exercises: List[ExerciseUpdateRequest]  # 수정할 운동들

    class Config:
        orm_mode = True

# 루틴 이름을 업데이트하기 위한 요청 데이터
class RoutineNameUpdateRequest(BaseModel):
    routine_name: str  # 루틴 이름

    class Config:
        orm_mode = True


# 응답 스키마 - 루틴 이름 업데이트 후의 루틴 정보 반환
class RoutineResponse(BaseModel):
    id: int  # 루틴 ID
    user_id: int  # 사용자 ID
    routine_name: str  # 루틴 이름
    sets: int  # 세트 수
    reps: int  # 반복 횟수

    class Config:
        orm_mode = True


#루틴 이름이랑 여러 운동 데이터 저장용
class RoutineCreateWithName(BaseModel):
    user_id: int
    routine_name: str
    exercises: List[Dict[str, int]]  

