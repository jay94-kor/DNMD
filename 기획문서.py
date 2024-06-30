import pandas as pd
from io import BytesIO

def create_documentation():
    # 엑셀 파일 생성
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # 1. 프로젝트 개요
        overview = pd.DataFrame({
            '항목': ['프로젝트명', '목적', '주요 기능', '대상 사용자', '개발 언어 및 프레임워크'],
            '내용': [
                '이벤트 기획 도구',
                '이벤트 기획 과정을 체계화하고 효율적으로 관리',
                '단계별 정보 입력, 진행 상황 추적, 발주요청서 자동 생성',
                '이벤트 기획자, 행사 담당자',
                'Python, Streamlit'
            ]
        })
        overview.to_excel(writer, sheet_name='프로젝트 개요', index=False)

        # 2. 앱 구조 및 흐름
        structure = pd.DataFrame({
            '단계': ['기본 정보', '행사 개요', '행사 형태 및 장소', '행사 구성 요소', '마무리'],
            '주요 내용': [
                '이름, 부서, 직급, 행사 유형, 일정',
                '행사 목적, 예상 참가자 수, 계약 형태, 예산 상태',
                '행사 형태, 장소 유형 및 상태',
                '무대, 음향, 조명, 케이터링 등 세부 요소',
                '설문 저장 및 발주요청서 생성'
            ],
            '관련 함수': [
                'display_basic_info(), improved_schedule_input()',
                'display_event_overview()',
                'display_event_format_and_venue()',
                'display_event_components(), setup_component()',
                'finalize(), save_survey_data(), generate_csv_file()'
            ]
        })
        structure.to_excel(writer, sheet_name='앱 구조 및 흐름', index=False)

        # 3. 질문 흐름 및 로직
        questions = pd.DataFrame({
            '단계': ['기본 정보', '기본 정보', '행사 개요', '행사 개요', '행사 형태 및 장소', '행사 구성 요소'],
            '질문': [
                '이름, 부서, 직급은?',
                '행사 일정은?',
                '행사의 주요 목적은?',
                '예상 참가자 수는?',
                '행사 형태는?',
                '무대 설치가 필요한가요?'
            ],
            '후속 질문 조건': [
                '없음',
                '없음',
                '없음',
                '"미정" 선택 시 추가 질문 없음',
                '"오프라인" 또는 "하이브리드" 선택 시 장소 관련 질문',
                '"예" 선택 시 무대 관련 세부 질문'
            ],
            '데이터 저장 키': [
                'name, department, position',
                'event_start_date, event_end_date',
                'event_purpose',
                'expected_participants',
                'event_format',
                'stage_setup (within 무대 설치)'
            ]
        })
        questions.to_excel(writer, sheet_name='질문 흐름 및 로직', index=False)

        # 4. 주요 함수 설명
        functions = pd.DataFrame({
            '함수명': ['main()', 'display_progress()', 'improved_schedule_input()', 'setup_component()', 'save_survey_data()', 'generate_csv_file()'],
            '역할': [
                '앱의 메인 로직 제어',
                '진행 상황 표시',
                '행사 일정 입력 및 계산',
                '각 구성 요소별 설정 입력',
                '설문 데이터를 JSON 파일로 저장',
                'CSV 형식의 발주요청서 생성'
            ],
            '주요 기능': [
                '단계별 화면 표시, 네비게이션 제어',
                '현재 진행 단계를 시각적으로 표시',
                '시작일, 종료일 입력 및 셋업, 철수 일정 계산',
                '동적으로 각 구성 요소의 설정 옵션 생성',
                '입력된 데이터를 구조화하여 JSON 형식으로 저장',
                '입력 데이터를 바탕으로 카테고리별 CSV 파일 생성'
            ]
        })
        functions.to_excel(writer, sheet_name='주요 함수 설명', index=False)

        # 5. 데이터 구조
        data_structure = pd.DataFrame({
            '키': ['name', 'department', 'event_start_date', 'event_purpose', 'event_format', '무대 설치', '음향 시스템'],
            '데이터 타입': ['문자열', '문자열', 'datetime', '리스트', '문자열', '딕셔너리', '딕셔너리'],
            '설명': [
                '사용자 이름',
                '근무 부서',
                '행사 시작일',
                '행사 목적 (복수 선택 가능)',
                '행사 형태 (예: 오프라인, 온라인)',
                '무대 설치 관련 세부 정보',
                '음향 시스템 관련 세부 정보'
            ],
            '예시 값': [
                '홍길동',
                '마케팅팀',
                '2023-07-01',
                "['브랜드 인지도 향상', '신제품 출시']",
                '오프라인 행사',
                "{'needed': True, 'stage_size': '10m x 5m'}",
                "{'needed': True, 'setup_type': '트러스 설치'}"
            ]
        })
        data_structure.to_excel(writer, sheet_name='데이터 구조', index=False)

    return output

# 엑셀 파일 생성 및 다운로드 버튼 표시
excel_file = create_documentation()
st.download_button(
    label="기획 문서 다운로드",
    data=excel_file.getvalue(),
    file_name="이벤트_기획_도구_기획문서.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
