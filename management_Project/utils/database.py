from sqlalchemy import create_engine, Column, Integer, String, Sequence, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, scoped_session

from config import settings

# DATABASE_URL = "sqlite:///./local_test.db"
DATABASE_URL = "sqlite:////mount/src/dnmd/management_Project/local_test.db"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = Session(autoflush=False, bind=engine)


def get_db() -> scoped_session:
    try:
        yield SessionLocal
        SessionLocal.commit()
    except Exception as ex:
        logger.error(f"Something failed, rolling back database transaction. {ex}")
        SessionLocal.rollback()
        raise
    finally:
        SessionLocal.close()


class User(BaseModel):
    id: int
    name: str
    email: str
    password: str

    class Config:
        from_attributes = True


def init_db():
    User.metadata.create_all(engine)
    logger.info("Database initialized successfully.")


if __name__ == "__main__":
    init_db()
    test_db_connection()

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 사용자 모델 정의
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, Sequence("user_id_seq"), primary_key=True, index=True)
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

def init_db():
    Base.metadata.create_all(bind=engine)

    # 어드민 계정 추가
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
