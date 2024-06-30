import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

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
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        border-radius: 5px;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# 진행 상황 표시 함수
def display_progress(current_step, total_steps):
    progress = (current_step / total_steps) * 100
    st.markdown(f"""
        <div class="progress-bar">
            <div class="progress" style="width: {progress}%;"></div>
        </div>
        <p style="text-align: center;">진행 상황: {current_step} / {total_steps}</p>
    """, unsafe_allow_html=True)

# 개선된 일정 입력 함수
def improved_schedule_input():
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("행사 시작일", value=st.session_state.data.get('event_start_date', datetime.now().date()))
    with col2:
        end_date = st.date_input("행사 종료일", value=st.session_state.data.get('event_end_date', start_date))
    
    st.session_state.data['event_start_date'] = start_date
    st.session_state.data['event_end_date'] = end_date

    setup_options = ["전날부터", "당일"]
    teardown_options = ["당일 철수", "다음날 철수"]

    col3, col4 = st.columns(2)
    with col3:
        setup_choice = st.selectbox("셋업 시작", setup_options, index=setup_options.index(st.session_state.data.get('setup_choice', '전날부터')))
    with col4:
        teardown_choice = st.selectbox("철수", teardown_options, index=teardown_options.index(st.session_state.data.get('teardown_choice', '당일 철수')))

    st.session_state.data['setup_choice'] = setup_choice
    st.session_state.data['teardown_choice'] = teardown_choice

    st.session_state.data['setup_date'] = start_date - timedelta(days=1) if setup_choice == "전날부터" else start_date
    st.session_state.data['teardown_date'] = end_date if teardown_choice == "당일 철수" else end_date + timedelta(days=1)

    st.write(f"셋업 일자: {st.session_state.data['setup_date']}")
    st.write(f"철수 일자: {st.session_state.data['teardown_date']}")

    event_duration = (end_date - start_date).days + 1
    st.session_state.data['event_duration'] = event_duration
    st.write(f"행사 기간: {event_duration}일")

# 기본 정보 표시 함수
def display_basic_info():
    st.session_state.data['name'] = st.text_input("이름", st.session_state.data.get('name', ''))
    st.session_state.data['department'] = st.text_input("근무 부서", st.session_state.data.get('department', ''))
    
    position_options = ["파트너 기획자", "선임", "책임", "수석"]
    st.session_state.data['position'] = st.selectbox("직급", position_options, index=position_options.index(st.session_state.data.get('position', '파트너 기획자')))
    
    st.session_state.data['event_types'] = st.multiselect("주로 기획하는 행사 유형", 
        ["콘서트", "컨퍼런스", "전시회", "축제", "기업 행사", "기타"], 
        default=st.session_state.data.get('event_types', []))
    
    st.session_state.data['event_name'] = st.text_input("용역명", st.session_state.data.get('event_name', ''))

    improved_schedule_input()

# 행사 개요 표시 함수
def display_event_overview():
    st.session_state.data['event_purpose'] = st.multiselect("용역의 주요 목적", 
        ["브랜드 인지도 향상", "고객 관계 강화", "신제품 출시", "교육 및 정보 제공", "수익 창출", "문화/예술 증진", "기타"],
        default=st.session_state.data.get('event_purpose', []))
    
    col1, col2 = st.columns(2)
    with col1:
        participants_undefined = st.checkbox("예상 참가자 수 미정", value=st.session_state.data.get('participants_undefined', False))
    with col2:
        participants_over_2000 = st.checkbox("2000명 이상", value=st.session_state.data.get('participants_over_2000', False))

    if not participants_undefined:
        if participants_over_2000:
            st.session_state.data['expected_participants'] = "2000명 이상"
        else:
            st.session_state.data['expected_participants'] = st.slider("예상 참가자 수", 0, 2000, value=st.session_state.data.get('expected_participants', 100))
    else:
        st.session_state.data['expected_participants'] = "미정"

    st.session_state.data['contract_type'] = st.selectbox("계약 형태", ["수의계약", "입찰", "B2B"], index=["수의계약", "입찰", "B2B"].index(st.session_state.data.get('contract_type', '수의계약')))
    st.session_state.data['budget_status'] = st.selectbox("예산 협의 상태", ["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"], 
                                                      index=["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"].index(st.session_state.data.get('budget_status', '협의 중')))

