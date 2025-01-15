from sqlalchemy.orm import Session, joinedload
from models import User, Friend, Routine, ExerciseName, Record, MealPhoto, OwnPhoto, BodyMetrics
from typing import Optional, List
from schemas import RoutineCreate, UserLoginRequest, BodyMetricsCreate, RoutineUpdateRequest, ExerciseUpdateRequest
from datetime import datetime
from fastapi import HTTPException
import base64
import re
import os

def manage_user_in_db(db: Session, user: UserLoginRequest):

    # 기존 유저 확인
    existing_user = db.query(User).filter(User.kakao_id == user.kakao_id).first()
    if existing_user:
        return {
            "message": "User exists",
            "user": {
                "id": existing_user.id, #임의 추가
                "kakao_id": existing_user.kakao_id,
                "nickname": existing_user.nickname,
                "profile_image": existing_user.profile_image,
            },
        }

    # 새로운 유저 추가
    new_user = User(
        id = user.id, # 임의 추가
        kakao_id=user.kakao_id,
        nickname=user.nickname,
        profile_image=user.profile_image,
        # connected_at=user.connected_at,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User added",
        "user": {
            "id" : new_user.id,
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
        # 동일한 user_id와 exercise_id, routine_id로 저장된 루틴이 없으면 추가
        existing_routine = db.query(Routine).filter(
            Routine.user_id == routine.user_id,
            Routine.exercise_id == routine.exercise_id,
            Routine.routine_id == routine.routine_id
        ).first()

        if not existing_routine:
            new_routine = Routine(
                routine_id=routine.routine_id,
                user_id=routine.user_id,
                exercise_id=routine.exercise_id,
                sets=routine.sets,
                reps=routine.reps,
            )
            db.add(new_routine)
    
    db.commit()

# 루틴 이름을 업데이트하는 함수
def update_routine_name_in_db(db: Session, user_id: int, routine_name: str):
    # user_id와 동일한 routine_id를 가진 모든 루틴을 가져옵니다.
    routines = db.query(Routine).filter(Routine.user_id == user_id).all()

    # 루틴이 없다면 False 반환
    if not routines:
        print("Debug: No routines found to update.")
        return False

    # 루틴 이름 업데이트
    for routine in routines:
        # 동일한 routine_id를 가진 루틴이 있으면 routine_name을 동일하게 업데이트
        routine.routine_name = routine_name

    db.commit()
    print("Debug: Routines updated successfully.")
    return True

# 특정 사용자의 루틴 이름, 운동 별 세트, 횟수 수정
def update_routine_details_and_name(
    db: Session, user_id: int, routine_id: int, routine_name: Optional[str], exercises: List[ExerciseUpdateRequest]
) -> List[Routine]:
    updated_routines = []
    
    for exercise in exercises:
        routine = db.query(Routine).filter(
            Routine.id == routine_id,
            Routine.user_id == user_id,
            Routine.exercise_id == exercise.exercise_id
        ).first()

        if not routine:
            raise HTTPException(status_code=404, detail=f"Routine not found for Exercise ID {exercise.exercise_id}")

        # 세트 수와 반복 횟수 수정
        routine.sets = exercise.sets
        routine.reps = exercise.reps

        # 루틴 이름 수정 (필요시)
        if routine_name:
            routine.routine_name = routine_name

        db.commit()
        db.refresh(routine)
        updated_routines.append(routine)

    return updated_routines

# # 루틴 가져오는 용 - 루틴 이름으로 조회
# def get_routines_by_name_in_db(db: Session, user_id: int, routine_name: str):

#     routines = db.query(Routine).options(joinedload(Routine.exercise)).filter(
#         Routine.user_id == user_id,
#         Routine.routine_name == routine_name
#     ).all()

#     # 운동 데이터를 반환
#     return [
#         {
#             "id": routine.id,
#             "exercise_id": routine.exercise_id,
#             "exercise_name": routine.exercise.name if routine.exercise else "Unknown Exercise",
#             "sets": routine.sets,
#             "reps": routine.reps,
#         }
#         for routine in routines
#     ]

# 운동 데이터 전체 조회
def get_all_exercises(db : Session):
    return db.query(ExerciseName).all()

# 운동 이름으로 운동 조회하기
def search_exercises_by_name(db : Session, query: str):
    return db.query(ExerciseName).filter(ExerciseName.name.contains(query)).all()

# 프로필, 운동 완료 일수 반환
def get_user_profile(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 운동 완료 일수 계산 (Record 테이블 기준)
    completed_days = db.query(Record).filter(Record.user_id == user_id).count()

    return {
        "user_id": user.id,  # 사용자 ID 추가
        "nickname": user.nickname,
        "profile_image": user.profile_image,
        "completed_days": completed_days,
    }


# 운동 완료 날짜를 캘린더에 표시하기 - 사용자의 운동 기록 데이터 날짜 별로 가져오기 / postman 확인 완료료
def get_user_records(db: Session, user_id: int):

    # 사용자 존재 여부 확인
    user_exists = db.query(User).filter(User.id == user_id).first()
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    # 운동 기록 데이터 조회
    records = db.query(Record).filter(Record.user_id == user_id).all()
    if not records:
        return []  # 기록이 없으면 빈 리스트 반환

    # 날짜별 기록 데이터 반환
    return [
        {
            "date": record.datetime.date(),
            "weight": record.weight,
            "body_fat": record.body_fat,
            "muscle_mass": record.muscle_mass,
        }
        for record in records
    ]

# 오운완 사진 DB 저장 
def save_own_photo(db: Session, user_id: int, photo_path: str):

    print(f"Saving photo for user_id={user_id}, photo_path={photo_path}")
    new_photo = OwnPhoto(
        user_id=user_id,
        photo_path=photo_path,
        datetime=datetime.now(),  # 현재 시간을 저장
        is_uploaded=False  # 기본적으로 소셜탭에 업로드되지 않은 상태
    )
    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)
    return new_photo

# 내 오운완 사진 전체 조회 - postman 확인 완료
def get_own_photos_by_user(db: Session, user_id: int):

    return db.query(OwnPhoto).filter(OwnPhoto.user_id == user_id).all()

# 소셜탭에 오운완 사진 업로드 하기
def mark_photo_as_uploaded(db: Session, photo_id: int, user_id: int):

    photo = db.query(OwnPhoto).filter(OwnPhoto.id == photo_id, OwnPhoto.user_id == user_id).first()
    if not photo:
        return None
    photo.is_uploaded = True  # 업로드 상태로 변경
    db.commit()
    db.refresh(photo)
    return photo

# 소셜탭에서 나랑 친구들이 업로드한 모든 사진 보기
def get_social_photos(db: Session, user_id: int):

    # 내 친구들의 ID 가져오기
    friends_subquery = db.query(Friend.friend_id).filter(Friend.user_id == user_id).subquery()

    # 내 사진 및 친구들의 업로드된 사진 조회
    photos = db.query(OwnPhoto).filter(
        (OwnPhoto.user_id == user_id) |  # 내 사진
        (OwnPhoto.user_id.in_(friends_subquery))  # 친구들의 사진
    ).filter(OwnPhoto.is_uploaded == True).all()  # 업로드된 사진만 반환
    return photos

# 식단 사진 DB 저장 
def save_meal_photo(db: Session, user_id: int, photo_path: str):

    new_meal_photo = MealPhoto(
        user_id=user_id,
        datetime=datetime.now(),  
        photo_path=photo_path
    )
    db.add(new_meal_photo)
    db.commit()
    db.refresh(new_meal_photo)
    return new_meal_photo

# 내 식단 사진 전체 조회
def get_all_meal_photos_by_user(db: Session, user_id: int):

    return db.query(MealPhoto).filter(MealPhoto.user_id == user_id).all()

# 사용자의 체중 및 골격근량, 체지방률 기록 생성
def create_body_metrics(db: Session, user_id: int, metrics_data: BodyMetricsCreate) -> BodyMetrics:
    # 새로운 BodyMetrics 객체 생성
    body_metrics = BodyMetrics(
        user_id=user_id,
        record_date=metrics_data.record_date,
        weight=metrics_data.weight,
        muscle_mass=metrics_data.muscle_mass,
        body_fat_percentage=metrics_data.body_fat_percentage,
    )
    db.add(body_metrics)
    db.commit()
    db.refresh(body_metrics)  
    return body_metrics

#사용자의 체중 및 골격근량, 체지방률 기록 조회
def get_user_body_metrics(db: Session, user_id: int) -> list[BodyMetrics]:
    return db.query(BodyMetrics).filter(BodyMetrics.user_id == user_id).order_by(BodyMetrics.record_date).all()