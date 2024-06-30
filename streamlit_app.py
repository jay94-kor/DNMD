import streamlit as st

def main():
    st.title("행사 기획 및 분리 발주 설문")

    # Initialize session state for data
    if 'data' not in st.session_state:
        st.session_state.data = {}

    collect_basic_info()
    collect_event_overview()
    collect_event_format_and_venue()
    collect_components_and_services()
    collect_marketing_and_promotion()
    collect_staffing()
    collect_tech_and_equipment()
    collect_budget_and_sponsorship()
    collect_risk_management()

def collect_basic_info():
    st.header("1. 기본 정보")
    st.session_state.data['name'] = st.text_input("이름")
    st.session_state.data['email'] = st.text_input("이메일")
    st.session_state.data['department'] = st.text_input("근무 부서")
    st.session_state.data['position'] = st.selectbox("직급", ["사원", "대리", "과장", "차장", "부장", "기타"])
    st.session_state.data['experience'] = st.number_input("행사 기획 경험 (년)", min_value=0, max_value=50)
    st.session_state.data['event_types'] = st.multiselect("주로 기획하는 행사 유형", ["콘서트", "컨퍼런스", "전시회", "축제", "기업 행사", "기타"])

def collect_event_overview():
    st.header("2. 행사 개요")
    st.session_state.data['has_current_event'] = st.radio("현재 계획 중인 행사가 있나요?", ["예", "아니오"])
    if st.session_state.data['has_current_event'] == "예":
        st.session_state.data['event_description'] = st.text_area("간단히 설명해주세요")
    st.session_state.data['event_purpose'] = st.multiselect("행사의 주요 목적은 무엇인가요?", 
                                   ["브랜드 인지도 향상", "고객 관계 강화", "신제품 출시", 
                                    "교육 및 정보 제공", "수익 창출", "문화/예술 증진", "기타"])
    st.session_state.data['expected_participants'] = st.select_slider("예상 참가자 수", 
                                             options=["50명 미만", "50-100명", "101-500명", "501-1000명", "1000명 이상"])
    st.session_state.data['budget_status'] = st.radio("예산 협의 상태", ["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"])
    if st.session_state.data['budget_status'] in ["확정됨", "거의 확정됨"]:
        st.session_state.data['budget_range'] = st.select_slider("행사 예산 범위", 
                                    options=["1000만원 미만", "1000만원 - 5000만원", "5000만원 - 1억원", 
                                             "1억원 - 5억원", "5억원 이상"])
    else:
        st.info("예산이 확정되면 더 정확한 계획을 세울 수 있습니다.")

def collect_event_format_and_venue():
    st.header("3. 행사 형태 및 장소")
    st.session_state.data['event_format'] = st.radio("행사 형태", ["오프라인 행사", "온라인 행사 (라이브 스트리밍)", 
                                        "하이브리드 (온/오프라인 병행)", "영상 콘텐츠 제작", "기타"])
    if st.session_state.data['event_format'] in ["오프라인 행사", "하이브리드 (온/오프라인 병행)"]:
        st.session_state.data['venue_type'] = st.radio("행사 장소 유형", ["실내 (호텔, 컨벤션 센터 등)", "야외 (공원, 광장 등)", "혼합형 (실내+야외)", "아직 미정"])
        st.session_state.data['venue_status'] = st.radio("행사 장소 협의 상태", ["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"])
        if st.session_state.data['venue_status'] in ["확정됨", "거의 확정됨"]:
            st.session_state.data['venue'] = st.text_input("구체적인 장소")
        else:
            st.session_state.data['region'] = st.text_input("예정 지역")

def collect_components_and_services():
    st.header("4. 행사 구성 요소 및 업체 선택")
    st.write("필요한 서비스를 선택하고 각 항목에 대한 세부 정보를 입력해주세요.")
    collect_stage_and_equipment()
    collect_interpretation_and_catering()

def collect_stage_and_equipment():
    st.subheader("무대 및 장비")
    st.session_state.data['stage_company'] = st.checkbox("무대 설치 업체")
    if st.session_state.data['stage_company']:
        st.session_state.data['stage_size_known'] = st.radio("무대 크기가 정해졌나요?", ["예", "아니오"])
        if st.session_state.data['stage_size_known'] == "예":
            st.session_state.data['stage_size'] = st.text_input("무대 크기 (예: 10m x 5m)")
        else:
            st.session_state.data['stage_capacity'] = st.slider("무대에 동시에 최대 몇 명이 올라갈 예정인가요?", 1, 100)
            st.session_state.data['stage_performance'] = st.multiselect("무대에서 어떤 종류의 퍼포먼스가 있을 예정인가요?", 
                                                           ["발표/연설", "음악 공연", "댄스 퍼포먼스", "연극", "기타"])
        st.session_state.data['stage_design'] = st.text_area("특별한 무대 디자인 요구사항")
    st.session_state.data['sound_company'] = st.checkbox("음향 시스템 업체")
    if st.session_state.data['sound_company']:
        st.session_state.data['mic_count'] = st.number_input("필요한 마이크 개수", min_value=1)
        st.session_state.data['live_music'] = st.checkbox("라이브 음악 공연 포함")
        st.session_state.data['sound_requirements'] = st.text_area("특별한 음향 요구사항")
    st.session_state.data['lighting_company'] = st.checkbox("조명 장비 업체")
    if st.session_state.data['lighting_company']:
        st.session_state.data['special_lighting'] = st.checkbox("특수 조명 효과 필요")
        st.session_state.data['lighting_requirements'] = st.text_area("조명에 대한 특별한 요구사항")
    st.session_state.data['led_company'] = st.checkbox("LED 스크린 업체")
    if st.session_state.data['led_company']:
        st.session_state.data['led_size_known'] = st.radio("LED 스크린 크기가 정해졌나요?", ["예", "아니오"])
        if st.session_state.data['led_size_known'] == "예":
            st.session_state.data['led_size'] = st.text_input("LED 스크린 크기 (예: 5m x 3m)")
        else:
            st.session_state.data['led_purpose'] = st.multiselect("LED 스크린의 주요 용도는 무엇인가요?", 
                                                     ["프레젠테이션 표시", "라이브 중계", "배경 그래픽", "기타"])

