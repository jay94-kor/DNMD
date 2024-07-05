import streamlit as st
from streamlit_option_menu import option_menu
from datetime import date, timedelta, datetime
import json
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
import os
from typing import Dict, Any, List
import logging
import re
from openpyxl.utils.dataframe import dataframe_to_rows



logging.basicConfig(filename='app.log', level=logging.ERROR)

JSON_PATH = os.path.join(os.path.dirname(__file__), 'item_options.json')
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

EVENT_TABLE_COLUMNS = [
    'event_name', 'client_name', 'manager_name', 'manager_contact', 'event_type', 
    'contract_type', 'scale', 'start_date', 'end_date', 'setup_start', 'teardown',
    'venue_name', 'venue_type', 'address', 'capacity', 'facilities',
    'contract_amount', 'expected_profit', 'components'
]

class EventOptions:
    def __init__(self, item_options):
        self.EVENT_TYPES = item_options['EVENT_TYPES']
        self.CONTRACT_TYPES = item_options['CONTRACT_TYPES']
        self.STATUS_OPTIONS = item_options['STATUS_OPTIONS']
        self.MEDIA_ITEMS = item_options['MEDIA_ITEMS']
        self.CATEGORIES = item_options['CATEGORIES']
        self.CATEGORY_ICONS = item_options['CATEGORY_ICONS']

# JSON 파일에서 item_options 로드
with open(JSON_PATH, 'r', encoding='utf-8') as file:
    item_options = json.load(file)

# config.json 파일에서 설정 로드
with open(CONFIG_PATH, 'r', encoding='utf-8') as file:
    config = json.load(file)

event_options = EventOptions(item_options)

def format_currency(amount: float) -> str:
    return f"{amount:,.0f}"

def format_phone_number(number):
    pattern = r'(\d{3})(\d{3,4})(\d{4})'
    return re.sub(pattern, r'\1-\2-\3', number)

def basic_info() -> None:
    event_data = st.session_state.event_data
    st.header("기본 정보")
    
    handle_general_info(event_data)
    handle_event_type(event_data)
    handle_budget_info(event_data)
    
    if event_data['event_type'] == "온라인 콘텐츠":
        handle_video_production(event_data)
    elif event_data['event_type'] == "오프라인 이벤트":
        handle_offline_event(event_data)

def handle_general_info(event_data: Dict[str, Any]) -> None:
    st.write(f"현재 예상 참여 관객 수: {event_data.get('scale', 0)}명")  # 기존 예상 참여 관객 수 표시

    event_data['event_name'] = st.text_input("용역명", value=event_data.get('event_name', ''), key="event_name_basic", autocomplete="off")
    event_data['client_name'] = st.text_input("클라이언트명", value=event_data.get('client_name', ''), key="client_name_basic")
    event_data['manager_name'] = st.text_input("담당자명", value=event_data.get('manager_name', ''), key="manager_name_basic")
    
    event_data['manager_position'] = render_option_menu(
        "담당자 직급",
        options=["선임", "책임", "수석"],
        key="manager_position"
    )
    
    manager_contact = st.text_input(
        "담당자 연락처",
        value=event_data.get('manager_contact', ''),
        help="숫자만 입력해주세요 (예: 01012345678)",
        key="manager_contact_basic"
    )
    if manager_contact:
        manager_contact = ''.join(filter(str.isdigit, manager_contact))
        event_data['manager_contact'] = format_phone_number(manager_contact)
    
    st.write(f"입력된 연락처: {event_data.get('manager_contact', '')}")

def render_option_menu(label: str, options: List[str], key: str) -> str:
    icons = ["🔹" for _ in options]
    selected = option_menu(
        None, options,
        icons=icons,
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#f0f0f0"},  # 연한 회색 배경
            "icon": {"color": "#ff6347", "font-size": "16px"},  # 토마토 색상 아이콘
            "nav-link": {"font-size": "14px", "text-align": "center", "margin":"0px", "--hover-color": "#ffcccc", "--icon-color": "#ff6347"},  # 연한 빨간색 호버, 토마토 색상 아이콘
            "nav-link-selected": {"background-color": "#ff6347", "color": "white", "--icon-color": "white"},  # 토마토 색상 배경, 흰색 글자, 흰색 아이콘
        },
        key=key
    )
    return selected

