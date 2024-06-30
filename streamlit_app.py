import streamlit as st
import pandas as pd
from datetime import datetime
import io

def generate_excel_file(data, category):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    # Common information
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
    
    # Category specific information
    if category in data:
        category_info = pd.DataFrame(data[category].items(), columns=['항목', '내용'])
        category_info.to_excel(writer, sheet_name=category, index=False)
    
    writer.save()
    output.seek(0)
    return output

def main():
    st.set_page_config(layout="wide")
    st.title("행사 기획 설문")

    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'data' not in st.session_state:
        st.session_state.data = {}

    # Sidebar for navigation
    st.sidebar.title("진행 상황")
    steps = ["기본 정보", "행사 개요", "행사 형태 및 장소", "구성 요소 선택", "영상", "마케팅 및 홍보", 
             "인력 관리", "기술 및 장비", "네트워킹", "예산 및 스폰서십", "리스크 관리"]
    for i, step in enumerate(steps, 1):
        if st.sidebar.button(f"{i}. {step}", key=f"nav_{i}"):
            st.session_state.step = i

    # Main content
    if st.session_state.step == 1:
        basic_info()
    elif st.session_state.step == 2:
        event_overview()
    elif st.session_state.step == 3:
        event_format_and_venue()
    elif st.session_state.step == 4:
        components_and_vendors()
    elif st.session_state.step == 5:
        video_production()
    elif st.session_state.step == 6:
        marketing_and_promotion()
    elif st.session_state.step == 7:
        staff_management()
    elif st.session_state.step == 8:
        technology_and_equipment()
    elif st.session_state.step == 9:
        networking()
    elif st.session_state.step == 10:
        budget_and_sponsorship()
    elif st.session_state.step == 11:
        risk_management()

    # Progress bar
    st.sidebar.progress(st.session_state.step / len(steps))

    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.step > 1:
            if st.button("이전"):
                st.session_state.step -= 1
    with col2:
        if st.session_state.step < len(steps):
            if st.button("다음"):
                st.session_state.step += 1
        else:
            if st.button("제출"):
                submit_form()

def basic_info():
    st.header("기본 정보")
    with st.form("basic_info_form"):
        st.session_state.data['name'] = st.text_input("이름", st.session_state.data.get('name', ''))
        st.session_state.data['department'] = st.text_input("근무 부서", st.session_state.data.get('department', ''))
        position_options = ["파트너 기획자", "선임", "책임", "수석"]
        current_position = st.session_state.data.get('position', '파트너 기획자')
        position_index = position_options.index(current_position) if current_position in position_options else 0
        st.session_state.data['position'] = st.radio(
            "직급", 
            position_options,
            index=position_index
        )
        st.session_state.data['event_types'] = st.multiselect("주로 기획하는 행사 유형", ["콘서트", "컨퍼런스", "전시회", "축제", "기업 행사", "기타"], default=st.session_state.data.get('event_types', []))
        st.session_state.data['event_name'] = st.text_input("용역명", st.session_state.data.get('event_name', ''))
        st.session_state.data['event_start_date'] = st.date_input("행사 시작일", value=st.session_state.data.get('event_start_date', datetime.now().date()))
        st.session_state.data['event_end_date'] = st.date_input("행사 마감일", value=st.session_state.data.get('event_end_date', datetime.now().date()))
        if st.checkbox("시작일/마감일이 정해지지 않았다면:", value='fast_start_date' in st.session_state.data):
            st.session_state.data['fast_start_date'] = st.date_input("빠른 시작일", value=st.session_state.data.get('fast_start_date', datetime.now().date()))
            st.session_state.data['late_end_date'] = st.date_input("늦은 마감일", value=st.session_state.data.get('late_end_date', datetime.now().date()))
        st.session_state.data['event_duration'] = st.text_input("진행 일정 (일 수)", st.session_state.data.get('event_duration', ''))
        st.session_state.data['setup_start_time'] = st.time_input("셋업 시작 시간", value=st.session_state.data.get('setup_start_time', datetime.now().time()))
        st.session_state.data['rehearsal_start_time'] = st.time_input("리허설 시작 시간", value=st.session_state.data.get('rehearsal_start_time', datetime.now().time()))
        st.session_state.data['rehearsal_end_time'] = st.time_input("리허설 마감 시간", value=st.session_state.data.get('rehearsal_end_time', datetime.now().time()))
        st.session_state.data['event_start_time'] = st.time_input("행사 시작 시간", value=st.session_state.data.get('event_start_time', datetime.now().time()))
        st.session_state.data['event_end_time'] = st.time_input("행사 마감 시간", value=st.session_state.data.get('event_end_time', datetime.now().time()))
        st.session_state.data['teardown_end_time'] = st.time_input("철수 마무리 시간", value=st.session_state.data.get('teardown_end_time', datetime.now().time()))
        if st.checkbox("정확하지 않으면 (예정) 키워드 추가", value='approximate_keyword' in st.session_state.data):
            st.session_state.data['approximate_keyword'] = "예정"
        
        submitted = st.form_submit_button("저장")
        if submitted:
            st.success("기본 정보가 저장되었습니다.")

