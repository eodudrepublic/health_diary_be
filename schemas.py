from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict


# 요청용 스키마
class OAuthToken(BaseModel):
    oauth_token: str


# 응답용 스키마
class UserResponse(BaseModel):
    id: int
    kakao_id: str
    connected_at: Optional[str]
    email: Optional[str]
    nickname: Optional[str]
    profile_image: Optional[str]
    thumbnail_image: Optional[str]
    profile_nickname_needs_agreement: Optional[bool]
    profile_image_needs_agreement: Optional[bool]
    is_default_image: Optional[bool]
    is_default_nickname: Optional[bool]

    class Config:
        #orm_mode = True
        from_attributes = True

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


