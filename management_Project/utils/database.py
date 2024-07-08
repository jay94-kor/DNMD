from sqlalchemy import create_engine, Column, Integer, String, Sequence, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

DATABASE_URL = "sqlite:///./local_test.db"

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