def event_overview():
    st.header("행사 개요")
    with st.form("event_overview"):
        st.session_state.data['event_purpose'] = st.multiselect("용역의 주요 목적은 무엇인가요?", 
                                           ["브랜드 인지도 향상", "고객 관계 강화", "신제품 출시", "교육 및 정보 제공", 
                                            "수익 창출", "문화/예술 증진", "기타"], 
                                           default=st.session_state.data.get('event_purpose', []))
        st.session_state.data['expected_participants'] = st.text_input("예상 참가자 수", st.session_state.data.get('expected_participants', ''))
        st.session_state.data['contract_type'] = st.radio("계약 형태", ["수의계약", "입찰", "B2B"], index=["수의계약", "입찰", "B2B"].index(st.session_state.data.get('contract_type', '수의계약')))
        st.session_state.data['budget_status'] = st.radio("예산 협의 상태", ["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"], 
                                                          index=["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"].index(st.session_state.data.get('budget_status', '협의 중')))
        st.form_submit_button("저장")

def event_format_and_venue():
    st.header("행사 형태 및 장소")
    with st.form("event_format_and_venue"):
        st.session_state.data['event_format'] = st.radio("행사 형태", ["오프라인 행사", "온라인 행사 (라이브 스트리밍)", "하이브리드 (온/오프라인 병행)", "영상 콘텐츠 제작", "기타"], 
                                                         index=["오프라인 행사", "온라인 행사 (라이브 스트리밍)", "하이브리드 (온/오프라인 병행)", "영상 콘텐츠 제작", "기타"].index(st.session_state.data.get('event_format', '오프라인 행사')))
        
        if st.session_state.data['event_format'] in ["오프라인 행사", "하이브리드 (온/오프라인 병행)"]:
            st.session_state.data['venue_type'] = st.radio("행사 장소 유형", ["실내 (호텔, 컨벤션 센터 등)", "야외 (공원, 광장 등)", "혼합형 (실내+야외)", "아직 미정"], 
                                                           index=["실내 (호텔, 컨벤션 센터 등)", "야외 (공원, 광장 등)", "혼합형 (실내+야외)", "아직 미정"].index(st.session_state.data.get('venue_type', '실내 (호텔, 컨벤션 센터 등)')))
            st.session_state.data['venue_status'] = st.radio("행사 장소 협의 상태", ["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"], 
                                                             index=["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"].index(st.session_state.data.get('venue_status', '협의 중')))
            
            if st.session_state.data['venue_status'] in ["확정됨", "거의 확정됨"]:
                st.session_state.data['specific_venue'] = st.text_input("구체적인 장소", st.session_state.data.get('specific_venue', ''))
            else:
                st.session_state.data['expected_area'] = st.text_input("예정 지역", st.session_state.data.get('expected_area', ''))
        
        st.form_submit_button("저장")

def components_and_vendors():
    st.header("행사 구성 요소 및 필요 업체 선택")
    
    components = {
        "무대 설치": setup_stage,
        "음향 시스템": setup_sound,
        "조명 장비": setup_lighting,
        "LED 스크린": setup_led,
        "동시통역 시스템": setup_interpretation,
        "케이터링 서비스": setup_catering
    }
    
    for component, setup_func in components.items():
        with st.expander(f"{component} 업체"):
            setup_func()