# 행사 형태 및 장소 표시 함수
def display_event_format_and_venue():
    st.session_state.data['event_format'] = st.selectbox("행사 형태", 
        ["오프라인 행사", "온라인 행사 (라이브 스트리밍)", "하이브리드 (온/오프라인 병행)", "영상 콘텐츠 제작", "기타"], 
        index=["오프라인 행사", "온라인 행사 (라이브 스트리밍)", "하이브리드 (온/오프라인 병행)", "영상 콘텐츠 제작", "기타"].index(st.session_state.data.get('event_format', '오프라인 행사')))
    
    if st.session_state.data['event_format'] in ["오프라인 행사", "하이브리드 (온/오프라인 병행)"]:
        st.session_state.data['venue_type'] = st.selectbox("행사 장소 유형", 
            ["실내 (호텔, 컨벤션 센터 등)", "야외 (공원, 광장 등)", "혼합형 (실내+야외)", "아직 미정"], 
            index=["실내 (호텔, 컨벤션 센터 등)", "야외 (공원, 광장 등)", "혼합형 (실내+야외)", "아직 미정"].index(st.session_state.data.get('venue_type', '실내 (호텔, 컨벤션 센터 등)')))
        st.session_state.data['venue_status'] = st.selectbox("행사 장소 협의 상태", 
            ["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"], 
            index=["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"].index(st.session_state.data.get('venue_status', '협의 중')))
        
        if st.session_state.data['venue_status'] in ["확정됨", "거의 확정됨"]:
            st.session_state.data['specific_venue'] = st.text_input("구체적인 장소", st.session_state.data.get('specific_venue', ''))
        else:
            st.session_state.data['expected_area'] = st.text_input("예정 지역", st.session_state.data.get('expected_area', ''))

# 행사 구성 요소 입력 섹션
def display_event_components():
    st.header("행사 구성 요소")
    
    components = {
        "무대 설치": setup_stage,
        "음향 시스템": setup_sound,
        "조명 장비": setup_lighting,
        "LED 스크린": setup_led,
        "동시통역 시스템": setup_interpretation,
        "케이터링 서비스": setup_catering,
        "영상 제작": setup_video_production,
        "마케팅 및 홍보": setup_marketing_and_promotion,
        "인력 관리": setup_staff_management,
        "기술 및 장비": setup_technology_and_equipment,
        "네트워킹": setup_networking,
        "예산 및 스폰서십": setup_budget_and_sponsorship,
        "리스크 관리": setup_risk_management
    }
    
    for component, setup_func in components.items():
        with st.expander(f"{component}"):
            setup_func()

def setup_stage():
    st.session_state.data['무대 설치'] = st.session_state.data.get('무대 설치', {})
    st.session_state.data['무대 설치']['needed'] = st.checkbox("무대 설치 필요", st.session_state.data['무대 설치'].get('needed', False))
    if st.session_state.data['무대 설치']['needed']:
        st.session_state.data['무대 설치']['stage_features'] = st.multiselect("무대에 필요한 기능", 
            ["발표/연설", "음악 공연", "댄스 퍼포먼스", "연극", "시상식", "기타"], 
            default=st.session_state.data['무대 설치'].get('stage_features', []))
        
        st.session_state.data['무대 설치']['stage_shape'] = st.radio("무대 형태", 
            ["단상형 (ㅡ 모양)", "일자형 (ㅣ 모양)", "T자형", "기타"],
            index=["단상형 (ㅡ 모양)", "일자형 (ㅣ 모양)", "T자형", "기타"].index(st.session_state.data['무대 설치'].get('stage_shape', '단상형 (ㅡ 모양)')))
        
        if st.session_state.data['무대 설치']['stage_shape'] == "기타":
            st.session_state.data['무대 설치']['custom_stage_shape'] = st.text_input("기타 무대 형태 설명", st.session_state.data['무대 설치'].get('custom_stage_shape', ''))

        st.session_state.data['무대 설치']['stage_size'] = st.text_input("무대 크기 (예: 10m x 5m)", st.session_state.data['무대 설치'].get('stage_size', ''))

