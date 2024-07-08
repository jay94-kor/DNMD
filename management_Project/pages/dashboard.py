import streamlit as st
from utils.database import get_db, Project, User
import pandas as pd

def dashboard_screen():
    st.title("대시보드")
    
    with get_db() as db:
        # 전체 예산 상태
        st.header("전체 예산 상태")
        projects = db.query(Project).all()
        total_budget = sum(project.budget for project in projects)
        total_revenue = sum(project.revenue for project in projects)
        total_expenses = sum(project.expenses for project in projects)
        total_requested = sum(project.requested_amount for project in projects)
        
        budget_data = pd.DataFrame({
            "항목": ["배정 금액", "매출액", "사용액", "사용 요청액"],
            "금액": [total_budget, total_revenue, total_expenses, total_requested]
        })
        st.bar_chart(budget_data.set_index("항목"))
        
        # 프로젝트별 순이익률
        st.header("프로젝트별 순이익률")
        project_profit_rates = {project.name: (project.revenue - project.expenses) / project.revenue 
                                for project in projects if project.revenue > 0}
        st.line_chart(project_profit_rates)
        
        # 사용자별 담당 프로젝트
        st.header("사용자별 담당 프로젝트")
        users = db.query(User).all()
        user_projects = []
        for user in users:
            user_projects.append({
                "사용자": user.name,
                "프로젝트": ", ".join([project.name for project in user.projects]),
                "평균 수익률": sum(project_profit_rates.get(project.name, 0) for project in user.projects) / len(user.projects) if user.projects else 0
            })
        st.table(pd.DataFrame(user_projects))

if __name__ == "__main__":
    dashboard_screen()