def setup_component(component):
    if component not in st.session_state.data:
        st.session_state.data[component] = {}
    
    st.session_state.data[component]['needed'] = st.checkbox(f"{component} 필요")
    if st.session_state.data[component]['needed']:
        st.session_state.data[component]['plan_status'] = st.radio("계획 상태", ["확정됨", "거의 확정됨", "정하는 중", "모름"], key=f"{component}_status")
        
def setup_component(component):
    if component not in st.session_state.data:
        st.session_state.data[component] = {}
    
    st.session_state.data[component]['needed'] = st.checkbox(f"{component} 필요")
    if st.session_state.data[component]['needed']:
        st.session_state.data[component]['plan_status'] = st.radio("계획 상태", ["확정됨", "거의 확정됨", "정하는 중", "모름"], key=f"{component}_status")
        
        if st.session_state.data[component]['plan_status'] in ["확정됨", "거의 확정됨"]:
            st.session_state.data[component]['details'] = st.text_area(f"{component} 상세 정보", st.session_state.data[component].get('details', ''))
        else:
            st.session_state.data[component]['expected_details'] = st.text_area(f"{component} 예상 정보", st.session_state.data[component].get('expected_details', ''))
        
        st.session_state.data[component]['preferred_vendor'] = st.checkbox(f"선호하는 {component} 업체가 있습니까?")
        if st.session_state.data[component]['preferred_vendor']:
            st.session_state.data[component]['vendor_name'] = st.text_input(f"선호하는 {component} 업체명", st.session_state.data[component].get('vendor_name', ''))
            st.session_state.data[component]['vendor_reason'] = st.multiselect("선호하는 이유", ["합리적인 견적", "제안서 도움", "퀄리티 보장", "기타 이유"], default=st.session_state.data[component].get('vendor_reason', []))
            if "기타 이유" in st.session_state.data[component]['vendor_reason']:
                st.session_state.data[component]['vendor_reason_detail'] = st.text_input("기타 이유", st.session_state.data[component].get('vendor_reason_detail', ''))

def setup_stage():
    setup_component("무대 설치")
    if st.session_state.data["무대 설치"]['needed']:
        if st.session_state.data["무대 설치"]['plan_status'] in ["확정됨", "거의 확정됨"]:
            st.session_state.data["무대 설치"]['stage_size'] = st.text_input("무대 크기", st.session_state.data["무대 설치"].get('stage_size', ''))
        else:
            st.session_state.data["무대 설치"]['expected_stage_size'] = st.text_input("예상 무대 크기", st.session_state.data["무대 설치"].get('expected_stage_size', ''))
            st.session_state.data["무대 설치"]['stage_features'] = st.multiselect("무대에 필요한 기능", ["발표/연설", "음악 공연", "댄스 퍼포먼스", "연극", "기타"], default=st.session_state.data["무대 설치"].get('stage_features', []))

def setup_sound():
    setup_component("음향 시스템")
    if st.session_state.data["음향 시스템"]['needed']:
        if st.session_state.data["음향 시스템"]['plan_status'] in ["확정됨", "거의 확정됨"]:
            st.session_state.data["음향 시스템"]['required_mic_count'] = st.number_input("필요한 마이크 개수", min_value=1, value=st.session_state.data["음향 시스템"].get('required_mic_count', 1))
        else:
            st.session_state.data["음향 시스템"]['expected_sound_equipment'] = st.multiselect("예상 음향 장비", ["마이크", "스피커", "믹서", "기타"], default=st.session_state.data["음향 시스템"].get('expected_sound_equipment', []))

def setup_lighting():
    setup_component("조명 장비")
    if st.session_state.data["조명 장비"]['needed']:
        if st.session_state.data["조명 장비"]['plan_status'] in ["확정됨", "거의 확정됨"]:
            st.session_state.data["조명 장비"]['special_light_effect'] = st.checkbox("특수 조명 효과 필요 여부", st.session_state.data["조명 장비"].get('special_light_effect', False))
        else:
            st.session_state.data["조명 장비"]['expected_light_equipment'] = st.multiselect("예상 조명 장비", ["일반 조명", "무대 조명", "특수 조명", "기타"], default=st.session_state.data["조명 장비"].get('expected_light_equipment', []))