def setup_sound():
    st.session_state.data['음향 시스템'] = st.session_state.data.get('음향 시스템', {})
    st.session_state.data['음향 시스템']['needed'] = st.checkbox("음향 시스템 필요", st.session_state.data['음향 시스템'].get('needed', False))
    if st.session_state.data['음향 시스템']['needed']:
        st.session_state.data['음향 시스템']['setup_type'] = st.radio("음향 시스템 설치 방식", 
            ["공간과 관객수에 맞게 알아서", "트러스 설치", "바닥 스탠딩", "미정"],
            index=["공간과 관객수에 맞게 알아서", "트러스 설치", "바닥 스탠딩", "미정"].index(st.session_state.data['음향 시스템'].get('setup_type', '공간과 관객수에 맞게 알아서')))
        
        st.session_state.data['음향 시스템']['venue_inspection_needed'] = st.checkbox("장소 답사 필요", st.session_state.data['음향 시스템'].get('venue_inspection_needed', False))
        st.session_state.data['음향 시스템']['house_music_needed'] = st.checkbox("행사 하우스 음악 필요", st.session_state.data['음향 시스템'].get('house_music_needed', False))
        st.session_state.data['음향 시스템']['bgm_needed'] = st.checkbox("기념식/시상식 BGM 필요", st.session_state.data['음향 시스템'].get('bgm_needed', False))

def setup_lighting():
    st.session_state.data['조명 장비'] = st.session_state.data.get('조명 장비', {})
    st.session_state.data['조명 장비']['needed'] = st.checkbox("조명 장비 필요", st.session_state.data['조명 장비'].get('needed', False))
    if st.session_state.data['조명 장비']['needed']:
        st.session_state.data['조명 장비']['lighting_equipment'] = st.multiselect("필요한 조명 장비", 
            ["일반 조명", "무대 조명", "특수 조명", "LED 조명", "이동식 조명", "기타"],
            default=st.session_state.data['조명 장비'].get('lighting_equipment', []))

def setup_led():
    st.session_state.data['LED 스크린'] = st.session_state.data.get('LED 스크린', {})
    st.session_state.data['LED 스크린']['needed'] = st.checkbox("LED 스크린 필요", st.session_state.data['LED 스크린'].get('needed', False))
    if st.session_state.data['LED 스크린']['needed']:
        st.session_state.data['LED 스크린']['screen_purpose'] = st.multiselect("스크린 사용 목적", 
            ["프레젠테이션 표시", "라이브 중계", "배경 그래픽", "무대 세트", "기타"],
            default=st.session_state.data['LED 스크린'].get('screen_purpose', []))
        
        st.session_state.data['LED 스크린']['screen_size'] = st.radio("스크린 크기",
            ["무대에 꽉 차게", "무대보다 약간 작게", "용도에 맞게 알아서", "정확한 규격 입력"],
            index=["무대에 꽉 차게", "무대보다 약간 작게", "용도에 맞게 알아서", "정확한 규격 입력"].index(st.session_state.data['LED 스크린'].get('screen_size', '용도에 맞게 알아서')))
        
        if st.session_state.data['LED 스크린']['screen_size'] == "정확한 규격 입력":
            st.session_state.data['LED 스크린']['custom_screen_size'] = st.text_input("LED 스크린 크기 (예: 5m x 3m)", st.session_state.data['LED 스크린'].get('custom_screen_size', ''))

