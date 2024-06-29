import streamlit as st
from datetime import time, date
import pandas as pd
from io import StringIO

# CSS 스타일 추가
st.markdown("""
    <style>
    .block-container { padding: 1rem; }
    .stButton button { width: 100%; height: 3rem; margin: 0.2rem; white-space: nowrap; }
    .small-text { font-size: 0.8rem; color: gray; }
    .fixed-header {
        position: fixed; top: 0; right: 0; width: 200px;
        background-color: white; z-index: 100;
        padding: 10px; border: 1px solid #ddd;
    }
    </style>
    """, unsafe_allow_html=True)

# 숫자 형식 설정 함수
def format_number(number):
    return "{:,}원".format(number)

# 예산 합계를 계산하여 표시하는 함수
def update_total_budget():
    if 'selected_options' in st.session_state:
        st.session_state.total_budget = sum(st.session_state.get(f"예산_{option}", 0) for option in st.session_state['selected_options'] if st.session_state.get(f"예산_{option}", 0) != "미정")

# 기본 정보 섹션
def basic_info_section():
    st.header("기본 정보")
    용역명 = st.text_input("용역명이 무엇인가요?", value="")
    용역목적 = st.text_input("용역의 목적이 무엇인가요?", value="")
    목표인원 = st.number_input("목표인원은 몇 명인가요?", min_value=0, value=0)
    용역담당자 = st.text_input("용역 담당자의 이름을 적어주세요.", value="")
    return 용역명, 용역목적, 목표인원, 용역담당자

# 필수 정보 섹션
def essential_info_section():
    st.header("예산 관리")
    부가세_포함 = st.radio("부가세 포함 여부를 선택해주세요.", ("포함", "별도"))
    return 부가세_포함

# 일정 계획 섹션
def schedule_section():
    st.header("일정 계획")
    일정_미정 = st.checkbox("일정이 미정인가요?")
    if 일정_미정:
        준비일정 = st.date_input("행사 시작일을 선택해주세요. (예상)", date.today())
        종료일정 = st.date_input("행사 종료일을 선택해주세요. (예상)", date.today())
        셋업시간 = st.time_input("셋업 시간 (예상)", time(9, 0))
        시작시간 = st.time_input("시작 시간 (예상)", time(10, 0))
        마감시간 = st.time_input("마감 시간 (예상)", time(18, 0))
    else:
        준비일정 = st.date_input("행사 시작일을 선택해주세요.", date.today())
        종료일정 = st.date_input("행사 종료일을 선택해주세요.", date.today())
        셋업시간 = st.time_input("셋업 시간", time(9, 0))
        시작시간 = st.time_input("시작 시간", time(10, 0))
        마감시간 = st.time_input("마감 시간", time(18, 0))
    return 준비일정, 종료일정, 셋업시간, 시작시간, 마감시간

# 장소 선정 섹션
def venue_section():
    st.header("장소 선정")
    장소 = st.text_input("정해져있다면 행사의 장소를 알려주세요. (없음으로 기재 가능)", value="")
    장소특이사항 = st.text_area("행사 장소의 특이사항이 있나요?", value="")
    return 장소, 장소특이사항

# 세부 사항 입력 섹션
def input_section(title):
    st.header(title)
    상세기획정도 = st.radio(f"{title}에 대한 상세 기획 정도를 선택해주세요.", ("정해졌다", "거의 정해졌다", "정하는 중이다", "정해지지 않았다", "전혀 정해지지 않았다"))
    if 상세기획정도 == "정해지지 않았다":
        예산 = st.radio(f"{title}에 배정된 예산을 선택해주세요.", ("미정", "예산 입력"), key=f"예산선택_{title}")
        if 예산 == "예산 입력":
            예산 = st.number_input(f"{title}에 배정된 예산을 입력해주세요.", min_value=0, value=0, step=1000, format="%d", key=f"예산_{title}")
    else:
        예산 = st.number_input(f"{title}에 배정된 예산을 입력해주세요.", min_value=0, value=0, step=1000, format="%d", key=f"예산_{title}")
    if 상세기획정도 in ["정해졌다", "거의 정해졌다", "정하는 중이다"]:
        st.text_area(f"{title}에 대한 세부 사항을 입력해주세요.")
    else:
        st.markdown(f'<p class="small-text">현재의 기획 정도에 따른 예상 답변: {title} 관련 정보</p>', unsafe_allow_html=True)
    return 예산