def handle_event_type(event_data: Dict[str, Any]) -> None:
    event_data['event_type'] = render_option_menu(
        "용역 유형",
        event_options.EVENT_TYPES,
        "event_type"
    )
    event_data['contract_type'] = render_option_menu(
        "용역 종류",
        event_options.CONTRACT_TYPES,
        "contract_type"
    )

def handle_budget_info(event_data: Dict[str, Any]) -> None:
    st.header("예산 정보")
    
    default_contract_status_index = config['CONTRACT_STATUS_OPTIONS'].index(event_data.get('contract_status', '확정'))
    event_data['contract_status'] = render_option_menu(
        "계약 금액 상태",
        config['CONTRACT_STATUS_OPTIONS'],
        "contract_status"
    )

    # 부가세 포함 여부 버튼을 노란색으로 변경
    vat_options = config['VAT_OPTIONS']
    vat_included = option_menu(
        "부가세 포함 여부",
        options=vat_options,
        icons=['check-circle', 'x-circle'],
        menu_icon="coin",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#FFF9C4"},  # 연한 노란색 배경
            "icon": {"color": "#FBC02D", "font-size": "16px"},  # 진한 노란색 아이콘
            "nav-link": {"font-size": "14px", "text-align": "center", "margin":"0px", "--hover-color": "#FFF59D", "--icon-color": "#FBC02D"},  # 연한 노란색 호버, 진한 노란색 아이콘
            "nav-link-selected": {"background-color": "#FBC02D", "color": "white", "--icon-color": "white"},  # 진한 노란색 배경, 흰색 글자, 흰색 아이콘
        },
        key="vat_included"
    )
    event_data['vat_included'] = (vat_included == vat_options[0])
    
    event_data['contract_amount'] = st.number_input(
        "총 계약 금액 (원)", 
        min_value=0, 
        value=event_data.get('contract_amount', 0), 
        key="contract_amount",
        format="%d"
    )
    
    if event_data['vat_included']:
        original_amount = round(event_data['contract_amount'] / 1.1)
        vat_amount = round(event_data['contract_amount'] - original_amount)
    else:
        original_amount = event_data['contract_amount']
        vat_amount = round(original_amount * 0.1)
    
    st.write(f"입력된 계약 금액: {format_currency(event_data['contract_amount'])} 원")
    st.write(f"원금: {format_currency(original_amount)} 원")
    st.write(f"부가세: {format_currency(vat_amount)} 원")
    
    if event_data['contract_status'] == "추가 예정":
        event_data['additional_amount'] = st.number_input(
            "추가 예정 금액 (원)", 
            min_value=0, 
            value=event_data.get('additional_amount', 0), 
            key="additional_amount",
            format="%d"
        )
        st.write(f"입력된 추가 예정 액: {format_currency(event_data['additional_amount'])} 원")
    
    event_data['expected_profit_percentage'] = st.number_input(
        "예상 수익률 (%)", 
        min_value=0.0, 
        max_value=100.0, 
        value=event_data.get('expected_profit_percentage', 0.0),
        format="%.2f",
        step=0.01,
        key="expected_profit_percentage"
    )
    
    total_amount = event_data['contract_amount'] + event_data.get('additional_amount', 0)
    expected_profit = round(original_amount * (event_data['expected_profit_percentage'] / 100))
    
    event_data['expected_profit'] = expected_profit
    
    st.write(f"예상 수익 금액: {format_currency(expected_profit)} 원")

def handle_video_production(event_data: Dict[str, Any]) -> None:
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("과업 시작일", value=event_data.get('start_date', date.today()), key="start_date")
    with col2:
        end_date = st.date_input("과업 종료일", value=event_data.get('end_date', start_date + timedelta(days=365)), key="end_date")

    if start_date > end_date:
        end_date = start_date + timedelta(days=365)
        st.warning("과업 종료일이 시작일 이전이어서 자동으로 조정되었습니다.")

    event_data['start_date'] = start_date
    event_data['end_date'] = end_date
    
    duration = (end_date - start_date).days
    months, days = divmod(duration, 30)
    st.write(f"과업 기간: {months}개월 {days}일")