def setup_catering():
    st.session_state.data['케이터링 서비스'] = st.session_state.data.get('케이터링 서비스', {})
    st.session_state.data['케이터링 서비스']['needed'] = st.checkbox("케이터링 서비스 필요", st.session_state.data['케이터링 서비스'].get('needed', False))
    if st.session_state.data['케이터링 서비스']['needed']:
        st.session_state.data['케이터링 서비스']['meal_type'] = st.radio("식사 유형", 
            ["뷔페", "플레이티드 서비스", "칵테일 리셉션", "도시락", "기타"],
            index=["뷔페", "플레이티드 서비스", "칵테일 리셉션", "도시락", "기타"].index(st.session_state.data['케이터링 서비스'].get('meal_type', '뷔페')))
        
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.data['케이터링 서비스']['staff_meal_count'] = st.slider("스탭 식사 수", 0, 100, st.session_state.data['케이터링 서비스'].get('staff_meal_count', 0))
        with col2:
            st.session_state.data['케이터링 서비스']['vip_meal_count'] = st.slider("VIP/클라이언트 식사 수", 0, 100, st.session_state.data['케이터링 서비스'].get('vip_meal_count', 0))

        st.session_state.data['케이터링 서비스']['special_diet_requirements'] = st.text_input("특별 식단 요구사항", st.session_state.data['케이터링 서비스'].get('special_diet_requirements', ''))

def setup_video_production():
    st.session_state.data['영상 제작'] = st.session_state.data.get('영상 제작', {})
    st.session_state.data['영상 제작']['needed'] = st.checkbox("영상 제작 필요", st.session_state.data['영상 제작'].get('needed', False))
    if st.session_state.data['영상 제작']['needed']:
        st.session_state.data['영상 제작']['video_type'] = st.multiselect("필요한 영상 유형", ["행사 홍보 영상", "행사 중계 영상", "하이라이트 영상", "인터뷰 영상", "기타"], default=st.session_state.data['영상 제작'].get('video_type', []))
        st.session_state.data['영상 제작']['video_length'] = st.text_input("예상 영상 길이", st.session_state.data['영상 제작'].get('video_length', ''))
        st.session_state.data['영상 제작']['video_purpose'] = st.text_area("영상 목적 및 활용 계획", st.session_state.data['영상 제작'].get('video_purpose', ''))
        st.session_state.data['영상 제작']['video_style'] = st.text_area("원하는 영상 스타일 또는 참고 영상", st.session_state.data['영상 제작'].get('video_style', ''))
        
        st.session_state.data['영상 제작']['video_equipment_needed'] = st.checkbox("영상 장비 대여 필요", st.session_state.data['영상 제작'].get('video_equipment_needed', False))
        if st.session_state.data['영상 제작']['video_equipment_needed']:
            st.session_state.data['영상 제작']['video_equipment'] = st.multiselect("필요한 영상 장비", ["카메라", "조명", "마이크", "드론", "기타"], default=st.session_state.data['영상 제작'].get('video_equipment', []))
        
        st.session_state.data['영상 제작']['video_editing_needed'] = st.checkbox("영상 편집 필요", st.session_state.data['영상 제작'].get('video_editing_needed', False))
        if st.session_state.data['영상 제작']['video_editing_needed']:
            st.session_state.data['영상 제작']['video_editing_requirements'] = st.text_area("영상 편집 요구사항", st.session_state.data['영상 제작'].get('video_editing_requirements', ''))

