from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine, get_db
from auth import verify_kakao_token
from crud import get_user_by_kakao_id, create_user, add_friend,save_temporary_routines_in_db, update_routine_name_in_db, get_routines_by_name_in_db, get_all_exercises, search_exercises_by_name 
from schemas import OAuthToken, UserResponse, RoutineCreate
from models import User, Friend, ExerciseName, Routine, MealPhoto, OwnPhoto, Record
from datetime import datetime
from typing import Dict,List
from collections import defaultdict


app = FastAPI()

# 테이블 생성
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Server is running"}

@app.get("/users")
def read_root():
    return {"message": "Server is running"}

#로그인 화면
@app.post("/users/login", response_model=UserResponse)
def login_or_register_with_kakao(token: OAuthToken, db: Session = Depends(get_db)):
    kakao_user_info = verify_kakao_token(token.oauth_token)

    user = get_user_by_kakao_id(db, kakao_id=kakao_user_info["id"])
    if not user:
        user = create_user(
            db,
            kakao_id=kakao_user_info["id"],
            connected_at=kakao_user_info.get("connected_at"),
            email=kakao_user_info.get("kakao_account", {}).get("email"),
            nickname=kakao_user_info.get("properties", {}).get("nickname"),
            profile_image=kakao_user_info.get("properties", {}).get("profile_image"),
            thumbnail_image=kakao_user_info.get("properties", {}).get("thumbnail_image"),
            profile_nickname_needs_agreement=kakao_user_info.get("kakao_account", {}).get(
                "profile_nickname_needs_agreement"
            ),
            profile_image_needs_agreement=kakao_user_info.get("kakao_account", {}).get(
                "profile_image_needs_agreement"
            ),
            is_default_image=kakao_user_info.get("kakao_account", {}).get("profile", {}).get(
                "is_default_image"
            ),
            is_default_nickname=kakao_user_info.get("kakao_account", {}).get("profile", {}).get(
                "is_default_nickname"
            ),
        )

    return UserResponse(
        id=user.id,
        kakao_id=user.kakao_id,
        connected_at=user.connected_at,
        email=user.email,
        nickname=user.nickname,
        profile_image=user.profile_image,
        thumbnail_image=user.thumbnail_image,
        profile_nickname_needs_agreement=user.profile_nickname_needs_agreement,
        profile_image_needs_agreement=user.profile_image_needs_agreement,
        is_default_image=user.is_default_image,
        is_default_nickname=user.is_default_nickname,
    )

# qr 코드로 친구 추가 엔드포인트
@app.post("/friends")
def create_friend(data: dict, db: Session = Depends(get_db)):
    # 1. 요청 데이터 검증
    scanned_user_id = data.get("scanned_user_id")
    qr_user_id = data.get("qr_user_id")
    if not scanned_user_id or not qr_user_id:
        raise HTTPException(status_code=400, detail="Both user IDs are required.")

    # 2. CRUD 함수 호출
    return add_friend(db, scanned_user_id, qr_user_id)  # crud.py의 함수를 호출

# 개인 friend 목록 볼 수 있는 tab4 의 엔드포인트 정리

@app.get("/users/{user_id}/friends")
def get_user_friends(user_id: int, db: Session = Depends(get_db)):
    """
    특정 사용자의 친구 목록을 반환합니다.
    """
    friends = db.query(Friend).filter(Friend.user_id == user_id).all()
    if not friends:
        raise HTTPException(status_code=404, detail="No friends found for the user")

    # 친구 목록 데이터를 반환
    friend_list = []
    for friend in friends:
        friend_user = db.query(User).filter(User.id == friend.friend_id).first()
        if friend_user:
            friend_list.append({
                "id": friend_user.id,
                "nickname": friend_user.nickname,
                "profile_image": friend_user.profile_image,
                "email": friend_user.email,
            })

    return {"friends": friend_list}

# 선택한 운동들 임시 저장
@app.post("/routines/temporary")
def save_temporary_routines(routines: List[RoutineCreate], db: Session = Depends(get_db)):

    save_temporary_routines_in_db(db, routines)
    return {"message": "Temporary routines saved successfully!"}
  
# 저장된 운동들에 루틴 이름 업데이트
@app.put("/routines/update_name")
def update_routine_name(user_id: int, routine_name: str, db: Session = Depends(get_db)):

    print(f"Request received: user_id={user_id}, routine_name={routine_name}")  # 요청 디버깅 로그

    try:
        success = update_routine_name_in_db(db, user_id, routine_name)
        print(f"Update success: {success}")  # 성공 여부 확인
    except Exception as e:
        print(f"Error during update: {e}")  # 예외 처리 로그
        raise HTTPException(status_code=500, detail="Failed to update routine name.")

    if not success:
        raise HTTPException(status_code=404, detail="No temporary routines found.")

    return {"message": f"Routine '{routine_name}' updated successfully!"}

# 특정 사용자의 루틴 이름으로 운동 조회
@app.get("/users/{user_id}/routines/{routine_name}")
def get_routines_by_name(user_id: int, routine_name: str, db: Session = Depends(get_db)):

    exercises = get_routines_by_name_in_db(db, user_id, routine_name)
    return {"routine_name": routine_name, "exercises": exercises}

# 전체 운동 목록 반환
@app.get("/exercises")
def get_all_exercises_list(db: Session = Depends(get_db)):

    exercises = get_all_exercises(db)
    return [
        {
            "id": exercise.id,
            "name": exercise.name,
            "target_area": exercise.target_area,
        }
        for exercise in exercises
    ]

# 운동 이름 검색
@app.get("/exercises/search")
def search_exercises(query: str, db: Session = Depends(get_db)):

    exercises = search_exercises_by_name(db, query)
    return [
        {
            "id": exercise.id,
            "name": exercise.name,
            "target_area": exercise.target_area,
        }
        for exercise in exercises
    ]