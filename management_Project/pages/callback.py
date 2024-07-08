import streamlit as st
from utils.naverworks_login import get_naverworks_token, get_naverworks_user_info

def callback_screen():
    st.title("네이버웍스 로그인 콜백 처리")

    query_params = st.experimental_get_query_params()
    code = query_params.get("code", [None])[0]
    state = query_params.get("state", [None])[0]
    
    if code and state == 'naverworks':
        try:
            token = get_naverworks_token(code, state)
            if token:
                user_info = get_naverworks_user_info(token)
                if user_info['email'].endswith('@dnmd.com'):
                    st.success(f"{user_info['name']}님 환영합니다!")
                    st.session_state.logged_in = True
                    st.session_state.user_email = user_info['email']
                    st.experimental_set_query_params(page="Dashboard")
                else:
                    st.error("@dnmd.com 이메일 주소를 가진 사용자만 로그인할 수 있습니다.")
            else:
                st.error("네이버웍스 로그인 실패")
        except Exception as e:
            st.error(f"네이버웍스 로그인 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    callback_screen()
