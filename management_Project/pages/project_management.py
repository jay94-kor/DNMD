import streamlit as st
from utils.database import get_db, Project
from sqlalchemy.orm import Session

def project_management_screen():
    st.title("프로젝트 관리")
    
    st.header("새로운 프로젝트 생성")
    project_name = st.text_input("프로젝트 이름", placeholder="프로젝트 이름을 입력하세요")
    project_status = st.selectbox("프로젝트 상태", ["진행 중", "완료", "보류"])
    if st.button("프로젝트 생성"):
        db = next(get_db())
        new_project = Project(name=project_name, status=project_status)
        db.add(new_project)
        db.commit()
        st.success(f"프로젝트 '{project_name}' 생성 완료")
    
    st.header("기존 프로젝트")
    db = next(get_db())
    projects = db.query(Project).all()
    for project in projects:
        st.write(f"프로젝트 이름: {project.name}, 상태: {project.status}")
        st.button("수정", key=f"edit_{project.id}")
        st.button("삭제", key=f"delete_{project.id}")

if __name__ == "__main__":
    project_management_screen()
