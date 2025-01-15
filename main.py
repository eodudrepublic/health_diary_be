from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine, get_db
from crud import add_friend,save_temporary_routines_in_db, update_routine_name_in_db, get_all_exercises, search_exercises_by_name, manage_user_in_db, get_user_profile, save_own_photo
from schemas import RoutineCreate, UserLoginRequest, UserLoginResponse, OwnPhotoResponse, OwnPhotoCreate, PhotoUploadRequest, MealPhotoResponse, MealPhotoCreate,  PhotoUploadResponse, BodyMetricsCreate, BodyMetricsResponse, RoutineUpdateRequest, RoutineResponse, RoutineNameUpdateRequest, RoutineCreateList
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

@app.post("/users/login", response_model=UserLoginResponse)
def login(user: UserLoginRequest, db: Session = Depends(get_db)):
    result = manage_user_in_db(db, user)
    return {
        "id": result["user"]["id"],  # 수정: id -> user_id
        "message": result["message"],
        "user": result["user"],
    }

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
    friend_list = []
    if not friends:
        raise HTTPException(status_code=404, detail="No friends found for the user")

    # 친구 목록 데이터를 반환
    for friend in friends:
        friend_user = db.query(User).filter(User.id == friend.friend_id).first()
        if friend_user:
            friend_list.append({
                "id": friend_user.id,
                "nickname": friend_user.nickname,
                "profile_image": friend_user.profile_image,
            })

    return {"friends": friend_list}

# 루틴 생성 - 선택한 운동들 임시 저장 (routine_id 사용)
@app.post("/users/{user_id}/routines/temporary")
def save_temporary_routines(user_id: int, routines: RoutineCreateList, db: Session = Depends(get_db)):
    # 루틴 임시 저장
    save_temporary_routines_in_db(db, routines.routines)
    return {"message": "Temporary routines saved successfully!"}

# # 루틴 이름을 업데이트하는 함수
# @app.put("/users/{user_id}/routines/{routine_id}/name", response_model=RoutineResponse)
# def update_routine_name(
#     user_id: int,
#     routine_id: int,
#     routine_name: RoutineNameUpdateRequest,  # 요청 본문으로 받기
#     db: Session = Depends(get_db)
# ):
#     from crud import update_routine_name_in_db

#     try:
#         # 루틴 이름을 업데이트
#         updated_routine = update_routine_name_in_db(db, user_id, routine_id, routine_name.routine_name)
#         if not updated_routine:
#             raise HTTPException(status_code=404, detail="Routine not found.")
#         return updated_routine
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error updating routine name: {str(e)}")

@app.put("/users/{user_id}/routines/{routine_id}/update_name")
def update_routine_name(user_id: int, routine_id: int, routine_name: str, db: Session = Depends(get_db)):
    try:
        # 루틴 이름 업데이트 함수 호출
        success = update_routine_name_in_db(db, user_id, routine_name)
        if not success:
            raise HTTPException(status_code=404, detail="No routines found to update.")
        return {"message": f"Routine name updated to '{routine_name}' successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating routine name: {str(e)}")

# 특정 사용자의 루틴 이름, 운동 별 세트, 횟수 수정
@app.put("/users/{user_id}/routines/{routine_id}/update", response_model=List[RoutineResponse])
def update_routine(
    user_id: int,
    routine_id: int,
    routine_data: RoutineUpdateRequest,
    db: Session = Depends(get_db)
):
    from crud import update_routine_details_and_name

    try:
        # 루틴의 세트와 반복 횟수, 그리고 루틴 이름을 수정
        updated_routines = update_routine_details_and_name(
            db, user_id, routine_id, routine_data.routine_name, routine_data.exercises
        )
        return updated_routines
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

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

# 사용자 프로필, 운동 완료 일수 불러오기
@app.get("/users/{user_id}/profile")
def get_user_profile_endpoint(user_id: int, db: Session = Depends(get_db)):
    return get_user_profile(db, user_id)

