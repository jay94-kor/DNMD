import streamlit as st
from utils.database import get_db, User
from sqlalchemy.orm import Session

def user_management_screen():
    st.title("사용자 관리")
    
    with get_db() as db:
        users = db.query(User).all()
        for user in users:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"사용자: {user.email}, 관리자 권한: {user.is_admin}")
            with col2:
                if st.button("삭제", key=f"delete_{user.id}"):
                    if 'confirm_delete_user' not in st.session_state:
                        st.session_state.confirm_delete_user = user.id
                    elif st.session_state.confirm_delete_user == user.id:
                        db.delete(user)
                        db.commit()
                        st.success(f"사용자 '{user.email}' 삭제 완료")
                        st.session_state.pop('confirm_delete_user', None)
                        st.experimental_rerun()
                    else:
                        st.warning("정말 삭제하시겠습니까?")
                        st.session_state.confirm_delete_user = user.id

    st.header("관리자 권한 부여")
    st.write("관리자 권한 부여는 별도의 관리 페이지에서 수행할 수 있습니다.")

if __name__ == "__main__":
    user_management_screen()
