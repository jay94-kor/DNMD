import streamlit as st

def main():
    st.title("행사 기획 및 분리 발주 설문")

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
    st.session_state.data['project_name'] = st.text_input("용역명", key='project_name')
    st.session_state.data['overview'] = st.text_area("개요", key='overview')
    st.session_state.data['project_amount'] = st.text_input("용역 금액 (원)", key='project_amount')

    st.session_state.data['net_profit'] = st.number_input("순이익 설정 (원)", min_value=0, step=1000, key='net_profit')
    if st.session_state.data['project_amount']:
        project_amount = float(st.session_state.data['project_amount'])
        net_profit = float(st.session_state.data['net_profit'])
        st.session_state.data['net_profit_percentage'] = (net_profit / project_amount) * 100
        st.write(f"순이익률: {st.session_state.data['net_profit_percentage']:.2f} %")
    
    st.session_state.data['event_format'] = st.radio("행사 형태", ["오프라인 행사", "온라인 행사 (라이브 스트리밍)", 
                                        "하이브리드 (온/오프라인 병행)", "영상 콘텐츠 제작", "기타"], key='event_format')
    if st.session_state.data['event_format'] in ["오프라인 행사", "하이브리드 (온/오프라인 병행)"]:
        st.session_state.data['venue_type'] = st.radio("행사 장소 유형", ["실내 (호텔, 컨벤션 센터 등)", "야외 (공원, 광장 등)", "혼합형 (실내+야외)", "아직 미정"], key='venue_type')
        st.session_state.data['venue_status'] = st.radio("행사 장소 협의 상태", ["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"], key='venue_status')
        if st.session_state.data['venue_status'] in ["확정됨", "거의 확정됨"]:
            st.session_state.data['venue'] = st.text_input("구체적인 장소", key='venue')
        else:
            st.session_state.data['region'] = st.text_input("예정 지역", key='region')

def collect_event_overview():
    st.header("2. 행사 개요")
    st.session_state.data['has_current_event'] = st.radio("현재 계획 중인 행사가 있나요?", ["예", "아니오"], key='has_current_event')
    st.session_state.data['event_purpose'] = st.multiselect("행사의 주요 목적은 무엇인가요?", 
                                   ["브랜드 인지도 향상", "고객 관계 강화", "신제품 출시", 
                                    "교육 및 정보 제공", "수익 창출", "문화/예술 증진", "기타"], key='event_purpose')
    st.session_state.data['expected_participants'] = st.text_input("예상 참가자 수", key='expected_participants')

def collect_event_format_and_venue():
    st.header("3. 행사 형태 및 장소")
    if st.session_state.data['event_format'] in ["오프라인 행사", "하이브리드 (온/오프라인 병행)"]:
        st.session_state.data['venue_type'] = st.radio("행사 장소 유형", ["실내 (호텔, 컨벤션 센터 등)", "야외 (공원, 광장 등)", "혼합형 (실내+야외)", "아직 미정"], key='venue_type2')
        st.session_state.data['venue_status'] = st.radio("행사 장소 협의 상태", ["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"], key='venue_status2')
        if st.session_state.data['venue_status'] in ["확정됨", "거의 확정됨"]:
            st.session_state.data['venue'] = st.text_input("구체적인 장소", key='venue2')
        else:
            st.session_state.data['region'] = st.text_input("예정 지역", key='region2')

def collect_components_and_services():
    st.header("4. 행사 구성 요소 및 업체 선택")
    st.write("필요한 서비스를 선택해주세요.")
    st.session_state.data['stage_company'] = st.checkbox("무대 설치 업체", key='stage_company')
    st.session_state.data['sound_company'] = st.checkbox("음향 시스템 업체", key='sound_company')
    st.session_state.data['lighting_company'] = st.checkbox("조명 장비 업체", key='lighting_company')
    st.session_state.data['led_company'] = st.checkbox("LED 스크린 업체", key='led_company')
    st.session_state.data['interpretation_company'] = st.checkbox("동시통역 시스템 업체", key='interpretation_company')
    st.session_state.data['catering_company'] = st.checkbox("케이터링 서비스 업체", key='catering_company')

def collect_marketing_and_promotion():
    st.header("5. 마케팅 및 홍보")
    st.session_state.data['marketing_channels'] = st.multiselect("사용할 홍보 채널", 
                                        ["소셜 미디어", "이메일 마케팅", "언론 보도", "온라인 광고", 
                                         "오프라인 광고 (현수막, 포스터 등)", "인플루언서 마케팅", "기타"], key='marketing_channels')
    st.session_state.data['branding_status'] = st.radio("행사 브랜딩 계획 상태", ["확정됨", "거의 확정됨", "기획 중", "아직 시작 못함"], key='branding_status')
    if st.session_state.data['branding_status'] in ["확정됨", "거의 확정됨", "기획 중"]:
        st.session_state.data['branding_plan'] = st.text_area("브랜딩 계획 설명", key='branding_plan')

def collect_staffing():
    st.header("6. 인력 관리")
    st.session_state.data['staff_number'] = st.text_input("행사 당일 필요한 예상 인력 수", key='staff_number')
    st.session_state.data['external_staff'] = st.multiselect("외부에서 고용할 필요가 있는 인력", 
                                    ["행사 진행 요원", "보안 요원", "기술 지원 인력", "MC 또는 사회자", 
                                     "공연자 또는 연사", "촬영 및 영상 제작 팀", "기타"], key='external_staff')

def collect_tech_and_equipment():
    st.header("7. 기술 및 장비")
    st.session_state.data['tech_requirements'] = st.multiselect("필요한 기술적 요구사항", 
                                       ["와이파이 네트워크", "라이브 스트리밍 장비", "촬영 장비", 
                                        "행사 관리 소프트웨어", "모바일 앱", "VR/AR 기술", "기타"], key='tech_requirements')

def collect_budget_and_sponsorship():
    st.header("8. 예산 및 스폰서십")
    st.session_state.data['sponsorship_status'] = st.radio("스폰서 유치 계획 상태", ["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"], key='sponsorship_status')
    if st.session_state.data['sponsorship_status'] in ["확정됨", "거의 확정됨", "협의 중"]:
        st.session_state.data['sponsorship_types'] = st.multiselect("고려 중인 스폰서십 유형", 
                                           ["금전적 후원", "현물 협찬", "미디어 파트너십", "기술 파트너십", "기타"], key='sponsorship_types')

def collect_risk_management():
    st.header("9. 리스크 관리")
    st.session_state.data['potential_risks'] = st.multiselect("우려되는 잠재적 리스크", 
                                     ["날씨 (야외 행사의 경우)", "예산 초과", "참가자 수 미달", 
                                      "기술적 문제", "안전 및 보안 문제", "기타"], key='potential_risks')
    st.session_state.data['risk_mitigation_status'] = st.radio("리스크 대비책 수립 상태", ["완료", "진행 중", "시작 전", "도움 필요"], key='risk_mitigation_status')
    if st.session_state.data['risk_mitigation_status'] in ["완료", "진행 중"]:
        st.session_state.data['risk_mitigation_plan'] = st.text_area("리스크 대비책 설명", key='risk_mitigation_plan')

if __name__ == "__main__":
    main()