def setup_led():
    setup_component("LED 스크린")
    if st.session_state.data["LED 스크린"]['needed']:
        if st.session_state.data["LED 스크린"]['plan_status'] in ["확정됨", "거의 확정됨"]:
            st.session_state.data["LED 스크린"]['led_screen_size'] = st.text_input("LED 스크린 크기", st.session_state.data["LED 스크린"].get('led_screen_size', ''))
            st.session_state.data["LED 스크린"]['led_screen_purpose'] = st.multiselect("스크린 사용 목적", ["프레젠테이션 표시", "라이브 중계", "배경 그래픽", "기타"], default=st.session_state.data["LED 스크린"].get('led_screen_purpose', []))
        else:
            st.session_state.data["LED 스크린"]['expected_led_screen_size'] = st.text_input("예상 LED 스크린 크기", st.session_state.data["LED 스크린"].get('expected_led_screen_size', ''))

def setup_interpretation():
    setup_component("동시통역 시스템")
    if st.session_state.data["동시통역 시스템"]['needed']:
        if st.session_state.data["동시통역 시스템"]['plan_status'] in ["확정됨", "거의 확정됨"]:
            st.session_state.data["동시통역 시스템"]['required_languages'] = st.multiselect("필요한 언어", ["영어", "중국어", "일본어", "기타"], default=st.session_state.data["동시통역 시스템"].get('required_languages', []))
            st.session_state.data["동시통역 시스템"]['need_interpreter'] = st.checkbox("통역사 필요 여부", st.session_state.data["동시통역 시스템"].get('need_interpreter', False))
        else:
            st.session_state.data["동시통역 시스템"]['expected_languages'] = st.multiselect("예상 통역 언어", ["영어", "중국어", "일본어", "기타"], default=st.session_state.data["동시통역 시스템"].get('expected_languages', []))

def setup_catering():
    setup_component("케이터링 서비스")
    if st.session_state.data["케이터링 서비스"]['needed']:
        if st.session_state.data["케이터링 서비스"]['plan_status'] in ["확정됨", "거의 확정됨"]:
            st.session_state.data["케이터링 서비스"]['meal_type'] = st.radio("식사 유형", ["뷔페", "플레이티드 서비스", "칵테일 리셉션", "기타"], index=["뷔페", "플레이티드 서비스", "칵테일 리셉션", "기타"].index(st.session_state.data["케이터링 서비스"].get('meal_type', '뷔페')))
            st.session_state.data["케이터링 서비스"]['special_diet_requirements'] = st.text_input("특별 식단 요구사항", st.session_state.data["케이터링 서비스"].get('special_diet_requirements', ''))
        else:
            st.session_state.data["케이터링 서비스"]['expected_meal_type'] = st.radio("예상 식사 유형", ["뷔페", "플레이티드 서비스", "칵테일 리셉션", "기타"], index=["뷔페", "플레이티드 서비스", "칵테일 리셉션", "기타"].index(st.session_state.data["케이터링 서비스"].get('expected_meal_type', '뷔페')))
            st.session_state.data["케이터링 서비스"]['expected_meal_count'] = st.number_input("예상 인원 수", min_value=1, value=st.session_state.data["케이터링 서비스"].get('expected_meal_count', 1))

