from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict

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

    kakao_id: str
    nickname: Optional[str] = None
    profile_image: Optional[str] = None
    connected_at: Optional[str] = None


class UserLoginResponse(BaseModel):

    message: str
    user: dict