def handle_offline_event(event_data: Dict[str, Any]) -> None:
    st.subheader("오프라인 이벤트 정보")

    event_data['start_date'] = st.date_input("시작 날짜", value=event_data.get('start_date', date.today()), key="start_date")
    event_data['end_date'] = st.date_input("종료 날짜", value=event_data.get('end_date', event_data['start_date']), key="end_date")

    event_data['setup_start'] = render_option_menu("셋업 시작", config['SETUP_OPTIONS'], "setup_start")

    if event_data['setup_start'] == config['SETUP_OPTIONS'][0]:
        event_data['setup_date'] = event_data['start_date'] - timedelta(days=1)
    else:
        event_data['setup_date'] = event_data['start_date']

    event_data['teardown'] = render_option_menu("철수", config['TEARDOWN_OPTIONS'], "teardown")

def venue_info() -> None:
    event_data = st.session_state.event_data
    st.header("장소 정보")

    if event_data['event_type'] == "온라인 콘텐츠":
        handle_online_content_location(event_data)
    else:
        event_data['venue_status'] = render_option_menu(
            "장소 확정 상태",
            event_options.STATUS_OPTIONS,
            "venue_status"
        )

        venue_type_options = ["실내", "실외", "혼합", "온라인"]
        event_data['venue_type'] = render_option_menu(
            "희망하는 장소 유형",
            venue_type_options,
            "venue_type"
        )

        event_data['scale'] = st.number_input(
            "예상 참여 관객 수", 
            min_value=0, 
            value=event_data.get('scale', 0),
            step=1,
            format="%d",
            key="scale_input_venue"
        )

        if event_data['venue_type'] == "온라인":
            st.info("온라인 이벤트는 물리적 장소 정보가 필요하지 않습니다.")
            event_data['venues'] = []
        elif event_data['venue_status'] == "알 수 없는 상태":
            handle_unknown_venue_status(event_data)
        else:
            handle_known_venue_status(event_data)

def handle_online_content_location(event_data: Dict[str, Any]) -> None:
    location_needed = st.radio("촬영 로케이션 필요 여부", ["필요", "불필요"], key="location_needed")
    
    if location_needed == "필요":
        location_type = st.radio("어떤 로케이션이 필요한가요?", ["프로덕션이 알아서 구해오기", "직접 지정"], key="location_type")
        
        if location_type == "프로덕션이 알아서 구해오기":
            location_preference = st.radio("실내, 실외, 혼합 중 하나를 선택해주세요.", ["실내", "실외", "혼합"], key="location_preference")
            
            if location_preference == "실내":
                event_data['indoor_location_description'] = st.text_area("어떤 느낌의 장소인지 작성해주세요.", key="indoor_location_description")
            elif location_preference == "실외":
                event_data['outdoor_location_description'] = st.text_area("어떤 느낌의 장소인지 작성해주세요.", key="outdoor_location_description")
        
        elif location_type == "직접 지정":
            event_data['location_type'] = st.radio("실내인지 실외인지 선택해주세요.", ["실내", "실외"], key="direct_location_type")
            event_data['location_name'] = st.text_input("장소명", key="location_name")
            event_data['location_address'] = st.text_input("주소", key="location_address")
            event_data['location_status'] = render_option_menu(
                "확정의 정도를 선택해주세요.",
                event_options.STATUS_OPTIONS,
                "location_status"
            )

def handle_unknown_venue_status(event_data: Dict[str, Any]) -> None:
    major_regions = [
        "서울", "부산", "인천", "대구", "대전", "광주", "울산", "세종",
        "경기도", "강원도", "충청북도", "충청남도", "전라북도", "전라남도", "경상북도", "경상남도", "제주도"
    ]
    
    def format_region(region: str) -> str:
        region_emojis = {
            "서울": "🗼", "부산": "🌉", "인천": "🛳️", "대구": "🌆", "대전": "🏙️", "광주": "🏞️", 
            "울산": "🏭", "세종": "🏛️", "경기도": "🏘️", "강원도": "⛰️", "충청북도": "🌳", "충청남도": "🌊", 
            "전라북도": "🍚", "전라남도": "🌴", "경상북도": "🍎", "경상남도": "🐘", "제주도": "🍊"
        }
        return f"{region_emojis.get(region, '📍')} {region}"
    
    event_data['desired_region'] = st.selectbox(
        "희망하는 지역",
        options=major_regions,
        index=major_regions.index(event_data.get('desired_region', major_regions[0])),
        format_func=format_region,
        key="desired_region_selectbox"
    )

    event_data['specific_location'] = st.text_input("세부 지역 (선택사항)", value=event_data.get('specific_location', ''), key="specific_location")
    event_data['desired_capacity'] = st.number_input("희망하는 수용 인원", min_value=0, value=int(event_data.get('desired_capacity', 0)), key="desired_capacity")

    handle_venue_facilities(event_data)
    handle_venue_budget(event_data)

