import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

# SQLite 데이터베이스 파일 경로
DATABASE_URL = "sqlite:///./local_test.db"

# SQLAlchemy 설정
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 사용자 모델 정의
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)

# 프로젝트 모델 정의
class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, Sequence("project_id_seq"), primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(String)

# 데이터베이스 생성 및 초기 데이터 삽입
def create_database():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # 관리자 계정 생성
    admin_password = "admin123"  # 실제 운영 환경에서는 더 강력한 비밀번호를 사용하세요
    hashed_admin_password = generate_password_hash(admin_password)
    
    admin_user = User(
        name="Admin",
        email="admin@example.com",
        hashed_password=hashed_admin_password,
        is_admin=True
    )
    
    db.add(admin_user)
    db.commit()
    
    print("데이터베이스가 생성되었고, 관리자 계정이 추가되었습니다.")
    db.close()

if __name__ == "__main__":
    create_database()