def collect_interpretation_and_catering():
    st.subheader("통역 및 케이터링")
    st.session_state.data['interpretation_company'] = st.checkbox("동시통역 시스템 업체")
    if st.session_state.data['interpretation_company']:
        st.session_state.data['languages'] = st.multiselect("필요한 언어", ["영어", "중국어", "일본어", "기타"])
        st.session_state.data['interpreter_needed'] = st.checkbox("통역사 필요")
    st.session_state.data['catering_company'] = st.checkbox("케이터링 서비스 업체")
    if st.session_state.data['catering_company']:
        st.session_state.data['meal_type'] = st.radio("식사 유형", ["뷔페", "플레이티드 서비스", "칵테일 리셉션", "기타"])
        st.session_state.data['special_diet'] = st.text_area("특별 식단 요구사항 (예: 채식, 할랄 등)")

def collect_marketing_and_promotion():
    st.subheader("마케팅 및 홍보")
    st.session_state.data['marketing_channels'] = st.multiselect("사용할 홍보 채널", 
                                        ["소셜 미디어", "이메일 마케팅", "언론 보도", "온라인 광고", 
                                         "오프라인 광고 (현수막, 포스터 등)", "인플루언서 마케팅", "기타"])
    st.session_state.data['branding_status'] = st.radio("행사 브랜딩 계획 상태", ["확정됨", "거의 확정됨", "기획 중", "아직 시작 못함"])
    if st.session_state.data['branding_status'] in ["확정됨", "거의 확정됨", "기획 중"]:
        st.session_state.data['branding_plan'] = st.text_area("브랜딩 계획 설명")

def collect_staffing():
    st.subheader("인력 관리")
    st.session_state.data['staff_number'] = st.number_input("행사 당일 필요한 예상 인력", min_value=1)
    st.session_state.data['external_staff'] = st.multiselect("외부에서 고용할 필요가 있는 인력", 
                                    ["행사 진행 요원", "보안 요원", "기술 지원 인력", "MC 또는 사회자", 
                                     "공연자 또는 연사", "촬영 및 영상 제작 팀", "기타"])
    if "공연자 또는 연사" in st.session_state.data['external_staff']:
        if 'stage_performance' in st.session_state.data:
            st.write("선택하신 무대 퍼포먼스:", st.session_state.data['stage_performance'])
        st.session_state.data['performer_count'] = st.number_input("공연자 또는 연사의 총 인원", min_value=1)
        st.session_state.data['performer_details'] = st.text_area("공연자 또는 연사에 대한 추가 정보")

def collect_tech_and_equipment():
    st.subheader("기술 및 장비")
    st.session_state.data['tech_requirements'] = st.multiselect("필요한 기술적 요구사항", 
                                       ["와이파이 네트워크", "라이브 스트리밍 장비", "촬영 장비", 
                                        "행사 관리 소프트웨어", "모바일 앱", "VR/AR 기술", "기타"])

def collect_budget_and_sponsorship():
    st.subheader("예산 및 스폰서십")
    st.session_state.data['sponsorship_status'] = st.radio("스폰서 유치 계획 상태", ["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"])
    if st.session_state.data['sponsorship_status'] in ["확정됨", "거의 확정됨", "협의 중"]:
        st.session_state.data['sponsorship_types'] = st.multiselect("고려 중인 스폰서십 유형", 
                                           ["금전적 후원", "현물 협찬", "미디어 파트너십", "기술 파트너십", "기타"])

def collect_risk_management():
    st.subheader("리스크 관리")
    st.session_state.data['potential_risks'] = st.multiselect("우려되는 잠재적 리스크", 
                                     ["날씨 (야외 행사의 경우)", "예산 초과", "참가자 수 미달", 
                                      "기술적 문제", "안전 및 보안 문제", "기타"])
    st.session_state.data['risk_mitigation_status'] = st.radio("리스크 대비책 수립 상태", ["완료", "진행 중", "시작 전", "도움 필요"])
    if st.session_state.data['risk_mitigation_status'] in ["완료", "진행 중"]:
        st.session_state.data['risk_mitigation_plan'] = st.text_area("리스크 대비책 설명")

if __name__ == "__main__":
    main()
