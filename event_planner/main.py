import streamlit as st
import pandas as pd
import sqlite3
from streamlit_pills import pills
import json
from datetime import datetime
import openpyxl

# 데이터베이스 연결 함수
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# 데이터베이스 초기화
def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS events
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     event_name TEXT,
                     client_name TEXT,
                     event_type TEXT,
                     scale INTEGER,
                     start_date DATE,
                     end_date DATE,
                     setup_start TEXT,
                     teardown TEXT,
                     venue_name TEXT,
                     venue_type TEXT,
                     address TEXT,
                     capacity TEXT,
                     facilities TEXT,
                     contract_amount INTEGER,
                     expected_profit INTEGER,
                     components TEXT)''')
    conn.commit()
    conn.close()

# 앱 초기화
def init_app():
    if 'step' not in st.session_state:
        st.session_state.step = 0
    if 'event_data' not in st.session_state:
        st.session_state.event_data = {}
    init_db()

# 메인 앱 함수
def main():
    st.title("이벤트 기획 도구")
    init_app()

    # 네비게이션
    steps = ["기본 정보", "장소 정보", "예산 정보", "용역 구성 요소", "진행 상황"]
    st.sidebar.title("단계")
    for i, step in enumerate(steps):
        if st.sidebar.button(step, key=f"nav_{i}"):
            st.session_state.step = i

    # 현재 단계 표시
    functions = [basic_info, venue_info, budget_info, service_components, progress_tracking]
    functions[st.session_state.step]()

    # 네비게이션 버튼
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.session_state.step > 0:
            if st.button("이전"):
                st.session_state.step -= 1
                st.experimental_rerun()
    with col2:
        if st.button("임시 저장"):
            save_data()
    with col3:
        if st.session_state.step < len(steps) - 1:
            if st.button("다음"):
                st.session_state.step += 1
                st.experimental_rerun()
        else:
            if st.button("제출"):
                save_data()
                generate_excel()

def basic_info():
    st.header("기본 정보")
    
    st.session_state.event_data['event_name'] = st.text_input("행사명", value=st.session_state.event_data.get('event_name', ''))
    st.session_state.event_data['client_name'] = st.text_input("클라이언트명", value=st.session_state.event_data.get('client_name', ''))
    
    event_types = ["영상 제작", "오프라인 이벤트"]
    # pills 함수 대신 multiselect 사용
    selected_types = st.multiselect("용역 유형", options=event_types, default=st.session_state.event_data.get('event_type', []))
    st.session_state.event_data['event_type'] = selected_types
    
    if "오프라인 이벤트" in selected_types:
        st.session_state.event_data['scale'] = st.number_input("예상 참여 관객 수", min_value=0, value=st.session_state.event_data.get('scale', 0))
        
        start_date = st.date_input("행사 시작일", value=st.session_state.event_data.get('start_date', date.today()))
        end_date = st.date_input("행사 종료일", value=st.session_state.event_data.get('end_date', date.today()))
        
        st.session_state.event_data['start_date'] = start_date
        st.session_state.event_data['end_date'] = end_date
        
        st.session_state.event_data['setup'] = st.radio("셋업 시작", ["전날부터", "당일"], index=0 if st.session_state.event_data.get('setup') == "전날부터" else 1)
        st.session_state.event_data['teardown'] = st.radio("철수", ["당일 철수", "다음날 철수"], index=0 if st.session_state.event_data.get('teardown') == "당일 철수" else 1)

def venue_info():
    st.header("장소 정보")
    
    venue_decided = st.radio("장소가 정확히 정해졌나요?", ["예", "아니오"])
    
    if venue_decided == "예":
        st.session_state.event_data['venue_name'] = st.text_input("장소명 (예: 서울시청 다목적홀B)", st.session_state.event_data.get('venue_name', ''))
        st.session_state.event_data['venue_type'] = st.selectbox("실내/실외", ["실내", "실외", "혼합", "온라인"], index=["실내", "실외", "혼합", "온라인"].index(st.session_state.event_data.get('venue_type', "실내")))
        
        if st.session_state.event_data['venue_type'] != "온라인":
            st.session_state.event_data['address'] = st.text_input("주소", st.session_state.event_data.get('address', ''))
        
        capacity_type = st.radio("수용 인원 입력 방식", ["범위", "단일 값"])
        current_capacity = st.session_state.event_data.get('capacity', '0-0')
        
        if isinstance(current_capacity, int):
            current_min = current_max = current_capacity
        elif isinstance(current_capacity, str) and '-' in current_capacity:
            current_min, current_max = map(int, current_capacity.split('-'))
        else:
            current_min = current_max = 0
        
        if capacity_type == "범위":
            min_capacity = st.number_input("최소 수용 인원", min_value=0, value=current_min)
            max_capacity = st.number_input("최대 수용 인원", min_value=0, value=current_max)
            st.session_state.event_data['capacity'] = f"{min_capacity}-{max_capacity}"
        else:
            st.session_state.event_data['capacity'] = st.number_input("수용 인원", min_value=0, value=current_min)
        
        facilities = ["무대", "음향 시스템", "조명 시스템", "프로젝터", "스크린", "Wi-Fi", "주차장", "기타"]
        st.session_state.event_data['facilities'] = st.multiselect("시설 및 장비", facilities, default=st.session_state.event_data.get('facilities', []))
    else:
        st.session_state.event_data['desired_region'] = st.text_input("희망 지역", st.session_state.event_data.get('desired_region', ''))
        st.session_state.event_data['desired_capacity'] = st.number_input("희망 수용 인원 (0 입력시 무관)", min_value=0, value=int(st.session_state.event_data.get('desired_capacity', 0)))

# 예산 정보 입력 함수
def budget_info():
    st.header("예산 정보")
    
    st.session_state.event_data['contract_amount'] = st.number_input("계약 금액 (원)", min_value=0, value=st.session_state.event_data.get('contract_amount', 0))
    
    profit_percent = st.number_input("예상 영업이익 (%)", min_value=0.0, max_value=100.0, value=st.session_state.event_data.get('profit_percent', 0.0))
    st.session_state.event_data['profit_percent'] = profit_percent
    
    expected_profit = int(st.session_state.event_data['contract_amount'] * (profit_percent / 100))
    st.session_state.event_data['expected_profit'] = expected_profit
    
    st.write(f"예상 영업이익: {expected_profit:,} 원")
    
    if st.button("예상 영업이익 수정"):
        st.session_state.event_data['expected_profit'] = st.number_input("예상 영업이익 (원)", min_value=0, value=expected_profit)
        st.session_state.event_data['profit_percent'] = (st.session_state.event_data['expected_profit'] / st.session_state.event_data['contract_amount']) * 100
        st.write(f"수정된 예상 영업이익 비율: {st.session_state.event_data['profit_percent']:.2f}%")

def service_components():
    st.header("용역 구성 요소")
    
    categories = [
        "기술 및 혁신", "네트워킹", "디자인", "마케팅 및 홍보", "미디어", "부대 행사",
        "섭외 / 인력", "시스템", "F&B", "제작 / 렌탈", "청소 / 관리", "출입 통제", "하드웨어"
    ]
    
    selected_categories = pills("카테고리 선택", categories, st.session_state.event_data.get('selected_categories', []))
    st.session_state.event_data['selected_categories'] = selected_categories
    
    if st.button("세부사항 입력"):
        st.session_state.event_data['components'] = {}
        for category in selected_categories:
            st.subheader(category)
            component = {}
            
            component['status'] = st.selectbox(f"{category} 진행 상황", ["발주처와 협상 진행 중", "확정", "거의 확정", "알 수 없는 상태"], key=f"status_{category}")
            
            if category == "기술 및 혁신":
                options = ["홍보용 앱 개발", "홍보용 홈페이지 개발"]
            elif category == "네트워킹":
                options = ["행사전 미팅 스케줄링", "행사전 참가자 매칭"]
            elif category == "디자인":
                options = ["로고", "캐릭터", "2D", "3D"]
            elif category == "마케팅 및 홍보":
                options = ["오프라인 (옥외 매체)", "오프라인 (지하철, 버스, 택시)", "온라인 (뉴스레터)", "온라인 (인플루언서)", 
                           "온라인 (키워드)", "온라인 (SNS / 바이럴)", "온라인 (SNS / 유튜브 비용집행)", 
                           "PR (기자회견 / 기자 컨택)", "PR (매체 광고)", "PR (보도자료 작성 및 배포)"]
            elif category == "미디어":
                options = ["2D/모션그래픽 제작", "3D 영상 제작", "드론 렌탈 및 운영", "배경 영상 제작", "사전 영상 제작",
                           "사진 (인물, 컨셉, 포스터 등)", "사진 (행사 스케치)", "스케치 영상 제작", "애니메이션 제작",
                           "중계 라이브 스트리밍", "중계 실시간 자막", "중계 촬영 / 편집", "프로젝션 맵핑 / 미디어 파사드",
                           "VR/AR 콘텐츠 제작"]
            elif category == "부대 행사":
                options = ["놀이 시설", "레크레이션", "자판기 (아이템 / 굿즈 등)", "자판기 (음료 / 스낵 / 솜사탕 등)",
                           "체험 부스 (게임존)", "체험 부스 (과학 실험)", "체험 부스 (로봇 체험)", "체험 부스 (심리상담)",
                           "체험 부스 (진로상담)", "체험 부스 (퍼스널 컬러)", "체험 부스 (VR/AR)", "키오스크"]
            elif category == "섭외 / 인력":
                options = ["가수", "강사", "경호 (행사 전반)", "경호 (VIP)", "공연팀 (댄스)", "공연팀 (서커스 / 마술 / 퍼포먼스)",
                           "공연팀 (음악)", "공연팀 (전통)", "배우", "번역", "연사", "요원 (소방안전)", "요원 (응급처치)",
                           "의전 도우미", "인플루언서", "코미디언", "통역 인력 및 장비 세팅", "패널 토론 진행자", 
                           "MC (기념식 / 시상식 등)", "MC (축제 / 페스티벌 등)", "STAFF (안전관리)", "STAFF (행사 운영)",
                           "STAFF (행사 진행)"]
            elif category == "시스템":
                options = ["음향 설치 및 운영", "음향 오퍼레이터", "조명 (공연)", "조명 (스피치 및 일반)", "LED 디스플레이 설치 및 운영"]
            elif category == "F&B":
                options = ["음료 바 설치", "커피차 대여 및 운영", "푸드 트럭 대여 및 운영", "푸드 트럭 섭외 및 공고",
                           "F&B (간식)", "F&B (도시락)", "F&B (뷔페식)", "F&B (코스요리)"]
            elif category == "제작 / 렌탈":
                options = ["렌탈 (다회용기)", "렌탈 (대형 특수)", "렌탈 (몽골텐트 3x3)", "렌탈 (부스)", "렌탈 (셔틀버스)",
                           "렌탈 (의자 / 테이블 / 무대 가구 등)", "렌탈 (이동식 화장실)", "렌탈 (흡연 부스)",
                           "목공 제작 (무대 배경)", "목공 제작 (세트 및 부스)", "목공 제작 (소품)", "목공 제작 (조형물)",
                           "인쇄 (명함)", "인쇄 (팜플렛 / 리플렛 / 포스터)", "제작 (몽골텐트 3x3)", "제작 (배너)",
                           "제작 (현수막)"]
            elif category == "청소 / 관리":
                options = ["환경미화팀"]
            elif category == "출입 통제":
                options = ["모바일 티켓 (QR)", "티켓 검수 & 티켓 인쇄"]
            elif category == "하드웨어":
                options = ["무대 설치 및 제작", "무대 시스템 (가변형 / 턴테이블 등)", "무대 특수효과"]
            else:
                options = []  # 기본값으로 빈 리스트 설정
            
            component['items'] = pills(f"{category} 세부 항목", options, key=f"items_{category}")
            
# 진행 상황 추적 함수
def progress_tracking():
    st.header("진행 상황")
    
    if 'components' in st.session_state.event_data:
        for category, component in st.session_state.event_data['components'].items():
            st.subheader(category)
            st.write(f"진행 상황: {component['status']}")
            st.write(f"선택된 항목: {', '.join(component['items'])}")
            st.write(f"예산: {component['budget']:,} 원 ({component['budget_percent']:.2f}%)")
            st.write(f"협력사 컨택: {component['contact']}")
            if 'other_company' in component:
                st.write(f"선정 업체: {component['other_company']}")
                st.write(f"선정 이유: {component['company_reason']}")
            st.write(f"세부사항: {component['details']}")
            st.write("---")

# 데이터 저장 함수
def save_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    event_data = st.session_state.event_data
    components_json = json.dumps(event_data.get('components', {}))
    
    cursor.execute('''INSERT OR REPLACE INTO events
                      (event_name, client_name, event_type, scale, start_date, end_date,
                       setup_start, teardown, venue_name, venue_type, address, capacity,
                       facilities, contract_amount, expected_profit, components)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (event_data.get('event_name'), event_data.get('client_name'),
                    json.dumps(event_data.get('event_type')), event_data.get('scale'),
                    event_data.get('start_date'), event_data.get('end_date'),
                    event_data.get('setup_start'), event_data.get('teardown'),
                    event_data.get('venue_name'), event_data.get('venue_type'),
                    event_data.get('address'), event_data.get('capacity'),
                    json.dumps(event_data.get('facilities')), event_data.get('contract_amount'),
                    event_data.get('expected_profit'), components_json))
    
    conn.commit()
    conn.close()
    
    st.success("데이터가 성공적으로 저장되었습니다.")

