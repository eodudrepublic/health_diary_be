from sqlalchemy.orm import Session
from models import User, Friend
from typing import Optional
from fastapi import HTTPException

#카카오 로그인 및 회원 가입 관련 crud 정리
def get_user_by_kakao_id(db: Session, kakao_id: str) -> Optional[User]:
    """
    주어진 kakao_id를 가진 사용자를 데이터베이스에서 검색합니다.
    """
    return db.query(User).filter(User.kakao_id == kakao_id).first()


def create_user(
    db: Session,
    kakao_id: str,
    connected_at: str,
    email: Optional[str],
    nickname: Optional[str],
    profile_image: Optional[str],
    thumbnail_image: Optional[str],
    profile_nickname_needs_agreement: Optional[bool],
    profile_image_needs_agreement: Optional[bool],
    is_default_image: Optional[bool],
    is_default_nickname: Optional[bool],
) -> User:
    """
    주어진 정보를 바탕으로 새로운 사용자를 생성하고 데이터베이스에 저장
    """
    user = User(
        kakao_id=kakao_id,
        connected_at=connected_at,
        email=email,
        nickname=nickname,
        profile_image=profile_image,
        thumbnail_image=thumbnail_image,
        profile_nickname_needs_agreement=profile_nickname_needs_agreement,
        profile_image_needs_agreement=profile_image_needs_agreement,
        is_default_image=is_default_image,
        is_default_nickname=is_default_nickname,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

#friend 테이블 관련 crud 정리

def add_friend(db: Session, scanned_user_id: int, qr_user_id: int):
    # 1. 자기 자신 추가 방지
    if scanned_user_id == qr_user_id:
        raise HTTPException(status_code=400, detail="You cannot add yourself as a friend.")

    # 2. 중복 친구 관계 확인
    existing_friendship = db.query(Friend).filter(
        Friend.user_id == scanned_user_id,
        Friend.friend_id == qr_user_id
    ).first()

    if existing_friendship:
        raise HTTPException(status_code=400, detail="Friendship already exists.")

    # 3. 양방향 친구 관계 추가
    new_friend_1 = Friend(user_id=scanned_user_id, friend_id=qr_user_id)
    new_friend_2 = Friend(user_id=qr_user_id, friend_id=scanned_user_id)
    db.add(new_friend_1)
    db.add(new_friend_2)
    db.commit()
    db.refresh(new_friend_1)
    db.refresh(new_friend_2)

    return {"message": "Friendship created successfully."}


def get_friends_by_user_id(db: Session, user_id: int):
    """
    특정 사용자의 모든 친구 조회
    """
    friends = db.query(Friend).filter_by(user_id=user_id).all()
    return friends


def update_friend(db: Session, friend_id: int, user_id: int, new_friend_id: int):
    """
    친구 정보 업데이트 (예: 기존 친구 관계를 다른 사용자로 변경)
    """
    friend_relationship = db.query(Friend).filter_by(user_id=user_id, friend_id=friend_id).first()

    if not friend_relationship:
        raise HTTPException(status_code=404, detail="Friendship not found.")

    # 업데이트 (기존 friend_id -> new_friend_id)
    friend_relationship.friend_id = new_friend_id
    db.commit()
    db.refresh(friend_relationship)

    return friend_relationship


def delete_friend(db: Session, user_id: int, friend_id: int):
    """
    친구 삭제
    """
    friend_relationship = db.query(Friend).filter_by(user_id=user_id, friend_id=friend_id).first()

    if not friend_relationship:
        raise HTTPException(status_code=404, detail="Friendship not found.")

    # 친구 관계 삭제
    db.delete(friend_relationship)
    db.commit()

    return {"message": "Friend deleted successfully"}