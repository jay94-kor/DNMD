import streamlit as st
from utils.auth import register_user
from utils.database import get_db
from sqlalchemy.orm import Session

def signup_screen():
    st.title("회원가입")
    name = st.text_input("이름", placeholder="이름을 입력하세요")
    email = st.text_input("이메일", placeholder="이메일을 입력하세요")
    password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
    confirm_password = st.text_input("비밀번호 확인", type="password", placeholder="비밀번호를 다시 입력하세요")
    
    if st.button("회원가입"):
        if password == confirm_password:
            db = next(get_db())
            user = register_user(db, name, email, password)
            if user:
                st.success("회원가입 성공")
                st.experimental_set_query_params(page="Login")
            else:
                st.error("회원가입 실패. 이메일을 다시 확인하세요.")
        else:
            st.error("비밀번호가 일치하지 않습니다")

if __name__ == "__main__":
    signup_screen()
