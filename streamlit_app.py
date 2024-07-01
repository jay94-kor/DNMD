import streamlit as st
import json
import os
from datetime import datetime, timedelta, date
from typing import Dict, Any, List
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from io import BytesIO

# 상수 정의
CONFIRMED = "확정됨"
ALMOST_CONFIRMED = "거의 확정됨"
IN_PROGRESS = "진행 중"
NOT_STARTED = "아직 시작 못함"

# 페이지 구성 설정
st.set_page_config(layout="wide", page_title="이벤트 기획 도구")

# CSS 스타일 적용
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
        font-family: 'Arial', sans-serif;
    }
    .progress-bar {
        width: 100%;
        background-color: #f0f0f0;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .progress {
        width: 0%;
        height: 20px;
        background-color: #4CAF50;
        border-radius: 5px;
        transition: width 0.5s ease-in-out;
    }
    .step-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .stButton>button {
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

def format_korean_currency(amount):
    if amount == "미정":
        return amount
    try:
        return '{:,}'.format(int(amount))
    except ValueError:
        return amount

def parse_korean_currency(amount):
    if amount == "미정":
        return amount
    try:
        return int(amount.replace(',', ''))
    except ValueError:
        return amount

def budget_input(key, label):
    col1, col2 = st.columns([3, 1])
    with col1:
        amount = st.text_input(label, value=format_korean_currency(st.session_state.data.get(key, '')))
    with col2:
        is_undecided = st.radio("미정", ["예", "아니오"], key=f"radio_{key}")
    
    st.session_state.data[key] = "미정" if is_undecided == "예" else parse_korean_currency(amount)

def multi_select_with_other(label, options):
    st.write(label)
    selections = []
    cols = st.columns(3)
    for i, option in enumerate(options):
        with cols[i % 3]:
            if option != "기타":
                if st.checkbox(option, key=f"checkbox_{label}_{option}"):
                    selections.append(option)
            else:
                if st.checkbox("기타", key=f"checkbox_{label}_other"):
                    other_text = st.text_input("기타 (직접 입력)", key=f"text_{label}_other")
                    if other_text:
                        selections.append(f"기타: {other_text}")
    return selections

def improved_schedule_input():
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("용역 시작일", value=st.session_state.data.get('service_start_date', datetime.now().date()))
    with col2:
        end_date = st.date_input("용역 종료일", value=st.session_state.data.get('service_end_date', start_date), min_value=start_date)
    
    st.session_state.data['service_start_date'] = start_date
    st.session_state.data['service_end_date'] = end_date

    col3, col4 = st.columns(2)
    with col3:
        setup_choice = st.radio("셋업 시작", ["전날부터", "당일"])
    with col4:
        teardown_choice = st.radio("철수", ["당일 철수", "다음날 철수"])

    st.session_state.data['setup_choice'] = setup_choice
    st.session_state.data['teardown_choice'] = teardown_choice

    st.session_state.data['setup_date'] = start_date - timedelta(days=1) if setup_choice == "전날부터" else start_date
    st.session_state.data['teardown_date'] = end_date if teardown_choice == "당일 철수" else end_date + timedelta(days=1)

    st.write(f"셋업 일자: {st.session_state.data['setup_date']}")
    st.write(f"철수 일자: {st.session_state.data['teardown_date']}")

    st.write("전체 일정:")
    st.write(f"셋업: {st.session_state.data['setup_date']}")
    st.write(f"행사: {start_date} ~ {end_date}")
    st.write(f"철수: {st.session_state.data['teardown_date']}")

def display_basic_info():
    st.header("기본 정보")
    st.session_state.data['event_name'] = st.text_input("행사명", value=st.session_state.data.get('event_name', ''))
    st.session_state.data['client_name'] = st.text_input("클라이언트명", value=st.session_state.data.get('client_name', ''))
    st.session_state.data['event_type'] = st.selectbox("행사 유형", ["컨퍼런스", "전시회", "콘서트", "기업 행사", "기타"], index=["컨퍼런스", "전시회", "콘서트", "기업 행사", "기타"].index(st.session_state.data.get('event_type', '컨퍼런스')))
    st.session_state.data['event_scale'] = st.selectbox("행사 규모", ["소규모 (100명 이하)", "중규모 (100-500명)", "대규모 (500명 이상)"], index=["소규모 (100명 이하)", "중규모 (100-500명)", "대규모 (500명 이상)"].index(st.session_state.data.get('event_scale', '중규모 (100-500명)')))
    improved_schedule_input()

def display_venue_info():
    st.header("장소 정보")
    st.session_state.data['venue_name'] = st.text_input("장소명", value=st.session_state.data.get('venue_name', ''))
    st.session_state.data['venue_address'] = st.text_input("주소", value=st.session_state.data.get('venue_address', ''))
    st.session_state.data['venue_capacity'] = st.number_input("수용 인원", min_value=0, value=st.session_state.data.get('venue_capacity', 0))
    st.session_state.data['venue_facilities'] = multi_select_with_other("시설 및 장비", ["무대", "음향 시스템", "조명 시스템", "프로젝터", "스크린", "Wi-Fi", "주차장", "기타"])

def display_budget_info():
    st.header("예산 정보")
    budget_input("total_budget", "총 예산")
    budget_input("venue_budget", "장소 대여 예산")
    budget_input("equipment_budget", "장비 대여 예산")
    budget_input("catering_budget", "케이터링 예산")
    budget_input("marketing_budget", "마케팅 예산")
    budget_input("staff_budget", "인력 예산")
    budget_input("misc_budget", "기타 예산")

def display_service_components():
    st.header("용역 구성 요소")
    
    with open('categories.json', 'r', encoding='utf-8') as f:
        components = json.load(f)
    
    for category, subcategories in components.items():
        with st.expander(f"{category}"):
            st.write(f"## {category}")
            
            category_selected = st.radio(f"{category} 선택", ["선택", "미선택"], key=f"radio_{category}")
            st.session_state.data[category] = {"needed": category_selected == "선택"}
            
            if st.session_state.data[category]["needed"]:
                for subcategory, items in subcategories.items():
                    subcategory_selected = st.radio(f"{subcategory} 선택", ["선택", "미선택"], key=f"radio_{category}_{subcategory}")
                    st.session_state.data[category][subcategory] = {"needed": subcategory_selected == "선택"}
                    
                    if st.session_state.data[category][subcategory]["needed"]:
                        selected_items = st.multiselect("항목 선택", items, key=f"multiselect_{category}_{subcategory}", default=[])
                        for item in items:
                            st.session_state.data[category][subcategory][item] = item in selected_items

                budget_input(f"{category}_budget", f"{category} 예산")
                
                reasons = ["클라이언트의 요청", "제안단계에서 먼저 도움을 줌", "퀄리티가 보장되고, 아는 업체", "동일 과업 경험"]
                st.session_state.data[category]["업체_선정_이유"] = st.selectbox(f"{category} 업체 선정 이유", reasons, key=f"select_{category}_reason")

def display_progress():
    st.header("진행 상황")
    progress_options = [NOT_STARTED, IN_PROGRESS, ALMOST_CONFIRMED, CONFIRMED]
    
    for category in ["장소 섭외", "장비 대여", "케이터링", "인력 채용", "마케팅 및 홍보"]:
        st.session_state.data[f"{category}_progress"] = st.selectbox(
            f"{category} 진행 상황",
            progress_options,
            index=progress_options.index=progress_options.index(st.session_state.data.get(f"{category}_progress", NOT_STARTED))
        )

def save_survey_data(data: Dict[str, Any]) -> bool:
    try:
        with open('survey_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        st.error(f"데이터 저장 중 오류 발생: {e}")
        return False

def load_survey_data() -> Dict[str, Any]:
    try:
        with open('survey_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        st.error("저장된 데이터를 불러오는 중 오류가 발생했습니다. 새로운 설문을 시작합니다.")
        return {}

def create_excel_report(data: Dict[str, Any]) -> BytesIO:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "이벤트 기획 보고서"

    # 스타일 정의
    title_font = Font(name='맑은 고딕', size=14, bold=True)
    header_font = Font(name='맑은 고딕', size=11, bold=True)
    data_font = Font(name='맑은 고딕', size=11)
    
    title_fill = PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid")
    header_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    
    border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

    # 제목 행
    ws.merge_cells('A1:D1')
    ws['A1'] = "이벤트 기획 보고서"
    ws['A1'].font = title_font
    ws['A1'].fill = title_fill
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')

    # 데이터 입력 및 스타일 적용
    row = 3
    for section, content in data.items():
        ws.merge_cells(f'A{row}:D{row}')
        ws[f'A{row}'] = section.upper()
        ws[f'A{row}'].font = header_font
        ws[f'A{row}'].fill = header_fill
        for cell in ws[row]:
            cell.border = border
        row += 1

        if isinstance(content, dict):
            for key, value in content.items():
                ws[f'B{row}'] = key
                ws[f'C{row}'] = str(value)
                for cell in ws[row]:
                    cell.font = data_font
                    cell.border = border
                row += 1
        else:
            ws[f'B{row}'] = str(content)
            for cell in ws[row]:
                cell.font = data_font
                cell.border = border
            row += 1
        
        row += 1  # 섹션 간 빈 행 추가

    # 열 너비 조정
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    # 엑셀 파일을 메모리에 저장
    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
    
    return excel_file

def main():
    if 'step' not in st.session_state:
        st.session_state.step = 1
    
    if 'data' not in st.session_state:
        st.session_state.data = load_survey_data()

    st.title("이벤트 기획 도구")

    # 진행 상황 표시
    progress_percentage = (st.session_state.step - 1) * 20
    st.markdown(f"""
        <div class="progress-bar">
            <div class="progress" style="width: {progress_percentage}%;"></div>
        </div>
    """, unsafe_allow_html=True)

    step_titles = [
        "기본 정보",
        "장소 정보",
        "예산 정보",
        "용역 구성 요소",
        "진행 상황"
    ]

    st.markdown(f'<p class="step-title">Step {st.session_state.step}: {step_titles[st.session_state.step - 1]}</p>', unsafe_allow_html=True)

    step_functions = [
        display_basic_info,
        display_venue_info,
        display_budget_info,
        display_service_components,
        display_progress
    ]

    step_functions[st.session_state.step - 1]()

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.session_state.step > 1:
            if st.button("이전"):
                st.session_state.step -= 1
        st.experimental_rerun()

    with col3:
        if st.session_state.step < 5:
            if st.button("다음"):
                st.session_state.step += 1
                st.experimental_rerun()
        else:
            if st.button("제출"):
                if save_survey_data(st.session_state.data):
                    st.success("설문이 성공적으로 저장되었습니다.")
                    
                    # 엑셀 보고서 생성
                    excel_file = create_excel_report(st.session_state.data)
                    
                    # 다운로드 버튼 생성
                    st.download_button(
                        label="엑셀 보고서 다운로드",
                        data=excel_file,
                        file_name="이벤트_기획_보고서.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.error("설문 저장 중 오류가 발생했습니다.")

    with col2:
        if st.button("임시 저장"):
            if save_survey_data(st.session_state.data):
                st.success("데이터가 임시 저장되었습니다.")
            else:
                st.error("임시 저장 중 오류가 발생했습니다.")

if __name__ == "__main__":
    main()