def setup_marketing_and_promotion():
    st.session_state.data['마케팅 및 홍보'] = st.session_state.data.get('마케팅 및 홍보', {})
    st.session_state.data['마케팅 및 홍보']['promo_channels'] = st.multiselect("사용할 홍보 채널", ["소셜 미디어", "이메일 마케팅", "언론 보도", "온라인 광고", "오프라인 광고 (현수막, 포스터 등)", "인플루언서 마케팅", "기타"], default=st.session_state.data['마케팅 및 홍보'].get('promo_channels', []))
    st.session_state.data['마케팅 및 홍보']['branding_status'] = st.radio("행사 브랜딩 계획 상태", ["확정됨", "거의 확정됨", "기획 중", "아직 시작 못함"], index=["확정됨", "거의 확정됨", "기획 중", "아직 시작 못함"].index(st.session_state.data['마케팅 및 홍보'].get('branding_status', '기획 중')))
    if st.session_state.data['마케팅 및 홍보']['branding_status'] in ["확정됨", "거의 확정됨", "기획 중"]:
        st.session_state.data['마케팅 및 홍보']['branding_details'] = st.text_area("브랜딩 계획 설명", st.session_state.data['마케팅 및 홍보'].get('branding_details', ''))

def setup_staff_management():
    st.session_state.data['인력 관리'] = st.session_state.data.get('인력 관리', {})
    st.session_state.data['인력 관리']['expected_staff'] = st.text_input("행사 당일 필요한 예상 인력 수", st.session_state.data['인력 관리'].get('expected_staff', ''))
    st.session_state.data['인력 관리']['external_staff_needed'] = st.multiselect("외부에서 고용할 필요가 있는 인력", ["행사 진행 요원", "보안 요원", "기술 지원 인력", "MC 또는 사회자", "공연자 또는 연사", "촬영 및 영상 제작 팀", "기타"], default=st.session_state.data['인력 관리'].get('external_staff_needed', []))
    if "공연자 또는 연사" in st.session_state.data['인력 관리']['external_staff_needed']:
        st.session_state.data['인력 관리']['performer_details'] = st.text_area("공연자 또는 연사에 대한 추가 정보", st.session_state.data['인력 관리'].get('performer_details', ''))

def setup_technology_and_equipment():
    st.session_state.data['기술 및 장비'] = st.session_state.data.get('기술 및 장비', {})
    st.session_state.data['기술 및 장비']['tech_requirements'] = st.multiselect("필요한 기술적 요구사항", ["와이파이 네트워크", "라이브 스트리밍 장비", "촬영 장비", "행사 관리 소프트웨어", "모바일 앱", "VR/AR 기술", "기타"], default=st.session_state.data['기술 및 장비'].get('tech_requirements', []))
    st.session_state.data['기술 및 장비']['tech_details'] = st.text_area("기술적 요구사항 세부 설명", st.session_state.data['기술 및 장비'].get('tech_details', ''))
    
    if "기타" in st.session_state.data['기술 및 장비']['tech_requirements']:
        st.session_state.data['기술 및 장비']['other_tech_requirements'] = st.text_input("기타 기술적 요구사항", st.session_state.data['기술 및 장비'].get('other_tech_requirements', ''))
    
    st.session_state.data['기술 및 장비']['equipment_rental_needed'] = st.checkbox("장비 대여 필요", st.session_state.data['기술 및 장비'].get('equipment_rental_needed', False))
    if st.session_state.data['기술 및 장비']['equipment_rental_needed']:
        st.session_state.data['기술 및 장비']['equipment_rental_list'] = st.text_area("대여 필요 장비 목록", st.session_state.data['기술 및 장비'].get('equipment_rental_list', ''))

def setup_networking():
    st.session_state.data['네트워킹'] = st.session_state.data.get('네트워킹', {})
    st.session_state.data['네트워킹']['networking_needed'] = st.checkbox("네트워킹 필요 여부", st.session_state.data['네트워킹'].get('networking_needed', False))
    if st.session_state.data['네트워킹']['networking_needed']:
        st.session_state.data['네트워킹']['networking_place_type'] = st.radio("네트워킹 장소 유형", ["실내", "야외", "기타"], index=["실내", "야외", "기타"].index(st.session_state.data['네트워킹'].get('networking_place_type', '실내')))
        st.session_state.data['네트워킹']['networking_people_count'] = st.number_input("네트워킹 예상 인원 수", min_value=1, value=st.session_state.data['네트워킹'].get('networking_people_count', 1))
        st.session_state.data['네트워킹']['networking_equipment'] = st.multiselect("네트워킹에 필요한 장비", ["테이블", "의자", "음향 장비", "조명", "기타"], default=st.session_state.data['네트워킹'].get('networking_equipment', []))
        st.session_state.data['네트워킹']['networking_activities'] = st.text_area("계획된 네트워킹 활동", st.session_state.data['네트워킹'].get('networking_activities', ''))

