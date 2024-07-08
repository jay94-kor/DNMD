import streamlit as st
from utils.database import get_db, User
from sqlalchemy.orm import Session

def user_management_screen():
    st.title("사용자 관리")
    
    st.header("사용자 리스트")
    db = next(get_db())
    users = db.query(User).all()
    user_data = [{"이름": user.name, "이메일": user.email} for user in users]
    st.table(user_data)
    
    st.header("새 사용자 추가")
    name = st.text_input("이름", placeholder="이름을 입력하세요")
    email = st.text_input("이메일", placeholder="이메일을 입력하세요")
    password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
    if st.button("추가"):
        from utils.auth import register_user
        user = register_user(db, name, email, password)
        if user:
            st.success("사용자가 추가되었습니다.")
        else:
            st.error("사용자 추가 실패")
    
    st.header("사용자 계정 삭제")
    email_to_delete = st.text_input("삭제할 사용자 이메일", placeholder="이메일을 입력하세요")
    if st.button("삭제"):
        user_to_delete = db.query(User).filter(User.email == email_to_delete).first()
        if user_to_delete:
            db.delete(user_to_delete)
            db.commit()
            st.success("사용자 계정이 삭제되었습니다.")
        else:
            st.error("사용자를 찾을 수 없습니다.")

if __name__ == "__main__":
    user_management_screen()