def video_production():
    st.header("영상 제작")
    with st.form("video_production"):
        st.session_state.data['video_needed'] = st.checkbox("영상 제작 필요", st.session_state.data.get('video_needed', False))
        if st.session_state.data['video_needed']:
            st.session_state.data['video_type'] = st.multiselect("필요한 영상 유형", ["행사 홍보 영상", "행사 중계 영상", "하이라이트 영상", "인터뷰 영상", "기타"], default=st.session_state.data.get('video_type', []))
            st.session_state.data['video_length'] = st.text_input("예상 영상 길이", st.session_state.data.get('video_length', ''))
            st.session_state.data['video_purpose'] = st.text_area("영상 목적 및 활용 계획", st.session_state.data.get('video_purpose', ''))
            st.session_state.data['video_style'] = st.text_area("원하는 영상 스타일 또는 참고 영상", st.session_state.data.get('video_style', ''))
            
            st.session_state.data['video_equipment_needed'] = st.checkbox("영상 장비 대여 필요", st.session_state.data.get('video_equipment_needed', False))
            if st.session_state.data['video_equipment_needed']:
                st.session_state.data['video_equipment'] = st.multiselect("필요한 영상 장비", ["카메라", "조명", "마이크", "드론", "기타"], default=st.session_state.data.get('video_equipment', []))
            
            st.session_state.data['video_editing_needed'] = st.checkbox("영상 편집 필요", st.session_state.data.get('video_editing_needed', False))
            if st.session_state.data['video_editing_needed']:
                st.session_state.data['video_editing_requirements'] = st.text_area("영상 편집 요구사항", st.session_state.data.get('video_editing_requirements', ''))
        
        st.form_submit_button("저장")

def marketing_and_promotion():
    st.header("마케팅 및 홍보")
    with st.form("marketing_and_promotion"):
        st.session_state.data['promo_channels'] = st.multiselect("사용할 홍보 채널", ["소셜 미디어", "이메일 마케팅", "언론 보도", "온라인 광고", "오프라인 광고 (현수막, 포스터 등)", "인플루언서 마케팅", "기타"], default=st.session_state.data.get('promo_channels', []))
        st.session_state.data['branding_status'] = st.radio("행사 브랜딩 계획 상태", ["확정됨", "거의 확정됨", "기획 중", "아직 시작 못함"], index=["확정됨", "거의 확정됨", "기획 중", "아직 시작 못함"].index(st.session_state.data.get('branding_status', '기획 중')))
        if st.session_state.data['branding_status'] in ["확정됨", "거의 확정됨", "기획 중"]:
            st.session_state.data['branding_details'] = st.text_area("브랜딩 계획 설명", st.session_state.data.get('branding_details', ''))
        st.form_submit_button("저장")

def staff_management():
    st.header("인력 관리")
    with st.form("staff_management"):
        st.session_state.data['expected_staff'] = st.text_input("행사 당일 필요한 예상 인력 수", st.session_state.data.get('expected_staff', ''))
        st.session_state.data['external_staff_needed'] = st.multiselect("외부에서 고용할 필요가 있는 인력", ["행사 진행 요원", "보안 요원", "기술 지원 인력", "MC 또는 사회자", "공연자 또는 연사", "촬영 및 영상 제작 팀", "기타"], default=st.session_state.data.get('external_staff_needed', []))
        if "공연자 또는 연사" in st.session_state.data['external_staff_needed']:
            st.session_state.data['performer_details'] = st.text_area("공연자 또는 연사에 대한 추가 정보", st.session_state.data.get('performer_details', ''))
        st.form_submit_button("저장")

def technology_and_equipment():
    st.header("기술 및 장비")
    with st.form("technology_and_equipment"):
        st.session_state.data['tech_requirements'] = st.multiselect("필요한 기술적 요구사항", ["와이파이 네트워크", "라이브 스트리밍 장비", "촬영 장비", "행사 관리 소프트웨어", "모바일 앱", "VR/AR 기술", "기타"], default=st.session_state.data.get('tech_requirements', []))
        st.session_state.data['tech_details'] = st.text_area("기술적 요구사항 세부 설명", st.session_state.data.get('tech_details', ''))
        
        if "기타" in st.session_state.data['tech_requirements']:
            st.session_state.data['other_tech_requirements'] = st.text_input("기타 기술적 요구사항", st.session_state.data.get('other_tech_requirements', ''))
        
        st.session_state.data['equipment_rental_needed'] = st.checkbox("장비 대여 필요", st.session_state.data.get('equipment_rental_needed', False))
        if st.session_state.data['equipment_rental_needed']:
            st.session_state.data['equipment_rental_list'] = st.text_area("대여 필요 장비 목록", st.session_state.data.get('equipment_rental_list', ''))
        
        st.form_submit_button("저장")

