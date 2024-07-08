from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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

# 프로젝트 모델 정의
class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, Sequence("project_id_seq"), primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(String, index=True)

# 데이터베이스 초기화
def init_db():
    Base.metadata.create_all(bind=engine)