def handle_known_venue_status(event_data: Dict[str, Any]) -> None:
    if 'venues' not in event_data or not event_data['venues']:
        event_data['venues'] = [{'name': '', 'address': ''}]

    for i, venue in enumerate(event_data['venues']):
        st.subheader(f"장소 {i+1}")
        col1, col2 = st.columns(2)
        with col1:
            venue['name'] = st.text_input("장소명", value=venue.get('name', ''), key=f"venue_name_{i}")
        with col2:
            venue['address'] = st.text_input("주소", value=venue.get('address', ''), key=f"venue_address_{i}")
        
        if i > 0 and st.button(f"장소 {i+1} 삭제", key=f"delete_venue_{i}"):
            event_data['venues'].pop(i)
            st.rerun()  # 여기를 변경했습니다

    if st.button("장소 추가"):
        event_data['venues'].append({'name': '', 'address': ''})
        st.rerun()  # 여기를 변경했습니다

    handle_venue_facilities(event_data)
    handle_venue_budget(event_data)

def handle_venue_facilities(event_data: Dict[str, Any]) -> None:
    if event_data['venue_type'] in ["실내", "혼합"]:
        if event_data['venue_status'] != "알 수 없는 상태":
            # 수용 인원 입력 부분 제거
            pass

        facility_options = ["음향 시설", "조명 시설", "LED 시설", "빔프로젝트 시설", "주차", "Wifi", "기타"]
        event_data['facilities'] = st.multiselect("행사장 자체 보유 시설", facility_options, default=event_data.get('facilities', []), key="facilities")
        
        if "기타" in event_data['facilities']:
            event_data['other_facilities'] = st.text_input("기타 시설 입력", key="other_facility_input")

def handle_venue_budget(event_data: Dict[str, Any]) -> None:
    event_data['venue_budget'] = st.number_input("장소 대관 비용 예산 (원)", min_value=0, value=int(event_data.get('venue_budget', 0)), key="venue_budget", format="%d")

def service_components() -> None:
    event_data = st.session_state.event_data
    st.header("용역 구성 요소")

    selected_categories = select_categories_with_icons(event_data)
    event_data['selected_categories'] = selected_categories

    event_data['components'] = event_data.get('components', {})
    for category in selected_categories:
        handle_category(category, event_data)

    event_data['components'] = {k: v for k, v in event_data['components'].items() if k in selected_categories}

def select_categories_with_icons(event_data: Dict[str, Any]) -> List[str]:
    categories = list(event_options.CATEGORIES.keys())
    default_categories = event_data.get('selected_categories', [])
    default_categories = [cat for cat in default_categories if cat in categories]

    if event_data.get('event_type') == "온라인 콘텐츠" and "미디어" not in default_categories:
        default_categories.append("미디어")
        st.info("온라인 콘텐츠 프로젝트를 위해 '미디어' 카테고리가 자동으로 추가되었습니다.")
    elif event_data.get('venue_type') == "온라인" and "미디어" not in default_categories:
        default_categories.append("미디어")
        st.info("온라인 이벤트를 위해 '미디어' 카테고리가 자동으로 추가되었습니다.")

    col1, col2, col3, col4 = st.columns(4)
    selected_categories = []

    for i, category in enumerate(categories):
        with [col1, col2, col3, col4][i % 4]:
            if st.checkbox(
                f"{event_options.CATEGORY_ICONS[category]} {category}",
                value=category in default_categories,
                key=f"category_{category}_{i}"  # 여기에 i를 추가하여 고유한 키 생성
            ):
                selected_categories.append(category)

    return selected_categories

