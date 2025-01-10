from pydantic import BaseModel, Field
from typing import Optional, Literal


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
        orm_mode = True

class TimetableCreate(BaseModel):
    url: str
    year: int = Field(..., ge=2000, le=2100, description="연도는 2000~2100 사이의 숫자여야 함함.")
    season: Literal[0, 1, 2, 3] = Field(..., description="봄은 0, 여름은 1, 가을은 2, 겨울은 3으로 입력하세요.")

class TimetableResponse(BaseModel):
    id: int
    year: int
    season: int  # 0: 봄, 1: 여름, 2: 가을, 3: 겨울
    url: str

    class Config:
        orm_mode = True