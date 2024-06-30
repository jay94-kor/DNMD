import streamlit as st
import pandas as pd
from datetime import datetime
import io

# CSS를 사용하여 앱의 스타일을 개선합니다.
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
        font-family: 'Arial', sans-serif;
    }
    .stSidebar {
        background-color: #f1f3f6;
        padding: 2rem;
        border-left: 1px solid #d1d9e6;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    .stSelectbox>div>div>select {
        border-radius: 5px;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

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

def main():
    st.set_page_config(layout="wide")
    st.title("행사 기획 설문")

    # 세션 상태 초기화
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'data' not in st.session_state:
        st.session_state.data = {}

    # 사이드바 (오른쪽)에 네비게이션 배치
    st.sidebar.title("진행 상황")
    steps = ["기본 정보", "행사 개요", "행사 형태 및 장소", "행사 구성 요소", "마무리"]
    for i, step in enumerate(steps, 1):
        if st.sidebar.button(f"{i}. {step}", key=f"nav_{i}"):
            if validate_current_step():
                st.session_state.step = i
            else:
                st.error("현재 단계의 모든 필수 항목을 채워주세요.")

    # 메인 컨텐츠
    if st.session_state.step == 1:
        basic_info()
    elif st.session_state.step == 2:
        event_overview()
    elif st.session_state.step == 3:
        event_format_and_venue()
    elif st.session_state.step == 4:
        event_components()
    elif st.session_state.step == 5:
        finalize()

    # 진행 상황 바
    st.sidebar.progress(st.session_state.step / len(steps))

    # 네비게이션 버튼
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.step > 1:
            if st.button("이전"):
                st.session_state.step -= 1
    with col2:
        if st.session_state.step < len(steps):
            if st.button("다음"):
                if validate_current_step():
                    st.session_state.step += 1
                else:
                    st.error("모든 필수 항목을 채워주세요.")

def validate_current_step():
    if st.session_state.step == 1:
        return all(st.session_state.data.get(field) for field in ['name', 'department', 'position', 'event_types', 'event_name', 'event_start_date', 'event_end_date', 'event_duration'])
    elif st.session_state.step == 2:
        return all(st.session_state.data.get(field) for field in ['event_purpose', 'expected_participants', 'contract_type', 'budget_status'])
    elif st.session_state.step == 3:
        required_fields = ['event_format']
        if st.session_state.data.get('event_format') in ["오프라인 행사", "하이브리드 (온/오프라인 병행)"]:
            required_fields.extend(['venue_type', 'venue_status'])
            if st.session_state.data.get('venue_status') in ["확정됨", "거의 확정됨"]:
                required_fields.append('specific_venue')
            else:
                required_fields.append('expected_area')
        return all(st.session_state.data.get(field) for field in required_fields)
    elif st.session_state.step == 4:
        # 행사 구성 요소의 필수 항목은 각 구성 요소 함수에서 개별적으로 처리
        return True
    return True

def basic_info():
    st.header("기본 정보")
    st.session_state.data['name'] = st.text_input("이름", st.session_state.data.get('name', ''))
    st.session_state.data['department'] = st.text_input("근무 부서", st.session_state.data.get('department', ''))
    position_options = ["파트너 기획자", "선임", "책임", "수석"]
    current_position = st.session_state.data.get('position', '파트너 기획자')
    position_index = position_options.index(current_position) if current_position in position_options else 0
    st.session_state.data['position'] = st.radio("직급", position_options, index=position_index)
    st.session_state.data['event_types'] = st.multiselect("주로 기획하는 행사 유형", ["콘서트", "컨퍼런스", "전시회", "축제", "기업 행사", "기타"], default=st.session_state.data.get('event_types', []))
    st.session_state.data['event_name'] = st.text_input("용역명", st.session_state.data.get('event_name', ''))
    st.session_state.data['event_start_date'] = st.date_input("행사 시작일", value=st.session_state.data.get('event_start_date', datetime.now().date()))
    st.session_state.data['event_end_date'] = st.date_input("행사 마감일", value=st.session_state.data.get('event_end_date', datetime.now().date()))
    st.session_state.data['event_duration'] = st.text_input("진행 일정 (일 수)", st.session_state.data.get('event_duration', ''))
    st.session_state.data['setup_start_time'] = st.time_input("셋업 시작 시간", value=st.session_state.data.get('setup_start_time', datetime.now().time()))
    st.session_state.data['rehearsal_start_time'] = st.time_input("리허설 시작 시간", value=st.session_state.data.get('rehearsal_start_time', datetime.now().time()))
    st.session_state.data['rehearsal_end_time'] = st.time_input("리허설 마감 시간", value=st.session_state.data.get('rehearsal_end_time', datetime.now().time()))
    st.session_state.data['event_start_time'] = st.time_input("행사 시작 시간", value=st.session_state.data.get('event_start_time', datetime.now().time()))
    st.session_state.data['event_end_time'] = st.time_input("행사 마감 시간", value=st.session_state.data.get('event_end_time', datetime.now().time()))
    st.session_state.data['teardown_end_time'] = st.time_input("철수 마무리 시간", value=st.session_state.data.get('teardown_end_time', datetime.now().time()))

def event_overview():
    st.header("행사 개요")
    st.session_state.data['event_purpose'] = st.multiselect("용역의 주요 목적은 무엇인가요?", 
                                       ["브랜드 인지도 향상", "고객 관계 강화", "신제품 출시", "교육 및 정보 제공", 
                                        "수익 창출", "문화/예술 증진", "기타"], 
                                       default=st.session_state.data.get('event_purpose', []))
    st.session_state.data['expected_participants'] = st.text_input("예상 참가자 수", st.session_state.data.get('expected_participants', ''))
    st.session_state.data['contract_type'] = st.radio("계약 형태", ["수의계약", "입찰", "B2B"], index=["수의계약", "입찰", "B2B"].index(st.session_state.data.get('contract_type', '수의계약')))
    st.session_state.data['budget_status'] = st.radio("예산 협의 상태", ["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"], 
                                                      index=["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"].index(st.session_state.data.get('budget_status', '협의 중')))

def event_format_and_venue():
    st.header("행사 형태 및 장소")
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


def event_components():
    st.header("행사 구성 요소")
    
    components = {
        "무대 설치": setup_stage,
        "음향 시스템": setup_sound,
        "조명 장비": setup_lighting,
        "LED 스크린": setup_led,
        "동시통역 시스템": setup_interpretation,
        "케이터링 서비스": setup_catering,
        "영상 제작": video_production,
        "마케팅 및 홍보": marketing_and_promotion,
        "인력 관리": staff_management,
        "기술 및 장비": technology_and_equipment,
        "네트워킹": networking,
        "예산 및 스폰서십": budget_and_sponsorship,
        "리스크 관리": risk_management
    }
    
    for component, setup_func in components.items():
        with st.expander(f"{component}"):
            setup_func()

def setup_stage():
    st.session_state.data['무대 설치'] = st.session_state.data.get('무대 설치', {})
    st.session_state.data['무대 설치']['needed'] = st.checkbox("무대 설치 필요", st.session_state.data['무대 설치'].get('needed', False))
    if st.session_state.data['무대 설치']['needed']:
        st.session_state.data['무대 설치']['plan_status'] = st.radio("계획 상태", ["확정됨", "거의 확정됨", "정하는 중", "모름"], key="무대_설치_status")
        if st.session_state.data['무대 설치']['plan_status'] in ["확정됨", "거의 확정됨"]:
            st.session_state.data['무대 설치']['stage_size'] = st.text_input("무대 크기", st.session_state.data['무대 설치'].get('stage_size', ''))
        else:
            st.session_state.data['무대 설치']['expected_stage_size'] = st.text_input("예상 무대 크기", st.session_state.data['무대 설치'].get('expected_stage_size', ''))
            st.session_state.data['무대 설치']['stage_features'] = st.multiselect("무대에 필요한 기능", ["발표/연설", "음악 공연", "댄스 퍼포먼스", "연극", "기타"], default=st.session_state.data['무대 설치'].get('stage_features', []))

def setup_sound():
    st.session_state.data['음향 시스템'] = st.session_state.data.get('음향 시스템', {})
    st.session_state.data['음향 시스템']['needed'] = st.checkbox("음향 시스템 필요", st.session_state.data['음향 시스템'].get('needed', False))
    if st.session_state.data['음향 시스템']['needed']:
        st.session_state.data['음향 시스템']['plan_status'] = st.radio("계획 상태", ["확정됨", "거의 확정됨", "정하는 중", "모름"], key="음향_시스템_status")
        if st.session_state.data['음향 시스템']['plan_status'] in ["확정됨", "거의 확정됨"]:
            st.session_state.data['음향 시스템']['required_mic_count'] = st.number_input("필요한 마이크 개수", min_value=1, value=st.session_state.data['음향 시스템'].get('required_mic_count', 1))
        else:
            st.session_state.data['음향 시스템']['expected_sound_equipment'] = st.multiselect("예상 음향 장비", ["마이크", "스피커", "믹서", "기타"], default=st.session_state.data['음향 시스템'].get('expected_sound_equipment', []))

def setup_lighting():
    st.session_state.data['조명 장비'] = st.session_state.data.get('조명 장비', {})
    st.session_state.data['조명 장비']['needed'] = st.checkbox("조명 장비 필요", st.session_state.data['조명 장비'].get('needed', False))
    if st.session_state.data['조명 장비']['needed']:
        st.session_state.data['조명 장비']['plan_status'] = st.radio("계획 상태", ["확정됨", "거의 확정됨", "정하는 중", "모름"], key="조명_장비_status")
        if st.session_state.data['조명 장비']['plan_status'] in ["확정됨", "거의 확정됨"]:
            st.session_state.data['조명 장비']['special_light_effect'] = st.checkbox("특수 조명 효과 필요 여부", st.session_state.data['조명 장비'].get('special_light_effect', False))
        else:
            st.session_state.data['조명 장비']['expected_light_equipment'] = st.multiselect("예상 조명 장비", ["일반 조명", "무대 조명", "특수 조명", "기타"], default=st.session_state.data['조명 장비'].get('expected_light_equipment', []))

def setup_led():
    st.session_state.data['LED 스크린'] = st.session_state.data.get('LED 스크린', {})
    st.session_state.data['LED 스크린']['needed'] = st.checkbox("LED 스크린 필요", st.session_state.data['LED 스크린'].get('needed', False))
    if st.session_state.data['LED 스크린']['needed']:
        st.session_state.data['LED 스크린']['plan_status'] = st.radio("계획 상태", ["확정됨", "거의 확정됨", "정하는 중", "모름"], key="LED_스크린_status")
        if st.session_state.data['LED 스크린']['plan_status'] in ["확정됨", "거의 확정됨"]:
            st.session_state.data['LED 스크린']['led_screen_size'] = st.text_input("LED 스크린 크기", st.session_state.data['LED 스크린'].get('led_screen_size', ''))
            st.session_state.data['LED 스크린']['led_screen_purpose'] = st.multiselect("스크린 사용 목적", ["프레젠테이션 표시", "라이브 중계", "배경 그래픽", "기타"], default=st.session_state.data['LED 스크린'].get('led_screen_purpose', []))
        else:
            st.session_state.data['LED 스크린']['expected_led_screen_size'] = st.text_input("예상 LED 스크린 크기", st.session_state.data['LED 스크린'].get('expected_led_screen_size', ''))

def setup_interpretation():
    st.session_state.data['동시통역 시스템'] = st.session_state.data.get('동시통역 시스템', {})
    st.session_state.data['동시통역 시스템']['needed'] = st.checkbox("동시통역 시스템 필요", st.session_state.data['동시통역 시스템'].get('needed', False))
    if st.session_state.data['동시통역 시스템']['needed']:
        st.session_state.data['동시통역 시스템']['plan_status'] = st.radio("계획 상태", ["확정됨", "거의 확정됨", "정하는 중", "모름"], key="동시통역_시스템_status")
        if st.session_state.data['동시통역 시스템']['plan_status'] in ["확정됨", "거의 확정됨"]:
            st.session_state.data['동시통역 시스템']['required_languages'] = st.multiselect("필요한 언어", ["영어", "중국어", "일본어", "기타"], default=st.session_state.data['동시통역 시스템'].get('required_languages', []))
            st.session_state.data['동시통역 시스템']['need_interpreter'] = st.checkbox("통역사 필요 여부", st.session_state.data['동시통역 시스템'].get('need_interpreter', False))
        else:
            st.session_state.data['동시통역 시스템']['expected_languages'] = st.multiselect("예상 통역 언어", ["영어", "중국어", "일본어", "기타"], default=st.session_state.data['동시통역 시스템'].get('expected_languages', []))

def setup_catering():
    st.session_state.data['케이터링 서비스'] = st.session_state.data.get('케이터링 서비스', {})
    st.session_state.data['케이터링 서비스']['needed'] = st.checkbox("케이터링 서비스 필요", st.session_state.data['케이터링 서비스'].get('needed', False))
    if st.session_state.data['케이터링 서비스']['needed']:
        st.session_state.data['케이터링 서비스']['plan_status'] = st.radio("계획 상태", ["확정됨", "거의 확정됨", "정하는 중", "모름"], key="케이터링_서비스_status")
        if st.session_state.data['케이터링 서비스']['plan_status'] in ["확정됨", "거의 확정됨"]:
            st.session_state.data['케이터링 서비스']['meal_type'] = st.radio("식사 유형", ["뷔페", "플레이티드 서비스", "칵테일 리셉션", "기타"], index=["뷔페", "플레이티드 서비스", "칵테일 리셉션", "기타"].index(st.session_state.data['케이터링 서비스'].get('meal_type', '뷔페')))
            st.session_state.data['케이터링 서비스']['special_diet_requirements'] = st.text_input("특별 식단 요구사항", st.session_state.data['케이터링 서비스'].get('special_diet_requirements', ''))
        else:
            st.session_state.data['케이터링 서비스']['expected_meal_type'] = st.radio("예상 식사 유형", ["뷔페", "플레이티드 서비스", "칵테일 리셉션", "기타"], index=["뷔페", "플레이티드 서비스", "칵테일 리셉션", "기타"].index(st.session_state.data['케이터링 서비스'].get('expected_meal_type', '뷔페')))
            st.session_state.data['케이터링 서비스']['expected_meal_count'] = st.number_input("예상 인원 수", min_value=1, value=st.session_state.data['케이터링 서비스'].get('expected_meal_count', 1))

def video_production():
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

def marketing_and_promotion():
    st.session_state.data['마케팅 및 홍보'] = st.session_state.data.get('마케팅 및 홍보', {})
    st.session_state.data['마케팅 및 홍보']['promo_channels'] = st.multiselect("사용할 홍보 채널", ["소셜 미디어", "이메일 마케팅", "언론 보도", "온라인 광고", "오프라인 광고 (현수막, 포스터 등)", "인플루언서 마케팅", "기타"], default=st.session_state.data['마케팅 및 홍보'].get('promo_channels', []))
    st.session_state.data['마케팅 및 홍보']['branding_status'] = st.radio("행사 브랜딩 계획 상태", ["확정됨", "거의 확정됨", "기획 중", "아직 시작 못함"], index=["확정됨", "거의 확정됨", "기획 중", "아직 시작 못함"].index(st.session_state.data['마케팅 및 홍보'].get('branding_status', '기획 중')))
    if st.session_state.data['마케팅 및 홍보']['branding_status'] in ["확정됨", "거의 확정됨", "기획 중"]:
        st.session_state.data['마케팅 및 홍보']['branding_details'] = st.text_area("브랜딩 계획 설명", st.session_state.data['마케팅 및 홍보'].get('branding_details', ''))

def staff_management():
    st.session_state.data['인력 관리'] = st.session_state.data.get('인력 관리', {})
    st.session_state.data['인력 관리']['expected_staff'] = st.text_input("행사 당일 필요한 예상 인력 수", st.session_state.data['인력 관리'].get('expected_staff', ''))
    st.session_state.data['인력 관리']['external_staff_needed'] = st.multiselect("외부에서 고용할 필요가 있는 인력", ["행사 진행 요원", "보안 요원", "기술 지원 인력", "MC 또는 사회자", "공연자 또는 연사", "촬영 및 영상 제작 팀", "기타"], default=st.session_state.data['인력 관리'].get('external_staff_needed', []))
    if "공연자 또는 연사" in st.session_state.data['인력 관리']['external_staff_needed']:
        st.session_state.data['인력 관리']['performer_details'] = st.text_area("공연자 또는 연사에 대한 추가 정보", st.session_state.data['인력 관리'].get('performer_details', ''))

def technology_and_equipment():
    st.session_state.data['기술 및 장비'] = st.session_state.data.get('기술 및 장비', {})
    st.session_state.data['기술 및 장비']['tech_requirements'] = st.multiselect("필요한 기술적 요구사항", ["와이파이 네트워크", "라이브 스트리밍 장비", "촬영 장비", "행사 관리 소프트웨어", "모바일 앱", "VR/AR 기술", "기타"], default=st.session_state.data['기술 및 장비'].get('tech_requirements', []))
    st.session_state.data['기술 및 장비']['tech_details'] = st.text_area("기술적 요구사항 세부 설명", st.session_state.data['기술 및 장비'].get('tech_details', ''))
    
    if "기타" in st.session_state.data['기술 및 장비']['tech_requirements']:
        st.session_state.data['기술 및 장비']['other_tech_requirements'] = st.text_input("기타 기술적 요구사항", st.session_state.data['기술 및 장비'].get('other_tech_requirements', ''))
    
    st.session_state.data['기술 및 장비']['equipment_rental_needed'] = st.checkbox("장비 대여 필요", st.session_state.data['기술 및 장비'].get('equipment_rental_needed', False))
    if st.session_state.data['기술 및 장비']['equipment_rental_needed']:
        st.session_state.data['기술 및 장비']['equipment_rental_list'] = st.text_area("대여 필요 장비 목록", st.session_state.data['기술 및 장비'].get('equipment_rental_list', ''))

def networking():
    st.session_state.data['네트워킹'] = st.session_state.data.get('네트워킹', {})
    st.session_state.data['네트워킹']['networking_needed'] = st.checkbox("네트워킹 필요 여부", st.session_state.data['네트워킹'].get('networking_needed', False))
    if st.session_state.data['네트워킹']['networking_needed']:
        st.session_state.data['네트워킹']['networking_place_type'] = st.radio("네트워킹 장소 유형", ["실내", "야외", "기타"], index=["실내", "야외", "기타"].index(st.session_state.data['네트워킹'].get('networking_place_type', '실내')))
        st.session_state.data['네트워킹']['networking_people_count'] = st.number_input("네트워킹 예상 인원 수", min_value=1, value=st.session_state.data['네트워킹'].get('networking_people_count', 1))
        st.session_state.data['네트워킹']['networking_equipment'] = st.multiselect("네트워킹에 필요한 장비", ["테이블", "의자", "음향 장비", "조명", "기타"], default=st.session_state.data['네트워킹'].get('networking_equipment', []))
        st.session_state.data['네트워킹']['networking_activities'] = st.text_area("계획된 네트워킹 활동", st.session_state.data['네트워킹'].get('networking_activities', ''))

def budget_and_sponsorship():
    st.session_state.data['예산 및 스폰서십'] = st.session_state.data.get('예산 및 스폰서십', {})
    st.session_state.data['예산 및 스폰서십']['total_budget'] = st.text_input("총 예산", st.session_state.data['예산 및 스폰서십'].get('total_budget', ''))
    st.session_state.data['예산 및 스폰서십']['budget_breakdown'] = st.text_area("예산 항목별 내역", st.session_state.data['예산 및 스폰서십'].get('budget_breakdown', ''))
    st.session_state.data['예산 및 스폰서십']['sponsorship_status'] = st.radio("스폰서 유치 계획 상태", ["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"], index=["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"].index(st.session_state.data['예산 및 스폰서십'].get('sponsorship_status', '협의 중')))
    if st.session_state.data['예산 및 스폰서십']['sponsorship_status'] in ["확정됨", "거의 확정됨", "협의 중"]:
        st.session_state.data['예산 및 스폰서십']['sponsorship_types'] = st.multiselect("고려 중인 스폰서십 유형", ["금전적 후원", "현물 협찬", "미디어 파트너십", "기술 파트너십", "기타"], default=st.session_state.data['예산 및 스폰서십'].get('sponsorship_types', []))
        st.session_state.data['예산 및 스폰서십']['sponsorship_details'] = st.text_area("스폰서십 세부 사항", st.session_state.data['예산 및 스폰서십'].get('sponsorship_details', ''))

def risk_management():
    st.session_state.data['리스크 관리'] = st.session_state.data.get('리스크 관리', {})
    st.session_state.data['리스크 관리']['potential_risks'] = st.multiselect("우려되는 잠재적 리스크", ["날씨 (야외 행사의 경우)", "예산 초과", "참가자 수 미달", "기술적 문제", "안전 및 보안 문제", "기타"], default=st.session_state.data['리스크 관리'].get('potential_risks', []))
    st.session_state.data['리스크 관리']['risk_preparation_status'] = st.radio("리스크 대비책 수립 상태", ["완료", "진행 중", "시작 전", "도움 필요"], index=["완료", "진행 중", "시작 전", "도움 필요"].index(st.session_state.data['리스크 관리'].get('risk_preparation_status', '진행 중')))
    if st.session_state.data['리스크 관리']['risk_preparation_status'] in ["완료", "진행 중"]:
        st.session_state.data['리스크 관리']['risk_preparation_details'] = st.text_area("리스크 대비책 설명", st.session_state.data['리스크 관리'].get('risk_preparation_details', ''))
    st.session_state.data['리스크 관리']['insurance_needed'] = st.checkbox("행사 보험 필요 여부", st.session_state.data['리스크 관리'].get('insurance_needed', False))
    if st.session_state.data['리스크 관리']['insurance_needed']:
        st.session_state.data['리스크 관리']['insurance_types'] = st.multiselect("필요한 보험 유형", ["행사 취소 보험", "책임 보험", "재산 보험", "기타"], default=st.session_state.data['리스크 관리'].get('insurance_types', []))

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

def save_survey_data(data):
    # 여기에 데이터를 저장하는 로직을 구현합니다.
    # 예: 데이터베이스에 저장, 파일로 저장 등
    pass

if __name__ == "__main__":
    main()
