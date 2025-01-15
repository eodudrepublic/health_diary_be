from sqlalchemy import Column, Integer, String, Boolean, Text, Date, DateTime, ForeignKey, UniqueConstraint,  Float
from sqlalchemy.orm import relationship
from database import Base

# 데이터베이스 모델을 정의함

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    kakao_id = Column(String, unique=True, index=True, nullable=False)
    nickname = Column(String, nullable=True)
    profile_image = Column(String, nullable=True)
    connected_at = Column(String, nullable=True)

    # Relationships
    records = relationship("Record", back_populates="user")
    meal_photos = relationship("MealPhoto", back_populates="user")
    own_photos = relationship("OwnPhoto", back_populates="user")
    body_metrics = relationship("BodyMetrics", back_populates="user")

class Friend(Base):
    __tablename__ = "friends"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 현재 사용자 ID
    friend_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 친구 사용자 ID

    # UniqueConstraint를 통해 동일한 사용자 간 중복된 관계 방지
    __table_args__ = (UniqueConstraint('user_id', 'friend_id', name='unique_friendship'),)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="friends")  # 현재 사용자
    friend = relationship("User", foreign_keys=[friend_id])  # 친구 사용자


class ExerciseName(Base):
    __tablename__ = "exercise_names"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # 운동 이름
    target_area = Column(String, nullable=False)  # 자극 부위
    # image_url = Column(String, nullable=True) # 운동 이미지 url - 대영이 짤 넣기~


class Routine(Base):
    __tablename__ = "routines"

    id = Column(Integer, primary_key=True, index=True)
    routine_id = Column(Integer, index=True)  # 동일한 루틴 ID를 사용하는 운동들
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 사용자 ID
    exercise_id = Column(Integer, ForeignKey("exercise_names.id"), nullable=False)  # 운동 ID
    routine_name = Column(String, nullable=True)
    sets = Column(Integer, nullable=False)  # 세트 수
    reps = Column(Integer, nullable=False)  # 반복 횟수

    # Relationships
    user = relationship("User")
    exercise = relationship("ExerciseName")


class OwnPhoto(Base):
    __tablename__ = "own_photos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    datetime = Column(DateTime, nullable=False)
    photo_path = Column(Text, nullable=False)
    is_uploaded = Column(Boolean, default=False)  # 소셜탭 업로드 여부 추가

    # Relationships
    user = relationship("User", back_populates="own_photos")


class MealPhoto(Base):
    __tablename__ = "meal_photos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 사용자 ID
    datetime = Column(DateTime, nullable=False)  # 사진 찍은 날짜 및 시간
    photo_path = Column(Text, nullable=False)  # 사진 경로

    # Relationships
    user = relationship("User", back_populates="meal_photos")

class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 사용자 ID
    datetime = Column(DateTime, nullable=False)  # 기록 날짜 및 시간
    weight = Column(Integer, nullable=False)  # 몸무게
    body_fat = Column(Integer, nullable=False)  # 체지방량
    muscle_mass = Column(Integer, nullable=False)  # 골격근량

    # Relationships
    user = relationship("User", back_populates="records")

class BodyMetrics(Base):
    __tablename__ = "body_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 사용자 ID
    record_date = Column(Date, nullable=False)  # 기록 날짜
    weight = Column(Float, nullable=False)  # 체중 (kg)
    muscle_mass = Column(Float, nullable=False)  # 골격근량 (kg)
    body_fat_percentage = Column(Float, nullable=False)  # 체지방률 (%)

    # Relationships
    user = relationship("User", back_populates="body_metrics")