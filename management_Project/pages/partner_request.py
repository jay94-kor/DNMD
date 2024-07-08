import streamlit as st

def partner_request_screen():
    st.title("협력사 추가 요청")
    
    st.header("협력사 추가 요청")
    partner_name = st.text_input("협력사 이름", placeholder="협력사 이름을 입력하세요")
    contact = st.text_input("연락처", placeholder="연락처를 입력하세요")
    email = st.text_input("이메일", placeholder="이메일을 입력하세요")
    if st.button("요청"):
        # 협력사 추가 요청 로직
        st.success("협력사 추가 요청이 접수되었습니다.")

if __name__ == "__main__":
    partner_request_screen()