def networking():
    st.header("네트워킹")
    with st.form("networking"):
        st.session_state.data['networking_needed'] = st.checkbox("네트워킹 필요 여부", st.session_state.data.get('networking_needed', False))
        if st.session_state.data['networking_needed']:
            st.session_state.data['networking_place_type'] = st.radio("네트워킹 장소 유형", ["실내", "야외", "기타"], index=["실내", "야외", "기타"].index(st.session_state.data.get('networking_place_type', '실내')))
            st.session_state.data['networking_people_count'] = st.number_input("네트워킹 예상 인원 수", min_value=1, value=st.session_state.data.get('networking_people_count', 1))
            st.session_state.data['networking_equipment'] = st.multiselect("네트워킹에 필요한 장비", ["테이블", "의자", "음향 장비", "조명", "기타"], default=st.session_state.data.get('networking_equipment', []))
            st.session_state.data['networking_activities'] = st.text_area("계획된 네트워킹 활동", st.session_state.data.get('networking_activities', ''))
        st.form_submit_button("저장")

def budget_and_sponsorship():
    st.header("예산 및 스폰서십")
    with st.form("budget_and_sponsorship"):
        st.session_state.data['total_budget'] = st.text_input("총 예산", st.session_state.data.get('total_budget', ''))
        st.session_state.data['budget_breakdown'] = st.text_area("예산 항목별 내역", st.session_state.data.get('budget_breakdown', ''))
        st.session_state.data['sponsorship_status'] = st.radio("스폰서 유치 계획 상태", ["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"], index=["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"].index(st.session_state.data.get('sponsorship_status', '협의 중')))
        if st.session_state.data['sponsorship_status'] in ["확정됨", "거의 확정됨", "협의 중"]:
            st.session_state.data['sponsorship_types'] = st.multiselect("고려 중인 스폰서십 유형", ["금전적 후원", "현물 협찬", "미디어 파트너십", "기술 파트너십", "기타"], default=st.session_state.data.get('sponsorship_types', []))
            st.session_state.data['sponsorship_details'] = st.text_area("스폰서십 세부 사항", st.session_state.data.get('sponsorship_details', ''))
        st.form_submit_button("저장")

def risk_management():
    st.header("리스크 관리")
    with st.form("risk_management"):
        st.session_state.data['potential_risks'] = st.multiselect("우려되는 잠재적 리스크", ["날씨 (야외 행사의 경우)", "예산 초과", "참가자 수 미달", "기술적 문제", "안전 및 보안 문제", "기타"], default=st.session_state.data.get('potential_risks', []))
        st.session_state.data['risk_preparation_status'] = st.radio("리스크 대비책 수립 상태", ["완료", "진행 중", "시작 전", "도움 필요"], index=["완료", "진행 중", "시작 전", "도움 필요"].index(st.session_state.data.get('risk_preparation_status', '진행 중')))
        if st.session_state.data['risk_preparation_status'] in ["완료", "진행 중"]:
            st.session_state.data['risk_preparation_details'] = st.text_area("리스크 대비책 설명", st.session_state.data.get('risk_preparation_details', ''))
        st.session_state.data['insurance_needed'] = st.checkbox("행사 보험 필요 여부", st.session_state.data.get('insurance_needed', False))
        if st.session_state.data['insurance_needed']:
            st.session_state.data['insurance_types'] = st.multiselect("필요한 보험 유형", ["행사 취소 보험", "책임 보험", "재산 보험", "기타"], default=st.session_state.data.get('insurance_types', []))
        st.form_submit_button("저장")

def submit_form():
    st.write("설문이 제출되었습니다.")
    
    # Generate Excel files
    categories = ["무대 설치", "음향 시스템", "조명 장비", "LED 스크린", "동시통역 시스템", "케이터링 서비스", "영상 제작"]
    for category in categories:
        if category in st.session_state.data and (category == "영상 제작" or st.session_state.data[category].get('needed', False)):
            excel_file = generate_excel_file(st.session_state.data, category)
            st.download_button(
                label=f"Download {category} 발주서",
                data=excel_file,
                file_name=f"{category}_발주서_{st.session_state.data['name']}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()
