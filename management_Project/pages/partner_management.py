import streamlit as st

def partner_management_screen():
    st.title("협력사 관리")
    
    st.header("협력사 리스트")
    st.table([{"협력사 이름": "협력사 1", "연락처": "010-1234-5678"}, {"협력사 이름": "협력사 2", "연락처": "010-8765-4321"}])
    
    st.header("새로운 협력사 추가")
    partner_name = st.text_input("협력사 이름", placeholder="협력사 이름을 입력하세요")
    contact = st.text_input("연락처", placeholder="연락처를 입력하세요")
    if st.button("추가"):
        # 협력사 추가 로직
        st.success("협력사가 추가되었습니다.")

if __name__ == "__main__":
    partner_management_screen()