# 운동 완료 날짜를 캘린더에 표시하기 - 사용자의 운동 기록 데이터 날짜 별로 가져오기
@app.get("/users/{user_id}/records")
def get_user_records_endpoint(user_id: int, db: Session = Depends(get_db)):

    from crud import get_user_records
    return get_user_records(db, user_id)

# 오운완 사진 DB 저장
@app.post("/users/{user_id}/own_photos", response_model=OwnPhotoResponse)
def upload_own_photo_endpoint(
    user_id: int,
    photo: OwnPhotoCreate,
    db: Session = Depends(get_db)
):
    try:
        # 사진 저장
        photo_data = save_own_photo(db, user_id, photo.photo_path)

        # Pydantic 모델로 변환하여 반환
        return photo_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# 내 오운완 사진 전체 조회
@app.get("/users/{user_id}/own_photos", response_model=list[OwnPhotoResponse])
def get_user_own_photos(user_id: int, db: Session = Depends(get_db)):

    from crud import get_own_photos_by_user
    photos = get_own_photos_by_user(db, user_id)
    if not photos:
        raise HTTPException(status_code=404, detail="No photos found for this user")
    return photos

# 소셜탭에 오운완 사진 업로드 하기
@app.post("/users/{user_id}/social/upload", response_model=OwnPhotoResponse)
def upload_to_social_tab(
    user_id: int,
    request: PhotoUploadRequest,
    db: Session = Depends(get_db)
):

    from crud import mark_photo_as_uploaded

    photo = mark_photo_as_uploaded(db, request.photo_id, user_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found or not authorized")
    return photo

# 소셜탭에서 나랑 친구들이 업로드한 모든 사진 보기
@app.get("/users/{user_id}/social/photos", response_model=list[OwnPhotoResponse])
def get_all_social_photos(user_id: int, db: Session = Depends(get_db)):

    from crud import get_social_photos

    photos = get_social_photos(db, user_id)
    if not photos:
        raise HTTPException(status_code=404, detail="No social photos found")
    return photos

# 식단 사진 DB 저장
@app.post("/users/{user_id}/meal_photos", response_model=MealPhotoResponse)
def upload_meal_photo(
    user_id: int,
    photo: MealPhotoCreate,
    db: Session = Depends(get_db)
):
    
    from crud import save_meal_photo

    try:
        # 식단 사진 저장
        meal_photo = save_meal_photo(db, user_id, photo.photo_path)
        return meal_photo
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# 내 식단 사진 전체 조회
@app.get("/users/{user_id}/meal_photos", response_model=list[MealPhotoResponse])
def get_meal_photos(user_id: int, db: Session = Depends(get_db)):

    from crud import get_all_meal_photos_by_user

    photos = get_all_meal_photos_by_user(db, user_id)
    if not photos:
        raise HTTPException(status_code=404, detail="No meal photos found for this user")
    return photos

# 사용자의 체중 및 골격근량, 체지방률 기록 추가
@app.post("/users/{user_id}/body_metrics", response_model=BodyMetricsResponse)
def add_body_metrics(
    user_id: int,
    metrics_data: BodyMetricsCreate,
    db: Session = Depends(get_db),
):
    from crud import create_body_metrics
    try:
        # CRUD 함수 호출
        new_metrics = create_body_metrics(db, user_id, metrics_data)
        return new_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save body metrics: {str(e)}")

# 사용자의 체중 및 골격근량, 체지방률 기록 조회
@app.get("/users/{user_id}/body_metrics", response_model=List[BodyMetricsResponse])
def get_body_metrics(user_id: int, db: Session = Depends(get_db)):

    from crud import get_user_body_metrics

    try:
        records = get_user_body_metrics(db, user_id)
        if not records:
            raise HTTPException(status_code=404, detail="No records found for the user")
        
        # Pydantic 스키마로 변환
        return [BodyMetricsResponse.from_orm(record) for record in records]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch records: {str(e)}")
    
# # 사용자 설정 저장 - 다크 모드, 앱 지문 잠금, 보이스 알림 대영/현정 설정
# @app.post("/users/{user_id}/settings")
# def ():


