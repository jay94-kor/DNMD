import streamlit as st
import pandas as pd
from datetime import datetime

def generate_order_request(data, category):
    filename = f"{category}_발주요청서_{data['name']}.txt"
    with open(filename, 'w') as f:
        f.write(f"발주 요청서\n")
        f.write(f"이름: {data['name']}\n")
        f.write(f"근무 부서: {data['department']}\n")
        f.write(f"직급: {data['position']}\n")
        f.write(f"주로 기획하는 행사 유형: {', '.join(data['event_types'])}\n")
        f.write(f"용역명: {data['event_name']}\n")
        f.write(f"행사 시작일: {data['event_start_date']}\n")
        f.write(f"행사 마감일: {data['event_end_date']}\n")
        if 'fast_start_date' in data:
            f.write(f"빠른 시작일: {data['fast_start_date']}\n")
            f.write(f"늦은 마감일: {data['late_end_date']}\n")
        f.write(f"진행 일정 (일 수): {data['event_duration']}\n")
        f.write(f"셋업 시작 시간: {data['setup_start_time']}\n")
        f.write(f"리허설 시작 시간: {data['rehearsal_start_time']}\n")
        f.write(f"리허설 마감 시간: {data['rehearsal_end_time']}\n")
        f.write(f"행사 시작 시간: {data['event_start_time']}\n")
        f.write(f"행사 마감 시간: {data['event_end_time']}\n")
        f.write(f"철수 마무리 시간: {data['teardown_end_time']}\n")
        if 'approximate_keyword' in data:
            f.write(f"예정: {data['approximate_keyword']}\n")
        if category == '무대 설치':
            if 'stage_plan_status' in data:
                f.write(f"\n무대 설치 계획 상태: {data['stage_plan_status']}\n")
                if data['stage_plan_status'] in ["확정됨", "거의 확정됨"]:
                    f.write(f"무대 크기: {data['stage_size']}\n")
                    f.write(f"무대 디자인 요구사항: {data['stage_design_requirements']}\n")
                else:
                    f.write(f"예상 무대 크기: {data['expected_stage_size']}\n")
                    f.write(f"무대에 필요한 기능: {', '.join(data['stage_features'])}\n")
            if 'preferred_stage_vendor' in data and data['preferred_stage_vendor']:
                f.write(f"선호하는 무대 설치 업체명: {data['stage_vendor_name']}\n")
                f.write(f"선호하는 이유: {', '.join(data['stage_vendor_reason'])}\n")
                if 'stage_vendor_reason_detail' in data:
                    f.write(f"기타 이유: {data['stage_vendor_reason_detail']}\n")
        # Add other categories here similarly
        if category == '음향 시스템':
            if 'sound_plan_status' in data:
                f.write(f"\n음향 시스템 계획 상태: {data['sound_plan_status']}\n")
                if data['sound_plan_status'] in ["확정됨", "거의 확정됨"]:
                    f.write(f"필요한 마이크 개수: {data['required_mic_count']}\n")
                    f.write(f"특별한 음향 요구사항: {data['special_sound_requirements']}\n")
                else:
                    f.write(f"예상 음향 장비: {', '.join(data['expected_sound_equipment'])}\n")
            if 'preferred_sound_vendor' in data and data['preferred_sound_vendor']:
                f.write(f"선호하는 음향 시스템 업체명: {data['sound_vendor_name']}\n")
                f.write(f"선호하는 이유: {', '.join(data['sound_vendor_reason'])}\n")
                if 'sound_vendor_reason_detail' in data:
                    f.write(f"기타 이유: {data['sound_vendor_reason_detail']}\n")
        if category == '조명 장비':
            if 'light_plan_status' in data:
                f.write(f"\n조명 장비 계획 상태: {data['light_plan_status']}\n")
                if data['light_plan_status'] in ["확정됨", "거의 확정됨"]:
                    if data.get('special_light_effect'):
                        f.write(f"특수 조명 효과 필요: 예\n")
                    f.write(f"조명 요구사항: {data['light_requirements']}\n")
                else:
                    f.write(f"예상 조명 장비: {', '.join(data['expected_light_equipment'])}\n")
            if 'preferred_light_vendor' in data and data['preferred_light_vendor']:
                f.write(f"선호하는 조명 장비 업체명: {data['light_vendor_name']}\n")
                f.write(f"선호하는 이유: {', '.join(data['light_vendor_reason'])}\n")
                if 'light_vendor_reason_detail' in data:
                    f.write(f"기타 이유: {data['light_vendor_reason_detail']}\n")
        if category == 'LED 스크린':
            if 'led_plan_status' in data:
                f.write(f"\nLED 스크린 계획 상태: {data['led_plan_status']}\n")
                if data['led_plan_status'] in ["확정됨", "거의 확정됨"]:
                    f.write(f"LED 스크린 크기: {data['led_screen_size']}\n")
                    f.write(f"스크린 사용 목적: {', '.join(data['led_screen_purpose'])}\n")
                else:
                    f.write(f"예상 LED 스크린 크기: {data['expected_led_screen_size']}\n")
                    f.write(f"스크린에 필요한 기능: {', '.join(data['led_screen_features'])}\n")
            if 'preferred_led_vendor' in data and data['preferred_led_vendor']:
                f.write(f"선호하는 LED 스크린 업체명: {data['led_vendor_name']}\n")
                f.write(f"선호하는 이유: {', '.join(data['led_vendor_reason'])}\n")
                if 'led_vendor_reason_detail' in data:
                    f.write(f"기타 이유: {data['led_vendor_reason_detail']}\n")
        if category == '동시통역 시스템':
            if 'interpretation_plan_status' in data:
                f.write(f"\n동시통역 시스템 계획 상태: {data['interpretation_plan_status']}\n")
                if data['interpretation_plan_status'] in ["확정됨", "거의 확정됨"]:
                    f.write(f"필요한 언어: {', '.join(data['required_languages'])}\n")
                    if data.get('need_interpreter'):
                        f.write(f"통역사 필요 여부: 예\n")
                else:
                    f.write(f"예상 통역 언어: {', '.join(data['expected_languages'])}\n")
            if 'preferred_interpretation_vendor' in data and data['preferred_interpretation_vendor']:
                f.write(f"선호하는 동시통역 시스템 업체명: {data['interpretation_vendor_name']}\n")
                f.write(f"선호하는 이유: {', '.join(data['interpretation_vendor_reason'])}\n")
                if 'interpretation_vendor_reason_detail' in data:
                    f.write(f"기타 이유: {data['interpretation_vendor_reason_detail']}\n")
        if category == '케이터링 서비스':
            if 'catering_plan_status' in data:
                f.write(f"\n케이터링 서비스 계획 상태: {data['catering_plan_status']}\n")
                if data['catering_plan_status'] in ["확정됨", "거의 확정됨"]:
                    f.write(f"식사 유형: {data['meal_type']}\n")
                    f.write(f"특별 식단 요구사항: {data['special_diet_requirements']}\n")
                else:
                    f.write(f"예상 식사 유형: {data['expected_meal_type']}\n")
                    f.write(f"예상 인원 수: {data['expected_meal_count']}\n")
            if 'preferred_catering_vendor' in data and data['preferred_catering_vendor']:
                f.write(f"선호하는 케이터링 서비스 업체명: {data['catering_vendor_name']}\n")
                f.write(f"선호하는 이유: {', '.join(data['catering_vendor_reason'])}\n")
                if 'catering_vendor_reason_detail' in data:
                    f.write(f"기타 이유: {data['catering_vendor_reason_detail']}\n")
    return filename