def handle_category(category: str, event_data: Dict[str, Any]) -> None:
    st.subheader(category)
    component = event_data['components'].get(category, {})
    
    component['status'] = render_option_menu(
        f"{category} 진행 상황",
        event_options.STATUS_OPTIONS,
        f"{category}_status"
    )
    
    component['items'] = st.multiselect(
        f"{category} 항목 선택",
        event_options.CATEGORIES.get(category, []),
        default=component.get('items', []),
        key=f"{category}_items"
    )

    component['budget'] = st.number_input(f"{category} 예산 (원)", min_value=0, value=component.get('budget', 0), key=f"{category}_budget")

    # 협력사 선택 옵션
    cooperation_options = ["협력사 매칭 필요", "선호하는 업체 있음"]
    component['cooperation_status'] = render_option_menu(
        "협력사 상태",
        cooperation_options,
        f"{category}_cooperation_status"
    )

    if component['cooperation_status'] == "선호하는 업체 있음":
        handle_preferred_vendor(component, category)
    else:
        # 협력사 매칭 필요 시 관련 정보 초기화
        component['preferred_vendor'] = False
        component['vendor_reason'] = ''
        component['vendor_name'] = ''
        component['vendor_contact'] = ''
        component['vendor_manager'] = ''

    for item in component['items']:
        handle_item_details(item, component)

    event_data['components'][category] = component

def handle_preferred_vendor(component: Dict[str, Any], category: str) -> None:
    component['vendor_reason'] = render_option_menu(
        "선호하는 이유를 선택해주세요:",
        config['VENDOR_REASON_OPTIONS'],
        f"{category}_vendor_reason"
    )
    component['vendor_name'] = st.text_input("선호 업체 상호명", value=component.get('vendor_name', ''), key=f"{category}_vendor_name")
    component['vendor_contact'] = st.text_input("선호 업체 연락처", value=component.get('vendor_contact', ''), key=f"{category}_vendor_contact")
    component['vendor_manager'] = st.text_input("선호 업체 담당자명", value=component.get('vendor_manager', ''), key=f"{category}_vendor_manager")

def handle_item_details(item: str, component: Dict[str, Any]) -> None:
    quantity_key = f'{item}_quantity'
    unit_key = f'{item}_unit'
    details_key = f'{item}_details'

    component[quantity_key] = st.number_input(f"{item} 수량", min_value=0, value=component.get(quantity_key, 0), key=quantity_key)
    
    if item in ["유튜브 (예능)", "유튜브 (교육 / 강의)", "유튜브 (인터뷰 형식)", 
                "숏폼 (재편집)", "숏폼 (신규 제작)", "웹드라마", 
                "2D / 모션그래픽 제작", "3D 영상 제작", "행사 배경 영상", 
                "행사 사전 영상", "스케치 영상 제작", "애니메이션 제작"]:
        component[unit_key] = "편"
    elif item in ["사진 (인물, 컨셉, 포스터 등)", "사진 (행사 스케치)"]:
        component[unit_key] = "컷"
    else:
        component[unit_key] = "개"
    
    component[details_key] = st.text_area(f"{item} 세부사항", value=component.get(details_key, ''), key=details_key)

