import streamlit as st
from utils.database import get_db, Project
from sqlalchemy.exc import SQLAlchemyError
import time

def project_management_screen():
    st.title("프로젝트 관리")
    
    st.header("새로운 프로젝트 생성")
    project_name = st.text_input("프로젝트 이름", placeholder="프로젝트 이름을 입력하세요")
    project_status = st.selectbox("프로젝트 상태", ["진행 중", "완료", "보류"])
    
    if st.button("프로젝트 생성"):
        if not project_name:
            st.error("프로젝트 이름을 입력해주세요.")
        else:
            with st.spinner("프로젝트 생성 중..."):
                try:
                    with get_db() as db:
                        new_project = Project(name=project_name, status=project_status)
                        db.add(new_project)
                        db.commit()
                    st.success(f"프로젝트 '{project_name}' 생성 완료")
                    time.sleep(1)  # 사용자가 메시지를 볼 수 있도록 잠시 대기
                    st.experimental_rerun()
                except SQLAlchemyError as e:
                    st.error(f"프로젝트 생성 중 오류 발생: {str(e)}")
    
    st.header("기존 프로젝트")
    try:
        with get_db() as db:
            projects = db.query(Project).all()
            for project in projects:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"프로젝트 이름: {project.name}, 상태: {project.status}")
                with col2:
                    if st.button("수정", key=f"edit_{project.id}"):
                        st.session_state.edit_project = project.id
                with col3:
                    if st.button("삭제", key=f"delete_{project.id}"):
                        if 'confirm_delete' not in st.session_state:
                            st.session_state.confirm_delete = project.id
                        elif st.session_state.confirm_delete == project.id:
                            with st.spinner("프로젝트 삭제 중..."):
                                try:
                                    db.delete(project)
                                    db.commit()
                                    st.success(f"프로젝트 '{project.name}' 삭제 완료")
                                    time.sleep(1)
                                    st.session_state.pop('confirm_delete', None)
                                    st.experimental_rerun()
                                except SQLAlchemyError as e:
                                    st.error(f"프로젝트 삭제 중 오류 발생: {str(e)}")
                        else:
                            st.warning("정말 삭제하시겠습니까?")
                            st.session_state.confirm_delete = project.id
    except SQLAlchemyError as e:
        st.error(f"프로젝트 목록 조회 중 오류 발생: {str(e)}")

    if 'edit_project' in st.session_state:
        edit_project(st.session_state.edit_project)

def edit_project(project_id):
    st.header("프로젝트 수정")
    try:
        with get_db() as db:
            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                new_name = st.text_input("새 프로젝트 이름", value=project.name)
                new_status = st.selectbox("새 프로젝트 상태", ["진행 중", "완료", "보류"], index=["진행 중", "완료", "보류"].index(project.status))
                if st.button("수정 완료"):
                    with st.spinner("프로젝트 수정 중..."):
                        project.name = new_name
                        project.status = new_status
                        db.commit()
                        st.success(f"프로젝트 '{new_name}' 수정 완료")
                        time.sleep(1)
                        del st.session_state.edit_project
                        st.experimental_rerun()
            else:
                st.error("프로젝트를 찾을 수 없습니다.")
    except SQLAlchemyError as e:
        st.error(f"프로젝트 수정 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    project_management_screen()