st.title("행사 기획 설문")

data = {}

# Step 1: 기본 정보
with st.form("step_1"):
    st.header("기본 정보")
    data['name'] = st.text_input("이름")
    data['department'] = st.text_input("근무 부서")
    data['position'] = st.radio("직급", ["파트너 기획자", "선임", "책임", "수석"])
    data['event_types'] = st.multiselect("주로 기획하는 행사 유형", ["콘서트", "컨퍼런스", "전시회", "축제", "기업 행사", "기타"])
    data['event_name'] = st.text_input("용역명")
    data['event_start_date'] = st.date_input("행사 시작일")
    data['event_end_date'] = st.date_input("행사 마감일")
    if st.checkbox("시작일/마감일이 정해지지 않았다면:"):
        data['fast_start_date'] = st.date_input("빠른 시작일")
        data['late_end_date'] = st.date_input("늦은 마감일")
    data['event_duration'] = st.text_input("진행 일정 (일 수)")
    data['setup_start_time'] = st.time_input("셋업 시작 시간")
    data['rehearsal_start_time'] = st.time_input("리허설 시작 시간")
    data['rehearsal_end_time'] = st.time_input("리허설 마감 시간")
    data['event_start_time'] = st.time_input("행사 시작 시간")
    data['event_end_time'] = st.time_input("행사 마감 시간")
    data['teardown_end_time'] = st.time_input("철수 마무리 시간")
    if st.checkbox("정확하지 않으면 (예정) 키워드 추가"):
        data['approximate_keyword'] = "예정"

    st.form_submit_button("다음 단계")