# 기본 정보 입력
용역명, 용역목적, 목표인원, 용역담당자 = basic_info_section()

# 필수 정보 입력
부가세_포함 = essential_info_section()

# 초기화
if 'selected_options' not in st.session_state:
    st.session_state['selected_options'] = []

# 필요한 요소 선택 섹션
st.header("필요한 요소 선택")
options = ["홍보 전략", "파트너십 및 후원", "티켓 판매", "인력 섭외", "행사 진행", "평가 및 피드백", "영상 및 미디어", "특수 효과", "장비 대여", "VR/AR 기술", "전시 부스", "디자인", "콘텐츠 제작", "인플루언서", "행사 관리", "공연 및 행사", "체험 프로그램", "전시 및 홍보", "시설 관리", "안전 관리", "교통 및 주차", "청소 및 위생"]

cols = st.columns(5)
for i, option in enumerate(options):
    if cols[i % 5].button(option):
        if option not in st.session_state['selected_options']:
            st.session_state['selected_options'].append(option)

# 기타 항목 추가 기능
if st.checkbox("기타 항목 추가"):
    new_option = st.text_input("추가할 항목을 입력하세요:")
    if st.button("추가"):
        if new_option and new_option not in st.session_state['selected_options']:
            st.session_state['selected_options'].append(new_option)

# 선택된 옵션에 대해 예산 합계 업데이트 및 입력
예산_항목들 = {}
for option in st.session_state['selected_options']:
    예산_항목들[option] = input_section(option)

# 예산 합계 업데이트
if 'total_budget' not in st.session_state:
    st.session_state.total_budget = 0
update_total_budget()
st.markdown(f'<div class="fixed-header">현재까지 입력된 예산 총합: {format_number(st.session_state.total_budget)}</div>', unsafe_allow_html=True)

# 일정 계획 입력
준비일정, 종료일정, 셋업시간, 시작시간, 마감시간 = schedule_section()

# 장소 선정 입력
장소, 장소특이사항 = venue_section()

# 데이터 저장 및 다운로드
def save_data(data):
    output = StringIO()
    for key, value in data.items():
        df = pd.DataFrame.from_dict(value, orient='index', columns=['내용'])
        df.to_csv(output, encoding='utf-8-sig')
    return output.getvalue()

data = {
    "기본정보": {
        "용역명": 용역명,
        "용역목적": 용역목적,
        "목표인원": 목표인원,
        "용역담당자": 용역담당자,
    },
    "필수정보": {
        "부가세_포함": 부가세_포함,
        "준비일정": 준비일정,
        "종료일정": 종료일정,
        "셋업시간": 셋업시간,
        "시작시간": 시작시간,
        "마감시간": 마감시간,
        "장소": 장소,
        "장소특이사항": 장소특이사항,
    },
}

for option in st.session_state['selected_options']:
    data[option] = {
        "예산": format_number(예산_항목들[option]) if 예산_항목들[option] != "미정" else "미정",
        "상세기획정도": st.session_state.get(f"상세기획정도_{option}", ""),
        "세부사항": st.session_state.get(f"세부사항_{option}", "")
    }

csv_data = save_data(data)

if st.button("제출"):
    st.write("설문이 제출되었습니다. 감사합니다!")
    st.download_button(label="발주요청서 다운로드", data=csv_data, file_name=f"{용역담당자}_{용역명}.csv", mime="text/csv")
