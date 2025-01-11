from sqlalchemy import Column, Integer, String, Boolean, Text, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

# 데이터베이스 모델을 정의함

class User(Base):
    __tablename__ = "users"

    # 기본 필드
    id = Column(Integer, primary_key=True, index=True)
    kakao_id = Column(String, unique=True, nullable=False)  # 카카오 사용자 ID
    connected_at = Column(String, nullable=True)  # 카카오와 연결된 시간
    email = Column(String, unique=True, nullable=True)  # 이메일 (카카오에서 필수 제공 아님)

    # properties 필드
    nickname = Column(String, nullable=True)  # 닉네임
    profile_image = Column(Text, nullable=True)  # 프로필 이미지 URL
    thumbnail_image = Column(Text, nullable=True)  # 썸네일 이미지 URL

    # kakao_account 필드
    profile_nickname_needs_agreement = Column(Boolean, nullable=True)  # 닉네임 동의 필요 여부
    profile_image_needs_agreement = Column(Boolean, nullable=True)  # 프로필 이미지 동의 필요 여부
    is_default_image = Column(Boolean, nullable=True)  # 기본 이미지 여부
    is_default_nickname = Column(Boolean, nullable=True)  # 기본 닉네임 여부

    # Relationships
    todos = relationship("Todo", back_populates="user")
    records = relationship("Record", back_populates="user")
    meal_photos = relationship("MealPhoto", back_populates="user")
    own_photos = relationship("OwnPhoto", back_populates="user")


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


class Routine(Base):
    __tablename__ = "routines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 사용자 ID
    exercise_id = Column(Integer, ForeignKey("exercise_names.id"), nullable=False)  # 운동 ID
    sets = Column(Integer, nullable=False)  # 세트 수
    reps = Column(Integer, nullable=False)  # 반복 횟수

    # Relationships
    user = relationship("User", back_populates="todos")
    exercise = relationship("ExerciseName")


class MealPhoto(Base):
    __tablename__ = "meal_photos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 사용자 ID
    datetime = Column(DateTime, nullable=False)  # 사진 찍은 날짜 및 시간
    photo_path = Column(Text, nullable=False)  # 사진 경로

    # Relationships
    user = relationship("User", back_populates="meal_photos")


class OwnPhoto(Base):
    __tablename__ = "own_photos"

    id = Column(Integer, primary_key=True, index=True)
    routine_id = Column(Integer, ForeignKey("routines.id"), nullable=False)  # 루틴 ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 사용자 ID (추가적인 조회용)
    datetime = Column(DateTime, nullable=False)  # 사진 찍은 날짜 및 시간
    photo_path = Column(Text, nullable=False)  # 사진 경로

    # Relationships
    routine = relationship("Routine")
    user = relationship("User", back_populates="own_photos")


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