# Step 2: 행사 개요
with st.form("step_2"):
    st.header("행사 개요")
    data['event_purpose'] = st.multiselect("용역의 주요 목적은 무엇인가요?", 
                                           ["브랜드 인지도 향상", "고객 관계 강화", "신제품 출시", "교육 및 정보 제공", 
                                            "수익 창출", "문화/예술 증진", "기타"])
    data['expected_participants'] = st.text_input("예상 참가자 수")
    data['contract_type'] = st.radio("계약 형태", ["수의계약", "입찰", "B2B"])
    data['budget_status'] = st.radio("예산 협의 상태", ["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"])

    st.form_submit_button("다음 단계")

# Step 3: 행사 형태 및 장소
with st.form("step_3"):
    st.header("행사 형태 및 장소")
    data['event_format'] = st.radio("행사 형태", ["오프라인 행사", "온라인 행사 (라이브 스트리밍)", "하이브리드 (온/오프라인 병행)", "영상 콘텐츠 제작", "기타"])
    
    if data['event_format'] in ["오프라인 행사", "하이브리드 (온/오프라인 병행)"]:
        data['venue_type'] = st.radio("행사 장소 유형", ["실내 (호텔, 컨벤션 센터 등)", "야외 (공원, 광장 등)", "혼합형 (실내+야외)", "아직 미정"])
        data['venue_status'] = st.radio("행사 장소 협의 상태", ["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"])
        
        if data['venue_status'] in ["확정됨", "거의 확정됨"]:
            data['specific_venue'] = st.text_input("구체적인 장소")
        else:
            data['expected_area'] = st.text_input("예정 지역")

    st.form_submit_button("다음 단계")

