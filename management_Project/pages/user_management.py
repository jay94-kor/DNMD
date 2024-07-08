import streamlit as st
from utils.database import get_db, User
from sqlalchemy.orm import Session

def user_management_screen():
    st.title("사용자 관리")
    
    query_params = st.experimental_get_query_params()
    email = query_params.get("email", [None])[0]

    db = next(get_db())
    user = db.query(User).filter(User.email == email).first()

    if user and user.is_admin:
        st.write("관리자가 사용자 계정을 관리할 수 있습니다.")
        
        users = db.query(User).all()
        for user in users:
            st.write(f"사용자: {user.email}, 관리자 권한: {user.is_admin}")
            if st.button(f"권한 부여 ({user.email})"):
                user.is_admin = not user.is_admin
                db.commit()
                st.success(f"{user.email}의 관리자 권한이 변경되었습니다.")
    else:
        st.write("관리자만 접근할 수 있는 페이지입니다.")

if __name__ == "__main__":
    user_management_screen()
