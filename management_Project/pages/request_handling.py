import streamlit as st

def request_handling_screen():
    st.title("수정 요청 처리")
    
    st.header("수정 요청 리스트")
    # 예제 데이터 (실제로는 DB에서 조회)
    requests = [{"project_name": "프로젝트 A", "request": "기능 추가", "time": "2023-07-01 12:00"}, {"project_name": "프로젝트 B", "request": "버그 수정", "time": "2023-07-02 14:00"}]
    st.table(requests)
    
    st.header("수정 요청 처리")
    request_id = st.text_input("요청 ID", placeholder="요청 ID를 입력하세요")
    request_action = st.selectbox("처리 상태", ["승인", "반려"])
    request_reason = st.text_area("사유 입력", placeholder="처리 사유를 입력하세요")
    if st.button("처리"):
        # 수정 요청 처리 로직 (DB 업데이트)
        st.success(f"요청 ID {request_id}가 {request_action}되었습니다.")

if __name__ == "__main__":
    request_handling_screen()