# Step 4: 행사 구성 요소 및 필요 업체 선택
with st.form("step_4"):
    st.header("행사 구성 요소 및 필요 업체 선택")
    data['stage_setup'] = st.checkbox("무대 설치 업체")
    if data['stage_setup']:
        data['stage_plan_status'] = st.radio("계획 상태", ["확정됨", "거의 확정됨", "정하는 중", "모름"])
        if data['stage_plan_status'] in ["확정됨", "거의 확정됨"]:
            data['stage_size'] = st.text_input("무대 크기")
            data['stage_design_requirements'] = st.text_input("무대 디자인 요구사항")
        else:
            data['expected_stage_size'] = st.text_input("예상 무대 크기")
            data['stage_features'] = st.multiselect("무대에 필요한 기능", ["발표/연설", "음악 공연", "댄스 퍼포먼스", "연극", "기타"])
        
        data['preferred_stage_vendor'] = st.checkbox("선호하는 무대 설치 업체가 있습니까?")
        if data['preferred_stage_vendor']:
            data['stage_vendor_name'] = st.text_input("선호하는 무대 설치 업체명")
            data['stage_vendor_reason'] = st.multiselect("선호하는 이유", ["합리적인 견적", "제안서 도움", "퀄리티 보장", "기타 이유"])
            if "기타 이유" in data['stage_vendor_reason']:
                data['stage_vendor_reason_detail'] = st.text_input("기타 이유")

    data['sound_system'] = st.checkbox("음향 시스템 업체")
    if data['sound_system']:
        data['sound_plan_status'] = st.radio("계획 상태", ["확정됨", "거의 확정됨", "정하는 중", "모름"])
        if data['sound_plan_status'] in ["확정됨", "거의 확정됨"]:
            data['required_mic_count'] = st.number_input("필요한 마이크 개수", min_value=1)
            data['special_sound_requirements'] = st.text_input("특별한 음향 요구사항")
        else:
            data['expected_sound_equipment'] = st.multiselect("예상 음향 장비", ["마이크", "스피커", "믹서", "기타"])
        
        data['preferred_sound_vendor'] = st.checkbox("선호하는 음향 시스템 업체가 있습니까?")
        if data['preferred_sound_vendor']:
            data['sound_vendor_name'] = st.text_input("선호하는 음향 시스템 업체명")
            data['sound_vendor_reason'] = st.multiselect("선호하는 이유", ["합리적인 견적", "제안서 도움", "퀄리티 보장", "기타 이유"])
            if "기타 이유" in data['sound_vendor_reason']:
                data['sound_vendor_reason_detail'] = st.text_input("기타 이유")

    data['lighting'] = st.checkbox("조명 장비 업체")
    if data['lighting']:
        data['light_plan_status'] = st.radio("계획 상태", ["확정됨", "거의 확정됨", "정하는 중", "모름"])
        if data['light_plan_status'] in ["확정됨", "거의 확정됨"]:
            data['special_light_effect'] = st.checkbox("특수 조명 효과 필요 여부")
            data['light_requirements'] = st.text_input("조명 요구사항")
        else:
            data['expected_light_equipment'] = st.multiselect("예상 조명 장비", ["일반 조명", "무대 조명", "특수 조명", "기타"])
        
        data['preferred_light_vendor'] = st.checkbox("선호하는 조명 장비 업체가 있습니까?")
        if data['preferred_light_vendor']:
            data['light_vendor_name'] = st.text_input("선호하는 조명 장비 업체명")
            data['light_vendor_reason'] = st.multiselect("선호하는 이유", ["합리적인 견적", "제안서 도움", "퀄리티 보장", "기타 이유"])
            if "기타 이유" in data['light_vendor_reason']:
                data['light_vendor_reason_detail'] = st.text_input("기타 이유")

    data['led_screen'] = st.checkbox("LED 스크린 업체")
    if data['led_screen']:
        data['led_plan_status'] = st.radio("계획 상태", ["확정됨", "거의 확정됨", "정하는 중", "모름"])
        if data['led_plan_status'] in ["확정됨", "거의 확정됨"]:
            data['led_screen_size'] = st.text_input("LED 스크린 크기")
            data['led_screen_purpose'] = st.multiselect("스크린 사용 목적", ["프레젠테이션 표시", "라이브 중계", "배경 그래픽", "기타"])
        else:
            data['expected_led_screen_size'] = st.text_input("예상 LED 스크린 크기")
            data['led_screen_features'] = st.multiselect("스크린에 필요한 기능", ["프레젠테이션 표시", "라이브 중계", "배경 그래픽", "기타"])
        
        data['preferred_led_vendor'] = st.checkbox("선호하는 LED 스크린 업체가 있습니까?")
        if data['preferred_led_vendor']:
            data['led_vendor_name'] = st.text_input("선호하는 LED 스크린 업체명")
            data['led_vendor_reason'] = st.multiselect("선호하는 이유", ["합리적인 견적", "제안서 도움", "퀄리티 보장", "기타 이유"])
            if "기타 이유" in data['led_vendor_reason']:
                data['led_vendor_reason_detail'] = st.text_input("기타 이유")

    data['interpretation_system'] = st.checkbox("동시통역 시스템 업체")
    if data['interpretation_system']:
        data['interpretation_plan_status'] = st.radio("계획 상태", ["확정됨", "거의 확정됨", "정하는 중", "모름"])
        if data['interpretation_plan_status'] in ["확정됨", "거의 확정됨"]:
            data['required_languages'] = st.multiselect("필요한 언어", ["영어", "중국어", "일본어", "기타"])
            data['need_interpreter'] = st.checkbox("통역사 필요 여부")
        else:
            data['expected_languages'] = st.multiselect("예상 통역 언어", ["영어", "중국어", "일본어", "기타"])
        
        data['preferred_interpretation_vendor'] = st.checkbox("선호하는 동시통역 시스템 업체가 있습니까?")
        if data['preferred_interpretation_vendor']:
            data['interpretation_vendor_name'] = st.text_input("선호하는 동시통역 시스템 업체명")
            data['interpretation_vendor_reason'] = st.multiselect("선호하는 이유", ["합리적인 견적", "제안서 도움", "퀄리티 보장", "기타 이유"])
            if "기타 이유" in data['interpretation_vendor_reason']:
                data['interpretation_vendor_reason_detail'] = st.text_input("기타 이유")

    data['catering_service'] = st.checkbox("케이터링 서비스 업체")
    if data['catering_service']:
        data['catering_plan_status'] = st.radio("계획 상태", ["확정됨", "거의 확정됨", "정하는 중", "모름"])
        if data['catering_plan_status'] in ["확정됨", "거의 확정됨"]:
            data['meal_type'] = st.radio("식사 유형", ["뷔페", "플레이티드 서비스", "칵테일 리셉션", "기타"])
            data['special_diet_requirements'] = st.text_input("특별 식단 요구사항")
        else:
            data['expected_meal_type'] = st.radio("예상 식사 유형", ["뷔페", "플레이티드 서비스", "칵테일 리셉션", "기타"])
            data['expected_meal_count'] = st.number_input("예상 인원 수", min_value=1)
        
        data['preferred_catering_vendor'] = st.checkbox("선호하는 케이터링 서비스 업체가 있습니까?")
        if data['preferred_catering_vendor']:
            data['catering_vendor_name'] = st.text_input("선호하는 케이터링 서비스 업체명")
            data['catering_vendor_reason'] = st.multiselect("선호하는 이유", ["합리적인 견적", "제안서 도움", "퀄리티 보장", "기타 이유"])
            if "기타 이유" in data['catering_vendor_reason']:
                data['catering_vendor_reason_detail'] = st.text_input("기타 이유")

    st.form_submit_button("다음 단계")

