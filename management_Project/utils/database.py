import os
from pathlib import Path

# 프로젝트 루트 디렉토리 찾기
project_root = Path(__file__).parent.parent

# config.yaml 파일의 절대 경로 생성
config_path = os.path.join(project_root, 'config', 'config.yaml')

# config 모듈에서 settings 가져오기
from config import load_config
settings = load_config(config_path)

from sqlalchemy import create_engine, Column, Integer, String, Sequence, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from contextlib import contextmanager
import logging

DATABASE_URL = settings['database']['url']  # 설정 파일에서 데이터베이스 URL 가져오기

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, Sequence("user_id_seq"), primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, Sequence("project_id_seq"), primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    admin_user = db.query(User).filter(User.email == "admin").first()
    if not admin_user:
        admin_user = User(
            name="Admin",
            email="admin",
            hashed_password="$2b$12$4v1z8jFn7JXsoXsTfyC5KOPO5FhbApQW1XZZP5HqThk63As1xMs.W",  # dnmdadmin!의 해시된 값
            is_admin=True
        )
        db.add(admin_user)
        db.commit()
    db.close()

def test_db_connection():
    try:
        with get_db() as db:
            db.execute("SELECT 1")
        print("데이터베이스 연결 성공")
    except Exception as e:
        print(f"데이터베이스 연결 실패: {e}")

if __name__ == "__main__":
    init_db()
    test_db_connection()