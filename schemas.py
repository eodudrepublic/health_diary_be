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