# 엑셀 보고서 생성 함수
def generate_excel():
    event_data = st.session_state.event_data
    
    # 전체 행사 보고서
    df_full = pd.DataFrame([event_data])
    df_full['components'] = df_full['components'].apply(json.dumps)
    
    # 부분 발주요청서
    df_partial = pd.DataFrame(columns=['카테고리', '진행 상황', '선택된 항목', '예산', '협력사 컨택', '선정 업체', '선정 이유', '세부사항'])
    
    for category, component in event_data.get('components', {}).items():
        df_partial = df_partial.append({
            '카테고리': category,
            '진행 상황': component['status'],
            '선택된 항목': ', '.join(component['items']),
            '예산': f"{component['budget']:,} 원 ({component['budget_percent']:.2f}%)",
            '협력사 컨택': component['contact'],
            '선정 업체': component.get('other_company', ''),
            '선정 이유': component.get('company_reason', ''),
            '세부사항': component['details']
        }, ignore_index=True)
    
    # Excel 파일 생성
    filename = f"이벤트_기획_{event_data['event_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    with pd.ExcelWriter(filename) as writer:
        df_full.to_excel(writer, sheet_name='전체 행사 보고서', index=False)
        df_partial.to_excel(writer, sheet_name='부분 발주요청서', index=False)
    
    st.success(f"엑셀 보고서가 생성되었습니다: {filename}")
    
    # 파일 다운로드 링크 제공
    with open(filename, "rb") as file:
        btn = st.download_button(
            label="엑셀 보고서 다운로드",
            data=file,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# 메인 함수 호출
if __name__ == "__main__":
    main()