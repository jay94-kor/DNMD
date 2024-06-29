import streamlit as st
from datetime import time, date
import pandas as pd
import csv
from io import StringIO

# CSS 스타일 추가
st.markdown(
    """
    <style>
    .block-container {
        padding: 1rem;
    }
    .stButton button {
        width: 100%;
        height: 3rem;
        margin: 0.2rem;
        white-space: nowrap;
    }
    .small-text {
        font-size: 0.8rem;
        color: gray;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 숫자 형식 설정 함수
def format_number(number):
    return "{:,}원".format(number)

# 기본 정보 섹션
st.title("행사 요구사항 설문지")

st.header("기본 정보")
용역명 = st.text_input("용역명이 무엇인가요?", value="")
용역목적 = st.text_input("용역의 목적이 무엇인가요?", value="")
목표인원 = st.number_input("목표인원은 몇 명인가요?", min_value=0, value=0)
용역담당자 = st.text_input("용역 담당자의 이름을 적어주세요.", value="")

# 필수 섹션
st.header("예산 관리")
총예산 = st.number_input("용역의 예산은 얼마인가요?", min_value=0, value=0, step=1000, format="%d")
부가세_포함 = st.radio("부가세 포함 여부를 선택해주세요.", ("포함", "별도"))

# 예산 형식 설정
if 부가세_포함 == "포함":
    부가세 = 총예산 / 1.1 * 0.1
    원금 = 총예산 / 1.1
    총액 = 총예산
else:
    부가세 = 총예산 * 0.1
    원금 = 총예산
    총액 = 총예산 * 1.1

st.write(f"부가세: {format_number(int(부가세))}, 원금: {format_number(int(원금))}, 총액: {format_number(int(총액))}")

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

st.header("장소 선정")
장소 = st.text_input("정해져있다면 행사의 장소를 알려주세요. (없음으로 기재 가능)", value="")
장소특이사항 = st.text_area("행사 장소의 특이사항이 있나요?", value="")

# 필요한 요소 선택 섹션
st.header("필요한 요소 선택")

options = [
    "홍보 전략", "파트너십 및 후원", "티켓 판매", "인력 섭외", "행사 진행", 
    "평가 및 피드백", "영상 및 미디어", "특수 효과", "장비 대여", 
    "VR/AR 기술", "전시 부스", "디자인", "콘텐츠 제작", "인플루언서", 
    "행사 관리", "공연 및 행사", "체험 프로그램", "전시 및 홍보", 
    "시설 관리", "안전 관리", "교통 및 주차", "청소 및 위생"
]

selected_options = st.session_state.get('selected_options', [])

cols = st.columns(5)
for i, option in enumerate(options):
    if cols[i % 5].button(option):
        if option not in selected_options:
            selected_options.append(option)
            st.session_state['selected_options'] = selected_options

# 기타 항목 추가 기능
if st.checkbox("기타 항목 추가"):
    new_option = st.text_input("추가할 항목을 입력하세요:")
    if st.button("추가"):
        if new_option and new_option not in selected_options:
            selected_options.append(new_option)
            st.session_state['selected_options'] = selected_options

# 세부 사항 입력 섹션
def input_section(title, options):
    st.header(title)
    for option in options:
        if option in selected_options:
            상세기획정도 = st.radio(f"{option}에 대한 상세 기획 정도를 선택해주세요.", ("매우 그렇다", "그렇다", "보통이다", "모른다", "전혀 모른다"))
            if 상세기획정도 in ["매우 그렇다", "그렇다", "보통이다"]:
                st.text_area(f"{option}에 대한 세부 사항을 입력해주세요.")
            else:
                st.markdown(f'<p class="small-text">예상 답변: {option} 관련 정보</p>', unsafe_allow_html=True)

# 무대에 대한 세부 사항 입력 섹션
if "공연 및 행사" in selected_options:
    st.header("공연 및 행사")
    음악공연 = st.text_area("어떤 종류의 음악 공연을 계획하고 있나요?")
    댄스공연 = st.text_area("어떤 종류의 댄스 공연을 계획하고 있나요?")
    특별행사 = st.text_area("어떤 특별 행사를 계획하고 있나요?")
    
    무대_악기 = st.text_area("무대에 필요한 악기가 있나요?")
    무대_인원 = st.number_input("최대 몇 명이 무대에 오를 예정인가요?", min_value=0, value=5)
    LED_설치 = st.checkbox("LED 설치가 필요한가요?")
    
    if LED_설치:
        LED_제작 = st.text_area("LED 제작 여부와 관련된 구체적인 요구사항이 있나요?")
    
    제작_필요 = st.checkbox("제작이 필요한 항목이 있나요? (조형물, 모형물, 무대 데코레이션 등)")
    
    if 제작_필요:
        제작_항목 = st.multiselect("어떤 제작 항목이 필요한가요?", ["조형물", "모형물", "무대 데코레이션"])
        제작_디테일_필요 = st.checkbox("디테일한 사항이 정해졌나요?")
        
        if 제작_디테일_필요:
            제작_디테일 = st.text_area("구체적인 디테일을 입력해주세요.")

if "조명" in selected_options:
    st.header("조명")
    상세기획정도 = st.radio("조명에 대한 상세 기획 정도를 선택해주세요.", ("매우 그렇다", "그렇다", "보통이다", "모른다", "전혀 모른다"))
    if 상세기획정도 in ["매우 그렇다", "그렇다", "보통이다"]:
        기본조명 = st.checkbox("기본 조명이 필요한가요?")
        특수조명 = st.checkbox("퍼포먼스를 돕는 특수 조명이 필요한가요?")
        트러스설치 = st.checkbox("트러스 설치가 필요한가요?")
    
        if 기본조명 or 특수조명 or 트러스설치:
            조명_세부사항 = st.text_area("조명 설치와 관련된 구체적인 요구사항을 입력해주세요.")

if "체험 프로그램" in selected_options:
    st.header("체험 프로그램")
    상세기획정도 = st.radio("체험 프로그램에 대한 상세 기획 정도를 선택해주세요.", ("매우 그렇다", "그렇다", "보통이다", "모른다", "전혀 모른다"))
    if 상세기획정도 in ["매우 그렇다", "그렇다", "보통이다"]:
        레크레이션 = st.text_area("어떤 레크레이션 프로그램을 계획하고 있나요?")
        게임부스 = st.text_area("어떤 게임 부스를 설치할 예정인가요?")
        체험부스 = st.text_area("어떤 체험 부스를 설치할 예정인가요?")

if "전시 및 홍보" in selected_options:
    st.header("전시 및 홍보")
    상세기획정도 = st.radio("전시 및 홍보에 대한 상세 기획 정도를 선택해주세요.", ("매우 그렇다", "그렇다", "보통이다", "모른다", "전혀 모른다"))
    if 상세기획정도 in ["매우 그렇다", "그렇다", "보통이다"]:
        전시회 = st.text_area("어떤 전시회를 계획하고 있나요?")
        전시회_세부 = st.checkbox("벽을 세워야 하나요?")
        전시회_작품수 = st.number_input("전시되는 작품 수는 몇 점인가요?", min_value=0, value=10)
        전시회_작품종류 = st.text_area("어떤 작품을 전시할 예정인가요?")
        홍보부스 = st.text_area("어떤 홍보 부스를 설치할 예정인가요?")
        상품판매 = st.text_area("어떤 상품을 판매할 예정인가요?")

if "시설 관리" in selected_options:
    st.header("시설 관리")
    상세기획정도 = st.radio("시설 관리에 대한 상세 기획 정도를 선택해주세요.", ("매우 그렇다", "그렇다", "보통이다", "모른다", "전혀 모른다"))
    if 상세기획정도 in ["매우 그렇다", "그렇다", "보통이다"]:
        무대 = st.text_area("무대 설치에 필요한 사항이 있나요?")
        음향 = st.text_area("음향 장비에 필요한 사항이 있나요?")
        조명 = st.text_area("조명 설치에 필요한 사항이 있나요?")
        전기 = st.text_area("전기 설치에 필요한 사항이 있나요?")
        화장실 = st.text_area("화장실 설치 및 관리에 필요한 사항이 있나요?")

if "안전 관리" in selected_options:
    st.header("안전 관리")
    상세기획정도 = st.radio("안전 관리에 대한 상세 기획 정도를 선택해주세요.", ("매우 그렇다", "그렇다", "보통이다", "모른다", "전혀 모른다"))
    if 상세기획정도 in ["매우 그렇다", "그렇다", "보통이다"]:
        응급처치소 = st.text_area("응급처치소 설치에 필요한 사항이 있나요?")
        안전요원 = st.number_input("안전 요원이 몇 명 필요한가요?", min_value=0, value=10)
        소방설비 = st.text_area("소방 설비에 필요한 사항이 있나요?")

if "교통 및 주차" in selected_options:
    st.header("교통 및 주차")
    상세기획정도 = st.radio("교통 및 주차에 대한 상세 기획 정도를 선택해주세요.", ("매우 그렇다", "그렇다", "보통이다", "모른다", "전혀 모른다"))
    if 상세기획정도 in ["매우 그렇다", "그렇다", "보통이다"]:
        교통통제 = st.text_area("교통 통제에 필요한 사항이 있나요?")
        주차장확보 = st.text_area("주차장 확보에 필요한 사항이 있나요?")
        셔틀버스운영 = st.text_area("셔틀버스 운영 계획이 있나요?")

if "청소 및 위생" in selected_options:
    st.header("청소 및 위생")
    상세기획정도 = st.radio("청소 및 위생에 대한 상세 기획 정도를 선택해주세요.", ("매우 그렇다", "그렇다", "보통이다", "모른다", "전혀 모른다"))
    if 상세기획정도 in ["매우 그렇다", "그렇다", "보통이다"]:
        쓰레기통배치 = st.text_area("쓰레기통 배치 계획이 있나요?")
        청소인력 = st.number_input("청소 인력이 몇 명 필요한가요?", min_value=0, value=5)
        화장실청결관리 = st.text_area("화장실 청결 관리를 어떻게 할 계획인가요?")

if "홍보 전략" in selected_options:
    st.header("홍보 전략")
    상세기획정도 = st.radio("홍보 전략에 대한 상세 기획 정도를 선택해주세요.", ("매우 그렇다", "그렇다", "보통이다", "모른다", "전혀 모른다"))
    if 상세기획정도 in ["매우 그렇다", "그렇다", "보통이다"]:
        홍보_옵션 = ["온라인 홍보", "오프라인 홍보", "SNS", "언론", "광고"]
        홍보_선택 = st.multiselect("어떤 홍보 전략이 필요한가요?", 홍보_옵션)
        홍보_예산 = st.number_input("홍보 예산을 입력해주세요.", min_value=0, value=0, step=1000)
        st.markdown(f'<p class="small-text">{format_number(홍보_예산)}</p>', unsafe_allow_html=True)

        for 옵션 in 홍보_선택:
            st.text_input(f"{옵션} 세부 사항을 입력해주세요.")

if "파트너십 및 후원" in selected_options:
    st.header("파트너십 및 후원")
    상세기획정도 = st.radio("파트너십 및 후원에 대한 상세 기획 정도를 선택해주세요.", ("매우 그렇다", "그렇다", "보통이다", "모른다", "전혀 모른다"))
    if 상세기획정도 in ["매우 그렇다", "그렇다", "보통이다"]:
        스폰서모집 = st.text_area("스폰서를 어떻게 모집할 계획인가요?")
        후원계약 = st.text_area("후원 계약을 어떻게 진행할 예정인가요?")
        파트너십관리 = st.text_area("파트너십 관리를 어떻게 할 계획인가요?")

if "티켓 판매" in selected_options:
    st.header("티켓 판매")
    상세기획정도 = st.radio("티켓 판매에 대한 상세 기획 정도를 선택해주세요.", ("매우 그렇다", "그렇다", "보통이다", "모른다", "전혀 모른다"))
    if 상세기획정도 in ["매우 그렇다", "그렇다", "보통이다"]:
        티켓가격 = st.number_input("티켓 가격을 어떻게 책정할 예정인가요?", min_value=0, value=10000, step=1000)
        st.markdown(f'<p class="small-text">{format_number(티켓가격)}</p>', unsafe_allow_html=True)
        판매채널 = st.text_area("티켓을 어떤 채널을 통해 판매할 예정인가요?")
        예매관리 = st.text_area("예매 관리를 어떻게 진행할 예정인가요?")

if "인력 섭외" in selected_options:
    st.header("인력 섭외")
    상세기획정도 = st.radio("인력 섭외에 대한 상세 기획 정도를 선택해주세요.", ("매우 그렇다", "그렇다", "보통이다", "모른다", "전혀 모른다"))
    if 상세기획정도 in ["매우 그렇다", "그렇다", "보통이다"]:
        인력_옵션 = ["설치 인력", "의전 및 행사 도우미 인력", "단순 운영 인력", "기타"]
        인력_선택 = st.multiselect("어떤 인력이 필요한가요?", 인력_옵션)

        for 인력 in 인력_선택:
            미정 = st.checkbox(f"{인력} 인원이 미정인가요?", key=인력)
            if 미정:
                st.text_input(f"{인력} 예상 인원 수를 입력해주세요.")
            else:
                st.number_input(f"{인력} 인원이 몇 명 필요한가요?", min_value=0, value=1, key=f"{인력}_수")

if "행사 진행" in selected_options:
    st.header("행사 진행")
    상세기획정도 = st.radio("행사 진행에 대한 상세 기획 정도를 선택해주세요.", ("매우 그렇다", "그렇다", "보통이다", "모른다", "전혀 모른다"))
    if 상세기획정도 in ["매우 그렇다", "그렇다", "보통이다"]:
        행사진행자 = st.text_area("행사 진행자를 어떻게 선정할 예정인가요?")
        진행계획 = st.text_area("행사 진행 계획을 어떻게 할 예정인가요?")
        진행순서 = st.text_area("행사 진행 순서를 어떻게 구성할 예정인가요?")

if "평가 및 피드백" in selected_options:
    st.header("평가 및 피드백")
    상세기획정도 = st.radio("평가 및 피드백에 대한 상세 기획 정도를 선택해주세요.", ("매우 그렇다", "그렇다", "보통이다", "모른다", "전혀 모른다"))
    if 상세기획정도 in ["매우 그렇다", "그렇다", "보통이다"]:
        참가자피드백 = st.text_area("참가자 피드백을 어떻게 수집할 예정인가요?")
        성과분석 = st.text_area("성과 분석을 어떻게 할 예정인가요?")
        개선사항도출 = st.text_area("개선 사항을 어떻게 도출할 예정인가요?")

if "영상 및 미디어" in selected_options:
    st.header("영상 및 미디어")
    상세기획정도 = st.radio("영상 및 미디어에 대한 상세 기획 정도를 선택해주세요.", ("매우 그렇다", "그렇다", "보통이다", "모른다", "전혀 모른다"))
    if 상세기획정도 in ["매우 그렇다", "그렇다", "보통이다"]:
        영상_옵션 = ["중계", "사전 영상 제작", "스케치 영상", "유튜브 연간 진행", "숏폼"]
        영상_선택 = st.multiselect("어떤 영상 제작이 필요한가요?", 영상_옵션)
        
        if "중계" in 영상_선택:
            중계_편수 = st.number_input("중계는 몇 편이 필요한가요?", min_value=0, value=1)
            중계_길이 = st.text_input("중계 영상의 예상 길이는 얼마인가요?")
            중계_공간 = st.text_area("중계 세팅 공간의 규모가 어떻게 되나요?")
            중계_카메라 = st.text_area("중계에 필요한 카메라 대수는 몇 대인가요?")
        
        if "사전 영상 제작"에 대한 세부사항을 입력해주세요.")
            사전영상_편수 = st.number_input("사전 영상은 몇 편이 필요한가요?", min_value=0, value=1)
            사전영상_길이 = st.text_input("사전 영상의 예상 길이는 얼마인가요?")
            사전영상_출연진 = st.checkbox("출연진 섭외가 필요한가요?")
        
        if "스케치 영상" in 영상_선택:
            스케치영상_편수 = st.number_input("스케치 영상은 몇 편이 필요한가요?", min_value=0, value=1)
            스케치영상_길이 = st.text_input("스케치 영상의 예상 길이는 얼마인가요?")
        
        if "유튜브 연간 진행" in 영상_선택:
            유튜브_편수 = st.number_input("유튜브 연간 진행은 몇 편이 필요한가요?", min_value=0, value=12)
            유튜브_길이 = st.text_input("유튜브 영상의 예상 길이는 얼마인가요?")
            유튜브_정기발행 = st.checkbox("정기 발행인가요?")
            if 유튜브_정기발행:
                유튜브_빈도 = st.text_area("발행 빈도를 입력해주세요.")
        
        if "숏폼" in 영상_선택:
            숏폼_편수 = st.number_input("숏폼 영상은 몇 편이 필요한가요?", min_value=0, value=5)
            숏폼_길이 = st.text_input("숏폼 영상의 예상 길이는 얼마인가요?")

if "특수 효과" in selected_options:
    st.header("특수 효과")
    상세기획정도 = st.radio("특수 효과에 대한 상세 기획 정도를 선택해주세요.", ("매우 그렇다", "그렇다", "보통이다", "모른다", "전혀 모른다"))
    if 상세기획정도 in ["매우 그렇다", "그렇다", "보통이다"]:
        무대특수효과 = st.text_area("무대 특수 효과 계획이 있나요?")
        특수효과_필요 = st.checkbox("특수효과가 정해졌나요?")
        if 특수효과_필요:
            특수효과_디테일 = st.text_area("구체적인 디테일을 입력해주세요.")

if "장비 대여" in selected_options:
    st.header("장비 대여")
    상세기획정도 = st.radio("장비 대여에 대한 상세 기획 정도를 선택해주세요.", ("매우 그렇다", "그렇다", "보통이다", "모른다", "전혀 모른다"))
    if 상세기획정도 in ["매우 그렇다", "그렇다", "보통이다"]:
        빔프로젝터 = st.text_area("빔 프로젝터 대여 계획이 있나요?")
        LEDPanels = st.text_area("LED 패널 대여 계획이 있나요?")
        장비_제작 = st.checkbox("장비 제작이 필요한가요?")
        if 장비_제작:
            장비_디테일 = st.text_area("구체적인 디테일을 입력해주세요.")

if "VR/AR 기술" in selected_options:
    st.header("VR/AR 기술")
    상세기획정도 = st.radio("VR/AR 기술에 대한 상세 기획 정도를 선택해주세요.", ("매우 그렇다", "그렇다", "보통이다", "모른다", "전혀 모른다"))
    if 상세기획정도 in ["매우 그렇다", "그렇다", "보통이다"]:
        XRVR콘텐츠 = st.text_area("XR 및 VR 콘텐츠 계획이 있나요?")

if "전시 부스" in selected_options:
    st.header("전시 부스")
    상세기획정도 = st.radio("전시 부스에 대한 상세 기획 정도를 선택해주세요.", ("매우 그렇다", "그렇다", "보통이다", "모른다", "전혀 모른다"))
    if 상세기획정도 in ["매우 그렇다", "그렇다", "보통이다"]:
        전시장부스 = st.text_area("전시장 부스(옥타놈/블록) 설치 계획이 있나요?")
        팝업부스 = st.text_area("팝업 부스 설치 계획이 있나요?")

if "디자인" in selected_options:
    st.header("디자인")
    상세기획정도 = st.radio("디자인에 대한 상세 기획 정도를 선택해주세요.", ("매우 그렇다", "그렇다", "보통이다", "모른다", "전혀 모른다"))
    if 상세기획정도 in ["매우 그렇다", "그렇다", "보통이다"]:
        이디디자인 = st.text_area("2D 디자인 계획이 있나요?")
        쓰리디디자인 = st.text_area("3D 디자인 계획이 있나요?")

if "콘텐츠 제작" in selected_options:
    st.header("콘텐츠 제작")
    상세기획정도 = st.radio("콘텐츠 제작에 대한 상세 기획 정도를 선택해주세요.", ("매우 그렇다", "그렇다", "보통이다", "모른다", "전혀 모른다"))
    if 상세기획정도 in ["매우 그렇다", "그렇다", "보통이다"]:
        교육콘텐츠 = st.text_area("교육 콘텐츠 개발 계획이 있나요?")

if "인플루언서" in selected_options:
    st.header("인플루언서")
    상세기획정도 = st.radio("인플루언서에 대한 상세 기획 정도를 선택해주세요.", ("매우 그렇다", "그렇다", "보통이다", "모른다", "전혀 모른다"))
    if 상세기획정도 in ["매우 그렇다", "그렇다", "보통이다"]:
        인플루언서_팔로워 = st.number_input("인플루언서는 몇 명 이상의 팔로워를 가지고 있어야 하나요?", min_value=0, value=10000)
        인플루언서_발행 = st.number_input("인플루언서의 발행 건수는 몇 건이 필요한가요?", min_value=0, value=5)
        인플루언서_선호 = st.text_area("선호하는 인플루언서가 있나요?")
        인플루언서_컨택 = st.checkbox("컨택을 했나요?")
        인플루언서_섭외 = st.text_area("컨택을 했다면, 섭외 내용과 진행 상황을 입력해주세요.")

if "행사 관리" in selected_options:
    st.header("행사 관리")
    상세기획정도 = st.radio("행사 관리에 대한 상세 기획 정도를 선택해주세요.", ("매우 그렇다", "그렇다", "보통이다", "모른다", "전혀 모른다"))
    if 상세기획정도 in ["매우 그렇다", "그렇다", "보통이다"]:
        행사보험 = st.text_area("행사 보험 가입 계획이 있나요?")
        등록매표 = st.text_area("등록 및 매표 시스템 계획이 있나요?")

# 데이터 저장 및 다운로드
def save_data(data):
    output = StringIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    for key, value in data.items():
        df = pd.DataFrame.from_dict(value, orient='index', columns=['내용'])
        df.to_excel(writer, sheet_name=key)
    writer.save()
    return output.getvalue()

data = {
    "기본정보": {
        "용역명": 용역명,
        "용역목적": 용역목적,
        "목표인원": 목표인원,
        "용역담당자": 용역담당자,
    },
    "필수정보": {
        "총예산": format_number(총예산),
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

# 각 선택된 옵션에 따라 데이터를 추가합니다
if "공연 및 행사" in selected_options:
    data["공연 및 행사"] = {
        "음악공연": 음악공연,
        "댄스공연": 댄스공연,
        "특별행사": 특별행사,
        "무대_악기": 무대_악기,
        "무대_인원": 무대_인원,
        "LED_설치": LED_설치,
        "LED_제작": LED_제작 if LED_설치 else "",
        "제작_필요": 제작_필요,
        "제작_항목": 제작_항목 if 제작_필요 else "",
        "제작_디테일": 제작_디테일 if 제작_필요 else ""
    }

if "조명" in selected_options:
    data["조명"] = {
        "기본조명": 기본조명,
        "특수조명": 특수조명,
        "트러스설치": 트러스설치,
        "조명_세부사항": 조명_세부사항 if 기본조명 or 특수조명 or 트러스설치 else ""
    }

# 선택된 모든 카테고리에 대해 동일한 방식으로 데이터를 추가합니다
# (코드 생략)

excel_data = save_data(data)

if st.button("제출"):
    st.write("설문이 제출되었습니다. 감사합니다!")
    st.download_button(label="발주요청서 다운로드", data=excel_data, file_name="발주요청서.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
