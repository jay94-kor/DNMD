import streamlit as st
from utils.auth import authenticate_user
from utils.database import get_db
from sqlalchemy.orm import Session
from utils.naverworks_login import get_naverworks_login_url, get_naverworks_token, get_naverworks_user_info

def login_screen():
    st.title("로그인")

    # 네이버웍스 로그인 URL 가져오기
    naverworks_login_url = get_naverworks_login_url()
    st.markdown(f'<a href="{naverworks_login_url}" target="_self"><button>네이버웍스 로그인</button></a>', unsafe_allow_html=True)
    
    email = st.text_input("이메일", placeholder="이메일을 입력하세요")
    password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
    
    if st.button("로그인"):
        db = next(get_db())
        user = authenticate_user(db, email, password)
        if user:
            st.success("로그인 성공")
            st.experimental_set_query_params(page="Dashboard")
        else:
            st.error("로그인 실패. 이메일 또는 비밀번호를 확인하세요.")

    st.write("아직 계정이 없으신가요?")
    if st.button("회원가입"):
        st.experimental_set_query_params(page="Signup")

    # 네이버웍스 로그인 콜백 처리
    query_params = st.experimental_get_query_params()
    code = query_params.get("code", [None])[0]
    state = query_params.get("state", [None])[0]
    if code and state == 'naverworks':
        token = get_naverworks_token(code, state)
        if token:
            user_info = get_naverworks_user_info(token)
            st.success(f"{user_info['name']}님 환영합니다!")
            # 네이버웍스 사용자 정보를 활용한 추가 처리 로직 (회원가입, 로그인 등)
        else:
            st.error("네이버웍스 로그인 실패")

if __name__ == "__main__":
    login_screen()