def setup_budget_and_sponsorship():
    st.session_state.data['예산 및 스폰서십'] = st.session_state.data.get('예산 및 스폰서십', {})
    st.session_state.data['예산 및 스폰서십']['total_budget'] = st.text_input("총 예산", st.session_state.data['예산 및 스폰서십'].get('total_budget', ''))
    st.session_state.data['예산 및 스폰서십']['budget_breakdown'] = st.text_area("예산 항목별 내역", st.session_state.data['예산 및 스폰서십'].get('budget_breakdown', ''))
    st.session_state.data['예산 및 스폰서십']['sponsorship_status'] = st.radio("스폰서 유치 계획 상태", ["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"], index=["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"].index(st.session_state.data['예산 및 스폰서십'].get('sponsorship_status', '협의 중')))
    if st.session_state.data['예산 및 스폰서십']['sponsorship_status'] in ["확정됨", "거의 확정됨", "협의 중"]:
        st.session_state.data['예산 및 스폰서십']['sponsorship_types'] = st.multiselect("고려 중인 스폰서십 유형", ["금전적 후원", "현물 협찬", "미디어 파트너십", "기술 파트너십", "기타"], default=st.session_state.data['예산 및 스폰서십'].get('sponsorship_types', []))
        st.session_state.data['예산 및 스폰서십']['sponsorship_details'] = st.text_area("스폰서십 세부 사항", st.session_state.data['예산 및 스폰서십'].get('sponsorship_details', ''))

def setup_risk_management():
    st.session_state.data['리스크 관리'] = st.session_state.data.get('리스크 관리', {})
    st.session_state.data['리스크 관리']['potential_risks'] = st.multiselect("우려되는 잠재적 리스크", ["날씨 (야외 행사의 경우)", "예산 초과", "참가자 수 미달", "기술적 문제", "안전 및 보안 문제", "기타"], default=st.session_state.data['리스크 관리'].get('potential_risks', []))
    st.session_state.data['리스크 관리']['risk_preparation_status'] = st.radio("리스크 대비책 수립 상태", ["완료", "진행 중", "시작 전", "도움 필요"], index=["완료", "진행 중", "시작 전", "도움 필요"].index(st.session_state.data['리스크 관리'].get('risk_preparation_status', '진행 중')))
    if st.session_state.data['리스크 관리']['risk_preparation_status'] in ["완료", "진행 중"]:
        st.session_state.data['리스크 관리']['risk_preparation_details'] = st.text_area("리스크 대비책 설명", st.session_state.data['리스크 관리'].get('risk_preparation_details', ''))
    st.session_state.data['리스크 관리']['insurance_needed'] = st.checkbox("행사 보험 필요 여부", st.session_state.data['리스크 관리'].get('insurance_needed', False))
    if st.session_state.data['리스크 관리']['insurance_needed']:
        st.session_state.data['리스크 관리']['insurance_types'] = st.multiselect("필요한 보험 유형", ["행사 취소 보험", "책임 보험", "재산 보험", "기타"], default=st.session_state.data['리스크 관리'].get('insurance_types', []))