# Step 5: 마케팅 및 홍보
with st.form("step_5"):
    st.header("마케팅 및 홍보")
    data['promo_channels'] = st.multiselect("사용할 홍보 채널", ["소셜 미디어", "이메일 마케팅", "언론 보도", "온라인 광고", "오프라인 광고 (현수막, 포스터 등)", "인플루언서 마케팅", "기타"])
    data['branding_status'] = st.radio("행사 브랜딩 계획 상태", ["확정됨", "거의 확정됨", "기획 중", "아직 시작 못함"])
    if data['branding_status'] in ["확정됨", "거의 확정됨", "기획 중"]:
        data['branding_details'] = st.text_area("브랜딩 계획 설명")

    st.form_submit_button("다음 단계")

# Step 6: 인력 관리
with st.form("step_6"):
    st.header("인력 관리")
    data['expected_staff'] = st.text_input("행사 당일 필요한 예상 인력 수")
    data['external_staff_needed'] = st.multiselect("외부에서 고용할 필요가 있는 인력", ["행사 진행 요원", "보안 요원", "기술 지원 인력", "MC 또는 사회자", "공연자 또는 연사", "촬영 및 영상 제작 팀", "기타"])
    if "공연자 또는 연사" in data['external_staff_needed']:
        data['performer_details'] = st.text_area("공연자 또는 연사에 대한 추가 정보")

    st.form_submit_button("다음 단계")

# Step 7: 기술 및 장비
with st.form("step_7"):
    st.header("기술 및 장비")
    data['tech_requirements'] = st.multiselect("필요한 기술적 요구사항", ["와이파이 네트워크", "라이브 스트리밍 장비", "촬영 장비", "행사 관리 소프트웨어", "모바일 앱", "VR/AR 기술", "기타"])
    data['tech_details'] = st.text_area("기술적 요구사항 세부 설명")

    st.form_submit_button("다음 단계")

# Step 8: 네트워킹
with st.form("step_8"):
    st.header("네트워킹")
    data['networking_needed'] = st.checkbox("네트워킹 필요 여부")
    if data['networking_needed']:
        data['networking_place_type'] = st.radio("네트워킹 장소 유형", ["실내", "야외", "기타"])
        data['networking_people_count'] = st.number_input("네트워킹 예상 인원 수", min_value=1)
        data['networking_equipment'] = st.multiselect("네트워킹에 필요한 장비", ["테이블", "의자", "음향 장비", "조명", "기타"])

    st.form_submit_button("다음 단계")

# Step 9: 예산 및 스폰서십
with st.form("step_9"):
    st.header("예산 및 스폰서십")
    data['sponsorship_status'] = st.radio("스폰서 유치 계획 상태", ["확정됨", "거의 확정됨", "협의 중", "아직 협의 못함"])
    if data['sponsorship_status'] in ["확정됨", "거의 확정됨", "협의 중"]:
        data['sponsorship_types'] = st.multiselect("고려 중인 스폰서십 유형", ["금전적 후원", "현물 협찬", "미디어 파트너십", "기술 파트너십", "기타"])

    st.form_submit_button("다음 단계")

# Step 10: 리스크 관리
with st.form("step_10"):
    st.header("리스크 관리")
    data['potential_risks'] = st.multiselect("우려되는 잠재적 리스크", ["날씨 (야외 행사의 경우)", "예산 초과", "참가자 수 미달", "기술적 문제", "안전 및 보안 문제", "기타"])
    data['risk_preparation_status'] = st.radio("리스크 대비책 수립 상태", ["완료", "진행 중", "시작 전", "도움 필요"])
    if data['risk_preparation_status'] in ["완료", "진행 중"]:
        data['risk_preparation_details'] = st.text_area("리스크 대비책 설명")

    st.form_submit_button("제출")

# 마지막 제출 버튼
if st.button("제출"):
    st.write("설문이 제출되었습니다.")
    
    # Generate order requests
    categories = ["무대 설치", "음향 시스템", "조명 장비", "LED 스크린", "동시통역 시스템", "케이터링 서비스"]
    files = []
    for category in categories:
        if category in data:
            filename = generate_order_request(data, category)
            files.append(filename)
    
    for file in files:
        with open(file, "r") as f:
            st.download_button(label=f"Download {file}", data=f.read(), file_name=file, mime='text/plain')
