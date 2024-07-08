import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import hashlib
import random
import string

# Database setup
DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, Sequence("user_id_seq"), primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, Sequence("project_id_seq"), primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(String, index=True)

def init_db():
    Base.metadata.create_all(bind=engine)

# Authentication helpers
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db, email, password):
    user = db.query(User).filter(User.email == email).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None

def register_user(db, name, email, password):
    hashed_password = get_password_hash(password)
    user = User(name=name, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Helper functions
def generate_random_string(length=12):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def hash_string(s):
    return hashlib.sha256(s.encode()).hexdigest()

# Streamlit app
def login_screen():
    st.title("로그인")
    email = st.text_input("이메일", placeholder="이메일을 입력하세요")
    password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
    
    if st.button("로그인"):
        db = SessionLocal()
        user = authenticate_user(db, email, password)
        if user:
            st.success("로그인 성공")
            st.experimental_set_query_params(page="dashboard")
        else:
            st.error("로그인 실패. 이메일 또는 비밀번호를 확인하세요.")
        db.close()

    st.markdown("[회원가입](#Signup)")

def signup_screen():
    st.title("회원가입")
    name = st.text_input("이름", placeholder="이름을 입력하세요")
    email = st.text_input("이메일", placeholder="이메일을 입력하세요")
    password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
    confirm_password = st.text_input("비밀번호 확인", type="password", placeholder="비밀번호를 다시 입력하세요")
    
    if st.button("회원가입"):
        if password == confirm_password:
            db = SessionLocal()
            user = register_user(db, name, email, password)
            if user:
                st.success("회원가입 성공")
                st.experimental_set_query_params(page="Login")
            else:
                st.error("회원가입 실패. 이메일을 다시 확인하세요.")
            db.close()
        else:
            st.error("비밀번호가 일치하지 않습니다")

def dashboard_screen():
    st.title("대시보드")
    
    st.header("전체 예산 상태")
    st.bar_chart({"금액": [1000000, 750000, 500000, 250000], "항목": ["배정 금액", "매출액", "사용액", "사용 요청액"]})
    
    st.header("프로젝트별 순이익률")
    st.line_chart({"프로젝트 A": [0.1, 0.15, 0.2], "프로젝트 B": [0.05, 0.1, 0.15]})
    
    st.header("사용자별 담당 프로젝트")
    st.table({"사용자": ["사용자 1", "사용자 2"], "프로젝트": ["프로젝트 A, 프로젝트 B", "프로젝트 C"], "평균 수익률": [0.15, 0.1]})
    
    st.header("그룹별 예산 사용 현황")
    st.area_chart({"그룹 A": [300000, 250000, 200000], "그룹 B": [400000, 350000, 300000]})

def project_management_screen():
    st.title("프로젝트 관리")
    
    st.header("새로운 프로젝트 생성")
    project_name = st.text_input("프로젝트 이름", placeholder="프로젝트 이름을 입력하세요")
    project_status = st.selectbox("프로젝트 상태", ["진행 중", "완료", "보류"])
    if st.button("프로젝트 생성"):
        db = SessionLocal()
        new_project = Project(name=project_name, status=project_status)
        db.add(new_project)
        db.commit()
        st.success(f"프로젝트 '{project_name}' 생성 완료")
        db.close()
    
    st.header("기존 프로젝트")
    db = SessionLocal()
    projects = db.query(Project).all()
    for project in projects:
        st.write(f"프로젝트 이름: {project.name}, 상태: {project.status}")
        st.button("수정", key=f"edit_{project.id}")
        st.button("삭제", key=f"delete_{project.id}")
    db.close()

def project_detail_screen():
    st.title("프로젝트 상세 정보")
    
    project_id = st.text_input("프로젝트 ID", placeholder="프로젝트 ID를 입력하세요")
    
    if st.button("조회"):
        db = SessionLocal()
        project = db.query(Project).filter(Project.id == project_id).first()
        
        if project:
            st.write(f"프로젝트 이름: {project.name}")
            st.write(f"프로젝트 상태: {project.status}")
            
            st.write("팀 멤버 리스트")
            team_members = [{"name": "멤버 1", "role": "개발자"}, {"name": "멤버 2", "role": "디자이너"}]
            st.table(team_members)
            
            st.write("산출내역서 리스트")
            outputs = [{"item": "산출내역서 1", "amount": 100000}, {"item": "산출내역서 2", "amount": 200000}]
            st.table(outputs)
            
            new_status = st.selectbox("프로젝트 상태 업데이트", ["진행 중", "완료", "보류"])
            if st.button("상태 업데이트"):
                project.status = new_status
                db.commit()
                st.success(f"프로젝트 상태가 '{new_status}'로 업데이트 되었습니다.")
            
            new_member = st.text_input("새 팀 멤버 추가", placeholder="팀 멤버 이름을 입력하세요")
            if st.button("멤버 추가"):
                st.success(f"팀 멤버 '{new_member}'가 추가되었습니다.")
            remove_member = st.text_input("팀 멤버 제거", placeholder="팀 멤버 이름을 입력하세요")
            if st.button("멤버 제거"):
                st.success(f"팀 멤버 '{remove_member}'가 제거되었습니다.")
        else:
            st.error("프로젝트를 찾을 수 없습니다.")
        db.close()

def request_handling_screen():
    st.title("수정 요청 처리")
    
    st.header("수정 요청 리스트")
    requests = [{"project_name": "프로젝트 A", "request": "기능 추가", "time": "2023-07-01 12:00"}, {"project_name": "프로젝트 B", "request": "버그 수정", "time": "2023-07-02 14:00"}]
    st.table(requests)
    
    st.header("수정 요청 처리")
    request_id = st.text_input("요청 ID", placeholder="요청 ID를 입력하세요")
    request_action = st.selectbox("처리 상태", ["승인", "반려"])
    request_reason = st.text_area("사유 입력", placeholder="처리 사유를 입력하세요")
    if st.button("처리"):
        st.success(f"요청 ID {request_id}가 {request_action}되었습니다.")

def user_management_screen():
    st.title("사용자 관리")
    
    st.header("사용자 리스트")
    db = SessionLocal()
    users = db.query(User).all()
    user_data = [{"이름": user.name, "이메일": user.email} for user in users]
    st.table(user_data)
    db.close()
    
    st.header("새 사용자 추가")
    name = st.text_input("이름", placeholder="이름을 입력하세요")
    email = st.text_input("이메일", placeholder="이메일을 입력하세요")
    password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
    if st.button("추가"):
        db = SessionLocal()
        from utils.auth import register_user
        user = register_user(db, name, email, password)
        if user:
            st.success("사용자가 추가되었습니다.")
        else:
            st.error("사용자 추가 실패")
        db.close()
    
    st.header("사용자 계정 삭제")
    email_to_delete = st.text_input("삭제할 사용자 이메일", placeholder="이메일을 입력하세요")
    if st.button("삭제"):
        db = SessionLocal()
        user_to_delete = db.query(User).filter(User.email == email_to_delete).first()
        if user_to_delete:
            db.delete(user_to_delete)
            db.commit()
            st.success("사용자 계정이 삭제되었습니다.")
        else:
            st.error("사용자를 찾을 수 없습니다.")
        db.close()

def output_management_screen():
    st.title("산출내역서 관리")
    
    st.header("산출내역서 리스트")
    st.table([{"항목": "산출내역서 1", "금액": 100000}, {"항목": "산출내역서 2", "금액": 200000}])
    
    st.header("새로운 산출내역서 추가")
    output_item = st.text_input("항목명", placeholder="산출내역서 항목을 입력하세요")
    amount = st.number_input("금액", min_value=0)
    if st.button("추가"):
        st.success("산출내역서가 추가되었습니다.")

def partner_management_screen():
    st.title("협력사 관리")
    
    st.header("협력사 리스트")
    st.table([{"협력사 이름": "협력사 1", "연락처": "010-1234-5678"}, {"협력사 이름": "협력사 2", "연락처": "010-8765-4321"}])
    
    st.header("새로운 협력사 추가")
    partner_name = st.text_input("협력사 이름", placeholder="협력사 이름을 입력하세요")
    contact = st.text_input("연락처", placeholder="연락처를 입력하세요")
    if st.button("추가"):
        st.success("협력사가 추가되었습니다.")

def partner_request_screen():
    st.title("협력사 추가 요청")
    
    st.header("협력사 추가 요청")
    partner_name = st.text_input("협력사 이름", placeholder="협력사 이름을 입력하세요")
    contact = st.text_input("연락처", placeholder="연락처를 입력하세요")
    email = st.text_input("이메일", placeholder="이메일을 입력하세요")
    if st.button("요청"):
        st.success("협력사 추가 요청이 접수되었습니다.")

# Main app
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select a page", ["Login", "Signup", "Dashboard", "Project Management", "Project Detail", "Output Management", "Request Handling", "User Management", "Partner Management", "Partner Request"])

    if page == "Login":
        login_screen()
    elif page == "Signup":
        signup_screen()
    elif page == "Dashboard":
        dashboard_screen()
    elif page == "Project Management":
        project_management_screen()
    elif page == "Project Detail":
        project_detail_screen()
    elif page == "Output Management":
        output_management_screen()
    elif page == "Request Handling":
        request_handling_screen()
    elif page == "User Management":
        user_management_screen()
    elif page == "Partner Management":
        partner_management_screen()
    elif page == "Partner Request":
        partner_request_screen()

if __name__ == "__main__":
    init_db()
    main()
