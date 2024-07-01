import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta, date
from typing import Dict, Any, List
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.metric_cards import style_metric_cards
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from io import BytesIO
import re
from streamlit_pills import pills

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
    .stPills span:nth-child(2) {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

def format_korean_currency(amount):
    if amount == "미정":
        return amount
    try:
        amount = int(amount)
        return '{:,}'.format(amount)
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
        is_undecided = pills("미정", ["예", "아니오"], ["#00B4D8", "#CAF0F8"])
    
    if is_undecided[0] == "예":
        st.session_state.data[key] = "미정"
    else:
        st.session_state.data[key] = parse_korean_currency(amount)

def main():
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'data' not in st.session_state:
        st.session_state.data = {}

    steps = ["기본 정보", "용역 개요", "용역 형태 및 장소", "용역 구성 요소", "마무리"]
    total_steps = len(steps)

    display_progress(st.session_state.step, total_steps)

    colored_header(
        label=f"Step {st.session_state.step}: {steps[st.session_state.step - 1]}",
        description="용역 기획을 위한 단계별 가이드",
        color_name="blue-70"
    )

    if st.session_state.step == 1:
        display_basic_info()
    elif st.session_state.step == 2:
        display_service_overview()
    elif st.session_state.step == 3:
        display_service_format_and_venue()
    elif st.session_state.step == 4:
        display_service_components()
    elif st.session_state.step == 5:
        finalize()

    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.step > 1:
            if st.button("이전", key="prev_button"):
                st.session_state.step -= 1
                st.experimental_rerun()
    with col2:
        if st.session_state.step < total_steps:
            if st.button("다음", key="next_button"):
                if validate_current_step():
                    st.session_state.step += 1
                    st.experimental_rerun()
                else:
                    st.error("모든 필수 항목을 채워주세요.")

    add_vertical_space(2)

def display_progress(current_step: int, total_steps: int):
    progress = (current_step / total_steps) * 100
    st.markdown(f"""
        <div class="progress-bar">
            <div class="progress" style="width: {progress}%;"></div>
        </div>
        <p style="text-align: center;">진행 상황: {current_step} / {total_steps}</p>
    """, unsafe_allow_html=True)

def improved_schedule_input():
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("용역 시작일", value=st.session_state.data.get('service_start_date', datetime.now().date()))
    
    if 'service_end_date' not in st.session_state.data or st.session_state.data['service_end_date'] < start_date:
        end_date = start_date
    else:
        end_date = st.session_state.data['service_end_date']
    
    with col2:
        end_date = st.date_input("용역 종료일", value=end_date, min_value=start_date)
    
    st.session_state.data['service_start_date'] = start_date
    st.session_state.data['service_end_date'] = end_date

    setup_options = ["전날부터", "당일"]
    teardown_options = ["당일 철수", "다음날 철수"]

    col3, col4 = st.columns(2)
    with col3:
        setup_choice = pills("셋업 시작", setup_options)
    with col4:
        teardown_choice = pills("철수", teardown_options)

    st.session_state.data['setup_choice'] = setup_choice[0] if setup_choice else setup_options[0]
    st.session_state.data['teardown_choice'] = teardown_choice[0] if teardown_choice else teardown_options[0]

    st.session_state.data['setup_date'] = start_date - timedelta(days=1) if st.session_state.data['setup_choice'] == "전날부터" else start_date
    st.session_state.data['teardown_date'] = end_date if st.session_state.data['teardown_choice'] == "당일 철수" else end_date + timedelta(days=1)

    st.write(f"셋업 일자: {st.session_state.data['setup_date']}")
    st.write(f"철수 일자: {st.session_state.data['teardown_date']}")

    service_duration = (end_date - start_date).days + 1
    st.session_state.data['service_duration'] = service_duration
    st.write(f"용역 기간: {service_duration}일")

def toggle_pill(label, key):
    if key not in st.session_state:
        st.session_state[key] = False
    
    if st.button(label, key=f"btn_{key}"):
        st.session_state[key] = not st.session_state[key]
    
    return st.session_state[key]

def multi_pills(label, options):
    st.write(label)
    selected = []
    cols = st.columns(3)  # 3열 레이아웃 사용
    for i, option in enumerate(options):
        with cols[i % 3]:
            key = f"{label}_{option}"
            if toggle_pill(option, key):
                selected.append(option)
    return selected

def display_basic_info():
    st.session_state.data['name'] = st.text_input("이름", st.session_state.data.get('name', ''))
    st.session_state.data['department'] = st.text_input("근무 부서", st.session_state.data.get('department', ''))
    
    position_options = ["파트너 기획자", "선임", "책임", "수석"]
    st.session_state.data['position'] = pills("직급", position_options)[0]
    
    service_types = ["행사 운영", "공간 디자인", "마케팅", "PR", "영상제작", "전시", "브랜딩", "온라인 플랫폼 구축", "기타"]
    st.session_state.data['service_types'] = multi_pills("주로 하는 용역 유형", service_types)
    
    st.session_state.data['service_name'] = st.text_input("용역명", st.session_state.data.get('service_name', ''))

    improved_schedule_input()
    
# CSS를 사용하여 버튼 스타일 지정
st.markdown("""
<style>
    .stButton > button {
        background-color: #CAF0F8;
        color: black;
        border: none;
        border-radius: 20px;
        padding: 5px 15px;
        margin: 5px;
    }
    .stButton > button:hover {
        background-color: #FF6B6B;
        color: white;
    }
    .stButton > button:focus {
        background-color: #FF6B6B;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


def display_service_overview():
    service_purposes = ["브랜드 인지도 향상", "고객 관계 강화", "신제품 출시", "교육 및 정보 제공", "수익 창출", "문화/예술 증진", "기타"]
    st.session_state.data['service_purpose'] = multi_pills("용역의 주요 목적", service_purposes)
    
    input_method = pills("예상 참가자 수 입력 방식", ["단일 값", "범위 설정"], ["#00B4D8", "#CAF0F8"])[0]
    
    if input_method == "단일 값":
        col1, col2 = st.columns(2)
        with col1:
            use_slider = pills("슬라이더 사용", ["예", "아니오"], ["#00B4D8", "#CAF0F8"])[0] == "예"
        with col2:
            participants_over_2000 = pills("2000명 이상", ["예", "아니오"], ["#00B4D8", "#CAF0F8"])[0] == "예"
        
        if participants_over_2000:
            st.session_state.data['expected_participants'] = "2000명 이상"
        else:
            if use_slider:
                current_value = st.session_state.data.get('expected_participants', 100)
                if isinstance(current_value, str):
                    try:
                        current_value = int(current_value)
                    except ValueError:
                        current_value = 100
                st.session_state.data['expected_participants'] = st.slider("예상 참가자 수", 0, 2000, value=int(current_value))
            else:
                current_value = st.session_state.data.get('expected_participants', '')
                if isinstance(current_value, int):
                    current_value = str(current_value)
                st.session_state.data['expected_participants'] = st.text_input("예상 참가자 수", value=current_value)
    else:
        col1, col2 = st.columns(2)
        with col1:
            min_participants = st.number_input("최소 예상 참가자 수", value=st.session_state.data.get('min_participants', 0), min_value=0)
        with col2:
            max_participants = st.number_input("최대 예상 참가자 수", value=st.session_state.data.get('max_participants', 100), min_value=min_participants)
        
        st.session_state.data['min_participants'] = min_participants
        st.session_state.data['max_participants'] = max_participants
        st.session_state.data['expected_participants'] = f"{min_participants} - {max_participants}"

    contract_types = ["수의계약", "입찰", "B2B"]
    st.session_state.data['contract_type'] = pills("계약 형태", contract_types)[0]
    
    budget_statuses = [CONFIRMED, ALMOST_CONFIRMED, IN_PROGRESS, NOT_STARTED]
    st.session_state.data['budget_status'] = pills("예산 협의 상태", budget_statuses)[0]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="예상 참가자 수", value=st.session_state.data['expected_participants'])
    with col2:
        st.metric(label="계약 형태", value=st.session_state.data['contract_type'])
    with col3:
        st.metric(label="예산 협의 상태", value=st.session_state.data['budget_status'])
    
    style_metric_cards()

def display_service_format_and_venue():
    service_formats = ["오프라인", "온라인", "하이브리드", "기타"]
    st.session_state.data['service_format'] = pills("용역 형태", service_formats)[0]
    
    if st.session_state.data['service_format'] in ["오프라인", "하이브리드"]:
        venue_types = ["실내 (호텔, 컨벤션 센터 등)", "야외 (공원, 광장 등)", "혼합형 (실내+야외)", "아직 미정"]
        st.session_state.data['venue_type'] = pills("용역 장소 유형", venue_types)[0]
        
        venue_statuses = [CONFIRMED, ALMOST_CONFIRMED, IN_PROGRESS, NOT_STARTED]
        st.session_state.data['venue_status'] = pills("용역 장소 협의 상태", venue_statuses)[0]
        
        if st.session_state.data['venue_status'] in [CONFIRMED, ALMOST_CONFIRMED]:
            st.session_state.data['specific_venue'] = st.text_input("구체적인 장소", st.session_state.data.get('specific_venue', ''))
        else:
            st.session_state.data['expected_area'] = st.text_input("예정 지역", st.session_state.data.get('expected_area', ''))

def display_service_components():
    st.header("용역 구성 요소")
    
    # JSON 파일에서 카테고리 데이터 불러오기
    with open('categories.json', 'r', encoding='utf-8') as f:
        components = json.load(f)
    
    for category, subcategories in components.items():
        with st.expander(f"{category}"):
            st.write(f"## {category}")
            
            # 대분류 선택
            category_selected = pills(f"{category} 선택", ["선택", "미선택"], ["#00B4D8", "#CAF0F8"])
            if "선택" in category_selected:
                st.session_state.data[category] = {"needed": True}
            else:
                st.session_state.data[category] = {"needed": False}
            
            if st.session_state.data[category]["needed"]:
                # 중분류 선택
                for subcategory, items in subcategories.items():
                    subcategory_selected = pills(f"{subcategory} 선택", ["선택", "미선택"], ["#00B4D8", "#CAF0F8"])
                    if "선택" in subcategory_selected:
                        st.session_state.data[category][subcategory] = {"needed": True}
                    else:
                        st.session_state.data[category][subcategory] = {"needed": False}
                    
                    if st.session_state.data[category][subcategory]["needed"]:
                        # 소분류 선택 (다중 선택)
                        selected_items = multi_pills("항목 선택", items)
                        for item in items:
                            st.session_state.data[category][subcategory][item] = item in selected_items

                # 견적 입력
                budget_input(f"{category}_budget", f"{category} 예산")
                
                # 업체 선정 이유
                reasons = ["클라이언트의 요청", "제안단계에서 먼저 도움을 줌", "퀄리티가 보장되고, 아는 업체", "동일 과업 경험"]
                selected_reason = pills(f"{category} 업체 선정 이유", reasons)
                if selected_reason:
                    st.session_state.data[category]["업체_선정_이유"] = selected_reason[0]
                else:
                    st.session_state.data[category]["업체_선정_이유"] = None

def validate_current_step() -> bool:
    step = st.session_state.step
    data = st.session_state.data

    if step == 1:
        required_fields = ['name', 'department', 'position', 'service_types', 'service_name', 'service_start_date', 'service_end_date']
    elif step == 2:
        required_fields = ['service_purpose', 'expected_participants', 'contract_type', 'budget_status']
    elif step == 3:
        required_fields = ['service_format']
        if data['service_format'] in ["오프라인", "하이브리드"]:
            required_fields.extend(['venue_type', 'venue_status'])
    elif step == 4:
        # 여기서는 모든 필드가 옵션이므로 항상 True를 반환
        return True
    else:
        return True

    for field in required_fields:
        if field not in data or not data[field]:
            return False
    return True

def generate_excel_file(data: Dict[str, Any], category: str) -> BytesIO:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"{category} 발주요청서"

    # 스타일 정의
    header_font = Font(name='맑은 고딕', size=12, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

    # 헤더 작성
    headers = ['항목', '내용']
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = border

    # 공통 정보 작성
    common_info = [
        ('이름', data['name']),
        ('근무 부서', data['department']),
        ('직급', data['position']),
        ('주로 하는 용역 유형', ', '.join(data['service_types'])),
        ('용역명', data['service_name']),
        ('용역 시작일', data['service_start_date']),
        ('용역 마감일', data['service_end_date']),
        ('진행 일정 (일 수)', data['service_duration']),
        ('셋업 시작일', data['setup_date']),
        ('철수 마감일', data['teardown_date']),
        ('용역 목적', ', '.join(data['service_purpose'])),
        ('예상 참가자 수', data['expected_participants']),
        ('계약 형태', data['contract_type']),
        ('예산 협의 상태', data['budget_status']),
        ('용역 형태', data['service_format']),
        ('용역 장소 유형', data.get('venue_type', 'N/A')),
        ('용역 장소', data.get('specific_venue', data.get('expected_area', 'N/A')))
    ]

    for row, (item, content) in enumerate(common_info, start=2):
        ws.cell(row=row, column=1, value=item).border = border
        ws.cell(row=row, column=2, value=content).border = border

    # 카테고리별 정보 작성
    if category in data:
        ws.append(['', ''])  # 빈 행 추가
        ws.append([f'{category} 세부 정보', ''])
        for item, content in data[category].items():
            ws.append([item, str(content)])
            ws.cell(row=ws.max_row, column=1).border = border
            ws.cell(row=ws.max_row, column=2).border = border

    # 예산 정보 추가
    budget_key = f"{category}_budget"
    if budget_key in data:
        ws.append(['', ''])
        ws.append(['배정 예산', format_korean_currency(data[budget_key])])
        ws.cell(row=ws.max_row, column=1).border = border
        ws.cell(row=ws.max_row, column=2).border = border

    # 열 너비 조정
    for column_cells in ws.columns:
        length = max(len(str(cell.value)) for cell in column_cells)
        ws.column_dimensions[get_column_letter(column_cells[0].column)].width = min(length + 2, 50)

    # 메모리에 엑셀 파일 저장
    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)

    return excel_file

def save_survey_data(data: Dict[str, Any]) -> bool:
    try:
        # 저장 디렉토리 생성
        save_dir = "survey_results"
        os.makedirs(save_dir, exist_ok=True)
        
        # 파일명 생성 (이름_날짜_시간.json)
        filename = f"{data['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(save_dir, filename)
        
        # 데이터 전처리
        processed_data = data.copy()
        for key, value in processed_data.items():
            if isinstance(value, (datetime, date)):
                processed_data[key] = value.isoformat()
        
        # JSON 파일로 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=4)
        
        return True
    except Exception as e:
        st.error(f"데이터 저장 중 오류 발생: {str(e)}")
        return False

def finalize():
    st.header("설문 완료")
    st.write("수고하셨습니다! 모든 단계를 완료하셨습니다.")
    
    if st.button("설문 저장 및 발주요청서 다운로드"):
        # 총 예산 계산
        total_budget = 0
        for category in ["무대 설치", "음향 시스템", "조명 장비", "LED 스크린", "동시통역 시스템", "케이터링 서비스", "영상 제작", "마케팅 및 홍보", "PR", "브랜딩", "온라인 플랫폼"]:
            budget_key = f"{category}_budget"
            if budget_key in st.session_state.data:
                budget = st.session_state.data[budget_key]
                if isinstance(budget, (int, float)):
                    total_budget += budget

        st.write(f"총 예산: {format_korean_currency(total_budget)}원")

        # 설문 데이터 저장
        save_result = save_survey_data(st.session_state.data)
        if save_result:
            st.success("설문이 성공적으로 저장되었습니다.")
        else:
            st.error("설문 저장 중 오류가 발생했습니다.")
        
        # 발주요청서 생성 및 다운로드
        categories = ["무대 설치", "음향 시스템", "조명 장비", "LED 스크린", "동시통역 시스템", "케이터링 서비스", "영상 제작", "마케팅 및 홍보", "PR", "브랜딩", "온라인 플랫폼"]
        for category in categories:
            if category in st.session_state.data and st.session_state.data[category].get('needed', False):
                excel_file = generate_excel_file(st.session_state.data, category)
                st.download_button(
                    label=f"{category} 발주요청서 다운로드",
                    data=excel_file,
                    file_name=f"{category}_발주요청서_{st.session_state.data['name']}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        st.success("발주요청서가 생성되었습니다. 위의 버튼을 클릭하여 각 카테고리별 발주요청서를 다운로드 하세요.")

if __name__ == "__main__":
    main()