def generate_summary_excel() -> None:
    event_data = st.session_state.event_data
    event_name = event_data.get('event_name', '무제')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    summary_filename = f"이벤트_기획_정의서_{event_name}_{timestamp}.xlsx"
    
    try:
        create_excel_summary(event_data, summary_filename)
        st.success(f"엑셀 정의서가 성공적으로 생성되었습니다: {summary_filename}")
        
        with open(summary_filename, "rb") as file:
            st.download_button(label="전체 행사 요약 정의서 다운로드", data=file, file_name=summary_filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        # 카테고리별 발주요청서 생성
        for category, component in event_data.get('components', {}).items():
            category_filename = f"발주요청서_{category}_{event_name}_{timestamp}.xlsx"
            create_category_excel(event_data, category, component, category_filename)
            try:
                with open(category_filename, "rb") as file:
                    st.download_button(label=f"{category} 발주요청서 다운로드", data=file, file_name=category_filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=f"download_{category}")
            except FileNotFoundError:
                st.error(f"{category_filename} 파일을 찾을 수 없습니다.")
        
    except Exception as e:
        st.error(f"엑셀 파일 생성 중 오류가 발생했습니다: {str(e)}")
        st.error("오류 상세 정보:")
        st.exception(e)

def create_excel_summary(event_data: Dict[str, Any], filename: str) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "전��� 행사 요약"
    
    # 열 너비 설정
    for col in ['A', 'B', 'C', 'D']:
        ws.column_dimensions[col].width = 30
    
    # 기본 정보 추가
    ws['A1'] = "용역명"
    ws['B1'] = event_data.get('event_name', '')
    ws['C1'] = "고객사"
    ws['D1'] = event_data.get('client_name', '')
    
    ws['A2'] = "담당자명"
    ws['B2'] = event_data.get('manager_name', '')
    ws['C2'] = "담당자 직급"
    ws['D2'] = event_data.get('manager_position', '')
    
    ws['A3'] = "담당자 연락처"
    ws['B3'] = event_data.get('manager_contact', '')
    ws['C3'] = "행사 유형"
    ws['D3'] = event_data.get('event_type', '')
    
    ws['A4'] = "용역 종류"
    ws['B4'] = event_data.get('contract_type', '')
    ws['C4'] = "규모"
    ws['D4'] = f"{event_data.get('scale', '')}명"
    
    ws['A5'] = "시작일"
    ws['B5'] = str(event_data.get('start_date', ''))
    ws['C5'] = "종료일"
    ws['D5'] = str(event_data.get('end_date', ''))
    
    ws['A6'] = "셋업 시작"
    ws['B6'] = event_data.get('setup_start', '')
    ws['C6'] = "철수"
    ws['D6'] = event_data.get('teardown', '')
    
    ws['A7'] = "총 계약 금액"
    ws['B7'] = f"{format_currency(event_data.get('contract_amount', 0))} 원"
    ws['C7'] = "예상 수익률"
    ws['D7'] = f"{event_data.get('expected_profit_percentage', 0)}%"
    
    ws['A8'] = "예상 수익 금액"
    ws['B8'] = f"{format_currency(event_data.get('expected_profit', 0))} 원"
    ws['C8'] = "장소 확정 상태"
    ws['D8'] = event_data.get('venue_status', '')
    
    # 스타일 적용
    apply_styles(ws, max_row=8, max_col=4)
    
    wb.save(filename)

def create_category_excel(event_data: Dict[str, Any], category: str, component: Dict[str, Any], filename: str) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f'{category} 발주요청서'
    
    # 열 너비 설정
    for col in ['A', 'B', 'C', 'D']:
        ws.column_dimensions[col].width = 30
    
    # 기본 정보 추가
    ws['A1'] = "용역명"
    ws['B1'] = event_data.get('event_name', '')
    ws['C1'] = "고객사"
    ws['D1'] = event_data.get('client_name', '')
    
    ws['A2'] = "담당자명"
    ws['B2'] = event_data.get('manager_name', '')
    ws['C2'] = "담당자 직급"
    ws['D2'] = event_data.get('manager_position', '')
    
    ws['A3'] = "담당자 연락처"
    ws['B3'] = event_data.get('manager_contact', '')
    ws['C3'] = "행사 유형"
    ws['D3'] = event_data.get('event_type', '')
    
    ws['A4'] = "용역 종류"
    ws['B4'] = event_data.get('contract_type', '')
    ws['C4'] = "규모"
    ws['D4'] = f"{event_data.get('scale', '')}명"
    
    ws['A5'] = "시작일"
    ws['B5'] = str(event_data.get('start_date', ''))
    ws['C5'] = "종료일"
    ws['D5'] = str(event_data.get('end_date', ''))
    
    ws['A6'] = "셋업 시작"
    ws['B6'] = event_data.get('setup_start', '')
    ws['C6'] = "철수"
    ws['D6'] = event_data.get('teardown', '')
    
    ws['A7'] = "총 계약 금액"
    ws['B7'] = f"{format_currency(event_data.get('contract_amount', 0))} 원"
    ws['C7'] = "예상 수익률"
    ws['D7'] = f"{event_data.get('expected_profit_percentage', 0)}%"
    
    ws['A8'] = "예상 수익 금액"
    ws['B8'] = f"{format_currency(event_data.get('expected_profit', 0))} 원"
    ws['C8'] = "장소 확정 상태"
    ws['D8'] = event_data.get('venue_status', '')
    
    # 카테고리 정보 추가
    ws['A10'] = "카테고리 정보"
    ws['A11'] = f"카테고리: {category}"
    ws['A12'] = f"진행 상황: {component.get('status', '')}"
    ws['A13'] = f"예산: {format_currency(component.get('budget', 0))} 원"
    ws['A14'] = f"선호 업체 여부: {'예' if component.get('preferred_vendor', False) else '아니오'}"
    
    if component.get('preferred_vendor', False):
        ws['A15'] = f"선호 이유: {component.get('vendor_reason', '')}"
        ws['A16'] = f"선호 업체 상호명: {component.get('vendor_name', '')}"
        ws['A17'] = f"선호 업체 연락처: {component.get('vendor_contact', '')}"
        ws['A18'] = f"선호 업체 담당자명: {component.get('vendor_manager', '')}"
    
    # 발주 요청 항목
    ws['A20'] = "발주 요청 항목"
    ws['A21'] = "카테고리"
    ws['B21'] = category
    ws['A22'] = "진행 상황"
    ws['B22'] = component.get('status', '')
    ws['A23'] = "예산"
    ws['B23'] = f"{format_currency(component.get('budget', 0))} 원"
    
    # 항목 리스트 추가
    ws['A25'] = "항목"
    ws['B25'] = "수량"
    ws['C25'] = "단위"
    ws['D25'] = "세부사항"
    
    row = 26
    for item in component.get('items', []):
        ws[f'A{row}'] = item
        ws[f'B{row}'] = component.get(f'{item}_quantity', 0)
        ws[f'C{row}'] = component.get(f'{item}_unit', '개')
        ws[f'D{row}'] = component.get(f'{item}_details', '')
        row += 1
    
    # 스타일 적용
    apply_styles(ws, max_row=row-1, max_col=4)
    
    wb.save(filename)

def apply_styles(ws, max_row, max_col):
    header_fill = PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid")
    border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    
    for row in ws.iter_rows(min_row=1, max_row=max_row, min_col=1, max_col=max_col):
        for cell in row:
            cell.border = border
            if cell.row == 1 or cell.column in [1, 3]:
                cell.fill = header_fill
                cell.font = Font(bold=True)

def format_currency(amount):
    return "{:,}".format(amount)

def render_option_menu(label: str, options: List[str], key: str) -> str:
    icons = ["🔹" for _ in options]
    selected = option_menu(
        None, options,
        icons=icons,
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#f0f0f0"},  # 연한 회색 배경
            "icon": {"color": "#ff6347", "font-size": "16px"},  # 토마토 색상 아이콘
            "nav-link": {"font-size": "14px", "text-align": "center", "margin":"0px", "--hover-color": "#ffcccc", "--icon-color": "#ff6347"},  # 연한 빨간색 호버, 토마토 색상 아이콘
            "nav-link-selected": {"background-color": "#ff6347", "color": "white", "--icon-color": "white"},  # 토마토 색상 배경, 흰색 글자, 흰색 아이콘
        },
        key=key
    )
    return selected


