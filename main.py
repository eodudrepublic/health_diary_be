from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine, get_db
from auth import verify_kakao_token
from crud import get_user_by_kakao_id, create_user, get_todos_by_user, get_todos_by_friends, add_friend, create_timetable_entry
from schemas import OAuthToken, UserResponse, TimetableCreate, TimetableResponse
from models import User, Todo, Friend, Timetable
from datetime import datetime
from typing import Dict,List
from collections import defaultdict
from everytime import Everytime


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

# 할 일 불러오기기
@app.get("/users/{user_id}/todos")
def get_user_todos(user_id: int, date: str = None, db: Session = Depends(get_db)) -> Dict[str, Dict]:


    # 1. DB에서 사용자와 관련된 TODO 데이터 가져오기
    query = db.query(Todo).filter(Todo.user_id == user_id)

    # 날짜 필터 추가 (선택한 날짜가 있을 경우)
    if date:
        try:
            selected_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
        query = query.filter(Todo.date_created == selected_date)

    todos = query.all()

    # 2. 데이터가 없을 경우 빈 데이터 반환
    if not todos:
        return {}

    result = {}

    for todo in todos:
        category = todo.category
        if category not in result:
            result[category] = {}
        result[category]["isEditing"] = False
        result[category]["isPublic"] = not todo.is_locked
        if "tasks" not in result[category]:
            result[category]["tasks"] = []
        result[category]["tasks"].append({
            "text": todo.task,
            "isCompleted": todo.is_completed,
            "isEditing": False
        })

    return result


# 할 일 업데이트 엔드포인트 - 데이터 파싱 추가

def parse_and_store_todos(user_id: int, data: dict, db: Session):
    print(data)
    #  날짜 가져오기
    date_str = data.get("date")
    to_do_list = data.get("toDoList")

    if not date_str:
        raise HTTPException(status_code=400, detail="Both 'date' and 'toDoList' are required.")

# 날짜 파싱
    try:
        # "2025-01-08T00:00:00.000" 형태의 문자열에서 날짜 부분만 추출하여 파싱
        date_obj = datetime.strptime(date_str.split("T")[0], "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use 'YYYY-MM-DD'.")

    print('------------------------')

    # toDoList가 문자열인지 확인하고, 문자열이면 JSON으로 변환
    if isinstance(to_do_list, str):
        try:
            to_do_list = json.loads(to_do_list.replace("'", '"'))  # 문자열을 JSON으로 변환
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid toDoList format.")

    # 기존 할 일 삭제
    db.query(Todo).filter(Todo.user_id == user_id, Todo.date_created == date_obj).delete()

    # 새로운 할 일 추가
    for category, details in to_do_list.items():
        tasks = details.get("tasks", [])
        is_locked = not details.get("isPublic", True)
        for task in tasks:
            new_todo = Todo(
                user_id=user_id,
                date_created=date_obj,
                category=category,
                task=task.get("text", "No Task"),
                is_locked=is_locked,
                is_completed=task.get("isCompleted", False),
            )
            db.add(new_todo)

    db.commit()


@app.put("/users/{user_id}/todos")
def update_todo_list(user_id: int, data: dict, db: Session = Depends(get_db)):
    """
    사용자 ID와 특정 날짜의 할 일 목록을 업데이트합니다.
    """
    parse_and_store_todos(user_id, data, db)
    return {"message": "To-do list updated successfully."}


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

@app.get("/users/{user_id}/friends/todos")
def get_friends_todos(
    user_id: int,
    date: str = None,
    limit: int = 10,  # 한 번에 가져올 최대 데이터 개수 (기본값: 10)
    offset: int = 0,  # 건너뛸 데이터 시작 위치 (기본값: 0)
    db: Session = Depends(get_db)
):
    # 친구들의 todo 가져오기
    todos = get_todos_by_friends(db, user_id, date, limit=limit, offset=offset)

    if not todos:
        raise HTTPException(status_code=404, detail="No todos found for the user's friends")

    return todos


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

@app.post("/users/{user_id}/timetable", response_model=TimetableResponse)
def create_timetable(user_id: int, timetable: TimetableCreate, db: Session = Depends(get_db)):
    """
    사용자가 제출한 시간표 정보를 저장하고, URL을 2차원 배열로 변환하여 DB에 저장합니다.
    """
    try:
        print(f"Received data: user_id={user_id}, year={timetable.year}, season={timetable.season}, url={timetable.url}")

        # Everytime 객체 생성 및 2차원 배열로 변환
        everytime = Everytime(timetable.url)
        binary_array = everytime.get_timetable()
        if binary_array is None:
            raise HTTPException(status_code=400, detail="Failed to parse the timetable from the URL.")

        print(f"Parsed binary array: {binary_array}")

        # 새로운 시간표 데이터 삽입
        new_timetable = Timetable(
            user_id=user_id,  # user_id 저장
            year=timetable.year,
            season=timetable.season,
            url=timetable.url,
            array=binary_array  # 변환된 2차원 배열 저장
        )
        db.add(new_timetable)
        db.commit()
        db.refresh(new_timetable)

        return {
            "id": new_timetable.id,
            "user_id": new_timetable.user_id,  # user_id 반환
            "year": new_timetable.year,
            "season": new_timetable.season,
            "url": new_timetable.url,
            "array": new_timetable.array,
        }
    except Exception as e:
        print(f"Error occurred in create_timetable: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/users/{user_id}/timetable/{year}/{season}")
def get_timetable(user_id: int, year: int, season: int, db: Session = Depends(get_db)):
    """
    사용자의 특정 연도, 학기의 시간표를 조회합니다.
    """
    print(f"Fetching timetable for user_id={user_id}, year={year}, season={season}")
    timetable = db.query(Timetable).filter(
        Timetable.user_id == user_id,  # user_id 조건 추가
        Timetable.year == year,
        Timetable.season == season,
    ).first()

    if not timetable:
        raise HTTPException(status_code=404, detail="Timetable not found")

    print(f"Found timetable: {timetable}")
    return {
        "id": timetable.id,
        "user_id": timetable.user_id,  # user_id 반환
        "year": timetable.year,
        "season": timetable.season,
        "url": timetable.url,
        "array": timetable.array,  # 저장된 2차원 배열 반환
    }

