import streamlit as st

def output_management_screen():
    st.title("산출내역서 관리")
    
    st.header("산출내역서 리스트")
    st.table([{"항목": "산출내역서 1", "금액": 100000}, {"항목": "산출내역서 2", "금액": 200000}])
    
    st.header("새로운 산출내역서 추가")
    output_item = st.text_input("항목명", placeholder="산출내역서 항목을 입력하세요")
    amount = st.number_input("금액", min_value=0)
    if st.button("추가"):
        # 산출내역서 추가 로직
        st.success("산출내역서가 추가되었습니다.")

if __name__ == "__main__":
    output_management_screen()
