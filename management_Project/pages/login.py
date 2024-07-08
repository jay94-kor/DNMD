import streamlit as st
from utils.auth import authenticate_user
from utils.database import get_db
from sqlalchemy.orm import Session

def login_screen():
    st.title("로그인")
    email = st.text_input("이메일", placeholder="이메일을 입력하세요")
    password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
    
    if st.button("로그인"):
        db = next(get_db())
        user = authenticate_user(db, email, password)
        if user:
            st.success("로그인 성공")
            st.experimental_set_query_params(page="dashboard")
        else:
            st.error("로그인 실패. 이메일 또는 비밀번호를 확인하세요.")

    st.markdown("[회원가입](#Signup)")

if __name__ == "__main__":
    login_screen()