def check_required_fields(step):
    event_data = st.session_state.event_data
    required_fields = []
    missing_fields = []

    if step == 0:  # 기본 정보
        required_fields = ['event_name', 'client_name', 'manager_name', 'manager_position', 'manager_contact', 'event_type', 'contract_type', 'contract_amount', 'expected_profit_percentage']
        if event_data.get('event_type') == "온라인 콘텐츠":
            required_fields.extend(['start_date', 'end_date'])
        elif event_data.get('event_type') == "오프라인 이벤트":
            required_fields.extend(['start_date', 'end_date', 'setup_start', 'teardown'])
    elif step == 1:  # 장소 정보
        if event_data.get('venue_type') != "온라인":
            required_fields = ['venue_status', 'venue_type', 'scale']
            if event_data.get('venue_status') == "알 수 없는 상태":
                required_fields.extend(['desired_region', 'desired_capacity'])
            else:
                required_fields.extend(['venues'])
                if event_data.get('venues'):
                    for i, venue in enumerate(event_data['venues']):
                        if not venue.get('name'):
                            missing_fields.append(f'venues[{i}].name')
                        if not venue.get('address'):
                            missing_fields.append(f'venues[{i}].address')
    elif step == 2:  # 용역 구성 요소
        if not event_data.get('selected_categories'):
            missing_fields.append('selected_categories')
        else:
            for category in event_data.get('selected_categories', []):
                if category not in event_data.get('components', {}):
                    missing_fields.append(f'components.{category}')
                else:
                    component = event_data['components'][category]
                    if not component.get('status'):
                        missing_fields.append(f'components.{category}.status')
                    if not component.get('items'):
                        missing_fields.append(f'components.{category}.items')
    else:
        return True, []  # 정의서 생성 단계는 모든 필드가 이미 채워져 있어야 함

    for field in required_fields:
        if not event_data.get(field):
            missing_fields.append(field)

    return len(missing_fields) == 0, missing_fields

