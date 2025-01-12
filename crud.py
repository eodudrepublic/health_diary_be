from sqlalchemy.orm import Session, joinedload
from models import User, Friend, Routine, ExerciseName
from typing import Optional, List
from schemas import RoutineCreate, UserLoginRequest
from fastapi import HTTPException

def manage_user_in_db(db: Session, user: UserLoginRequest):

    # 기존 유저 확인
    existing_user = db.query(User).filter(User.kakao_id == user.kakao_id).first()
    if existing_user:
        return {
            "message": "User exists",
            "user": {
                "kakao_id": existing_user.kakao_id,
                "nickname": existing_user.nickname,
                "profile_image": existing_user.profile_image,
            },
        }

    # 새로운 유저 추가
    new_user = User(
        kakao_id=user.kakao_id,
        nickname=user.nickname,
        profile_image=user.profile_image,
        connected_at=user.connected_at,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User added",
        "user": {
            "kakao_id": new_user.kakao_id,
            "nickname": new_user.nickname,
            "profile_image": new_user.profile_image,
        },
    }
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

# 루틴 생성 - 선택한 운동들 임시 저장
def save_temporary_routines_in_db(db: Session, routines: List[RoutineCreate]):

    for routine in routines:
        new_routine = Routine(
            user_id=routine.user_id,
            exercise_id=routine.exercise_id,
            sets=routine.sets,
            reps=routine.reps,
        )
        db.add(new_routine)
    
    db.commit()

# 루틴 이름 추가
def update_routine_name_in_db(db: Session, user_id: int, routine_name: str) -> bool:

    # user_id와 routine_name IS NULL인 경우 필터링
    routines = db.query(Routine).filter(
        Routine.user_id == user_id,
        Routine.routine_name == None
    ).all()

    if not routines:
        # 업데이트할 데이터가 없는 경우 False 반환
        return False

    # 이름 업데이트
    for routine in routines:
        routine.routine_name = routine_name

    db.commit()
    return True


# 루틴 가져오는 용 - 루틴 이름으로 조회
def get_routines_by_name_in_db(db: Session, user_id: int, routine_name: str):

    routines = db.query(Routine).options(joinedload(Routine.exercise)).filter(
        Routine.user_id == user_id,
        Routine.routine_name == routine_name
    ).all()

    # 운동 데이터를 반환
    return [
        {
            "id": routine.id,
            "exercise_id": routine.exercise_id,
            "exercise_name": routine.exercise.name if routine.exercise else "Unknown Exercise",
            "sets": routine.sets,
            "reps": routine.reps,
        }
        for routine in routines
    ]

# 운동 데이터 전체 조회
def get_all_exercises(db : Session):
    return db.query(ExerciseName).all()

# 운동 이름으로 운동 조회하기
def search_exercises_by_name(db : Session, query: str):
    return db.query(ExerciseName).filter(ExerciseName.name.contains(query)).all()
