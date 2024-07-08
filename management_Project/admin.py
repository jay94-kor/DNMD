import streamlit as st
from utils.database import get_db, User
from sqlalchemy.orm import Session

def admin_screen():
    st.title("관리자 페이지")
    
    st.header("사용자 권한 관리")
    with get_db() as db:
        users = db.query(User).all()
        for user in users:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"사용자: {user.email}, 현재 권한: {'관리자' if user.is_admin else '일반 사용자'}")
            with col2:
                if st.button("권한 변경", key=f"change_role_{user.id}"):
                    user.is_admin = not user.is_admin
                    db.commit()
                    st.success(f"{user.email}의 권한이 변경되었습니다.")
                    st.experimental_rerun()

    st.header("시스템 설정")
    # 여기에 추가적인 관리자 기능을 구현할 수 있습니다.

if __name__ == "__main__":
    admin_screen()