def highlight_missing_fields(missing_fields):
    field_names = {
        'event_name': '용역명',
        'client_name': '클라이언트명',
        'manager_name': '담당자명',
        'manager_position': '담당자 직급',
        'manager_contact': '담당자 연락처',
        'event_type': '용역 유형',
        'contract_type': '용역 종류',
        'scale': '예상 참여 관객 수',
        'contract_amount': '총 계약 금액',
        'expected_profit_percentage': '예상 수익률',
        'start_date': '시작일',
        'end_date': '종료일',
        'setup_start': '셋업 시작',
        'teardown': '철수',
        'venue_status': '장소 확정 상태',
        'venue_type': '장소 유형',
        'desired_region': '희망하는 지역',
        'desired_capacity': '희망하는 수용 인원',
        'venues': '장소',
        'selected_categories': '선택된 카테고리',
        'components': '용역 구성 요소',
        'status': '상태',
        'items': '항목'
    }

    for field in missing_fields:
        if '.' in field:
            category, subfield = field.split('.', 1)
            st.error(f"{field_names.get(category, category)} 카테고리의 {field_names.get(subfield, subfield)} 항목을 입력해주세요.")
        elif '[' in field:
            base, index = field.split('[')
            index = index.split(']')[0]
            subfield = field.split('.')[-1]
            st.error(f"{field_names.get(base, base)} 목록의 {int(index)+1}번째 항목의 {field_names.get(subfield, subfield)}을(를) 입력해주세요.")
        else:
            st.error(f"{field_names.get(field, field)} 항목을 입력해주세요.")

def main():
    st.title("이벤트 플래너")
    
    if 'current_event' not in st.session_state:
        st.session_state.current_event = None
    if 'step' not in st.session_state:
        st.session_state.step = 0
    if 'event_data' not in st.session_state:
        st.session_state.event_data = {}

    functions = {
        0: basic_info,
        1: venue_info,
        2: service_components,
        3: generate_summary_excel
    }

    step_names = ["기본 정보", "장소 정보", "용역 구성 요소", "정의서 생성"]
    
    current_step = st.session_state.step
    selected_step = option_menu(
        None, 
        step_names, 
        icons=['info-circle', 'geo-alt', 'list-task', 'file-earmark-spreadsheet'], 
        default_index=current_step, 
        orientation='horizontal',
        styles={
            "container": {"padding": "0!important", "background-color": "#e3f2fd"},  # 매우 연한 푸른색 배경
            "icon": {"color": "#1976d2", "font-size": "25px"},  # 진한 푸른색 아이콘
            "nav-link": {"font-size": "16px", "text-align": "center", "margin":"0px", "--hover-color": "#bbdefb", "--icon-color": "#1976d2"},  # 연한 푸른색 호버, 진한 푸른색 아이콘
            "nav-link-selected": {"background-color": "#2196f3", "color": "white", "--icon-color": "white"},  # 중간 푸른색 배경, 흰색 글자, 흰색 아이콘
        },
    )
    
    if selected_step != step_names[current_step]:
        st.session_state.step = step_names.index(selected_step)
        st.rerun()  # 여기를 변경했습니다
    
    functions[current_step]()
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if current_step > 0:
            if st.button("이전 단계로"):
                st.session_state.step -= 1
                st.rerun()  # 여기를 변경했습니다
    
    with col3:
        if current_step < len(functions) - 1:
            if st.button("다음 단계로"):
                fields_complete, missing_fields = check_required_fields(current_step)
                if fields_complete:
                    st.session_state.step += 1
                    st.rerun()
                else:
                    st.error("모든 필수 항목을 입력해주세요.")
                    highlight_missing_fields(missing_fields)

if __name__ == "__main__":
    main()