# 설문 완료 함수
def finalize():
    st.header("설문 완료")
    st.write("수고하셨습니다! 모든 단계를 완료하셨습니다.")
    
    if st.button("설문 저장 및 발주요청서 다운로드"):
        # 설문 데이터 저장 로직 (예: 데이터베이스에 저장)
        save_survey_data(st.session_state.data)
        
        # 발주요청서 생성 및 다운로드
        categories = ["무대 설치", "음향 시스템", "조명 장비", "LED 스크린", "동시통역 시스템", "케이터링 서비스", "영상 제작"]
        for category in categories:
            if category in st.session_state.data and st.session_state.data[category].get('needed', False):
                excel_file = generate_excel_file(st.session_state.data, category)
                st.download_button(
                    label=f"{category} 발주요청서 다운로드",
                    data=excel_file,
                    file_name=f"{category}_발주요청서_{st.session_state.data['name']}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        st.success("설문이 저장되었고, 발주요청서가 생성되었습니다. 위의 버튼을 클릭하여 각 카테고리별 발주요청서를 다운로드 하세요.")

# 설문 데이터 저장 함수
def save_survey_data(data):
    # 여기에 데이터를 저장하는 로직을 구현합니다.
    # 예: 데이터베이스에 저장, 파일로 저장 등
    pass

# 엑셀 파일 생성 함수
def generate_excel_file(data, category):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    # 공통 정보
    common_info = pd.DataFrame({
        '항목': ['이름', '근무 부서', '직급', '주로 기획하는 행사 유형', '용역명', '행사 시작일', '행사 마감일', '진행 일정 (일 수)',
                 '셋업 시작 시간', '리허설 시작 시간', '리허설 마감 시간', '행사 시작 시간', '행사 마감 시간', '철수 마무리 시간',
                 '행사 목적', '예상 참가자 수', '계약 형태', '예산 협의 상태', '행사 형태', '행사 장소 유형', '행사 장소'],
        '내용': [data['name'], data['department'], data['position'], ', '.join(data['event_types']), data['event_name'],
                data['event_start_date'], data['event_end_date'], data['event_duration'], data['setup_start_time'],
                data['rehearsal_start_time'], data['rehearsal_end_time'], data['event_start_time'], data['event_end_time'],
                data['teardown_end_time'], ', '.join(data['event_purpose']), data['expected_participants'],
                data['contract_type'], data['budget_status'], data['event_format'], data.get('venue_type', 'N/A'),
                data.get('specific_venue', data.get('expected_area', 'N/A'))]
    })
    common_info.to_excel(writer, sheet_name='기본 정보', index=False)
    
    # 카테고리별 정보
    if category in data:
        category_info = pd.DataFrame(data[category].items(), columns=['항목', '내용'])
        category_info.to_excel(writer, sheet_name=category, index=False)
    
    writer.save()
    output.seek(0)
    return output

# 메인 함수
def main():
    # 세션 상태 초기화
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'data' not in st.session_state:
        st.session_state.data = {}

    # 단계 정의
    steps = ["기본 정보", "행사 개요", "행사 형태 및 장소", "행사 구성 요소", "마무리"]
    total_steps = len(steps)

    # 진행 상황 표시
    display_progress(st.session_state.step, total_steps)

    # 현재 단계 제목 표시
    st.markdown(f"<h2 class='step-title'>{steps[st.session_state.step - 1]}</h2>", unsafe_allow_html=True)

    # 메인 컨텐츠
    if st.session_state.step == 1:
        display_basic_info()
    elif st.session_state.step == 2:
        display_event_overview()
    elif st.session_state.step == 3:
        display_event_format_and_venue()
    elif st.session_state.step == 4:
        display_event_components()
    elif st.session_state.step == 5:
        finalize()

    # 네비게이션 버튼
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.step > 1:
            if st.button("이전"):
                st.session_state.step -= 1
    with col2:
        if st.session_state.step < total_steps:
            if st.button("다음"):
                if validate_current_step():
                    st.session_state.step += 1
                else:
                    st.error("모든 필수 항목을 채워주세요.")

# 프로그램 실행
if __name__ == "__main__":
    main()
