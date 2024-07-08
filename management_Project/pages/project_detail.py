import streamlit as st
from utils.database import get_db, Project
from sqlalchemy.orm import Session

def project_detail_screen():
    st.title("프로젝트 상세 정보")
    
    project_id = st.text_input("프로젝트 ID", placeholder="프로젝트 ID를 입력하세요")
    
    if st.button("조회"):
        db = next(get_db())
        project = db.query(Project).filter(Project.id == project_id).first()
        
        if project:
            st.write(f"프로젝트 이름: {project.name}")
            st.write(f"프로젝트 상태: {project.status}")
            
            # 팀 멤버 리스트
            st.write("팀 멤버 리스트")
            # 예제 데이터 (실제로는 DB에서 조회)
            team_members = [{"name": "멤버 1", "role": "개발자"}, {"name": "멤버 2", "role": "디자이너"}]
            st.table(team_members)
            
            # 산출내역서 리스트
            st.write("산출내역서 리스트")
            # 예제 데이터 (실제로는 DB에서 조회)
            outputs = [{"item": "산출내역서 1", "amount": 100000}, {"item": "산출내역서 2", "amount": 200000}]
            st.table(outputs)
            
            # 프로젝트 상태 업데이트
            new_status = st.selectbox("프로젝트 상태 업데이트", ["진행 중", "완료", "보류"])
            if st.button("상태 업데이트"):
                project.status = new_status
                db.commit()
                st.success(f"프로젝트 상태가 '{new_status}'로 업데이트 되었습니다.")
            
            # 팀 멤버 추가 및 제거
            new_member = st.text_input("새 팀 멤버 추가", placeholder="팀 멤버 이름을 입력하세요")
            if st.button("멤버 추가"):
                if new_member:
                    # 실제 DB 연동 로직 구현 필요
                    st.success(f"팀 멤버 '{new_member}'가 추가되었습니다.")
                else:
                    st.error("팀 멤버 이름을 입력해주세요.")
            remove_member = st.text_input("팀 멤버 제거", placeholder="팀 멤버 이름을 입력하세요")
            if st.button("멤버 제거"):
                if remove_member:
                    # 실제 DB 연동 로직 구현 필요
                    st.success(f"팀 멤버 '{remove_member}'가 제거되었습니다.")
                else:
                    st.error("제거할 팀 멤버 이름을 입력해주세요.")
        else:
            st.error("프로젝트를 찾을 수 없습니다.")

if __name__ == "__main__":
    project_detail_screen()
