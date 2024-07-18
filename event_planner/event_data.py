import streamlit as st
from datetime import date, datetime, timedelta
from ui import render_option_menu
from utils import format_phone_number, format_currency
from config import config
from main import event_options, save_event_data, display_guide

def handle_general_info(event_data):
    st.write(f"현재 예상 참여 관객 수: {event_data.get('scale', 0)}명")

    col1, col2 = st.columns(2)
    with col1:
        event_data['event_name'] = st.text_input("용역명", value=event_data.get('event_name', ''), key="event_name_basic", autocomplete="off")
        event_data['client_name'] = st.text_input("클라이언트명", value=event_data.get('client_name', ''), key="client_name_basic")
    with col2:
        event_data['manager_name'] = st.text_input("담당 PM", value=event_data.get('manager_name', ''), key="manager_name_basic")
        event_data['manager_email'] = st.text_input("담당 PM 이메일", value=event_data.get('manager_email', ''), key="manager_email_basic")

    event_data['manager_position'] = render_option_menu(
        "담당자 직급",
        ["선임", "책임", "수석"],
        "manager_position"
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

def handle_event_type(event_data):
    col1, col2 = st.columns(2)
    with col1:
        event_data['event_type'] = render_option_menu(
            "용역 유형",
            event_options.EVENT_TYPES,
            "event_type"
        )
    with col2:
        event_data['contract_type'] = render_option_menu(
            "용역 종류",
            event_options.CONTRACT_TYPES,
            "contract_type"
        )

def handle_budget_info(event_data):
    st.header("예산 정보")

    col1, col2 = st.columns(2)
    with col1:
        event_data['contract_status'] = render_option_menu(
            "계약 금액 상태",
            config['CONTRACT_STATUS_OPTIONS'],
            "contract_status"
        )
    with col2:
        vat_options = config['VAT_OPTIONS']
        vat_included = render_option_menu(
            "부가세 포함 여부",
            options=vat_options,
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

    display_budget_details(event_data)

    if event_data['contract_status'] == "추가 예정":
        handle_additional_amount(event_data)

    handle_profit_info(event_data)

def display_budget_details(event_data):
    if event_data['vat_included']:
        original_amount = round(event_data['contract_amount'] / 1.1)
        vat_amount = round(event_data['contract_amount'] - original_amount)
    else:
        original_amount = event_data['contract_amount']
        vat_amount = round(original_amount * 0.1)

    st.write(f"입력된 계약 금액: {format_currency(event_data['contract_amount'])} 원")
    st.write(f"원금: {format_currency(original_amount)} 원")
    st.write(f"부가세: {format_currency(vat_amount)} 원")

def handle_additional_amount(event_data):
    event_data['additional_amount'] = st.number_input(
        "추가 예정 금액 (원)",
        min_value=0,
        value=event_data.get('additional_amount', 0),
        key="additional_amount",
        format="%d"
    )
    st.write(f"입력된 추가 예정 액: {format_currency(event_data['additional_amount'])} 원")

def handle_profit_info(event_data):
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
    original_amount = round(total_amount / 1.1) if event_data['vat_included'] else total_amount
    expected_profit = round(original_amount * (event_data['expected_profit_percentage'] / 100))

    event_data['expected_profit'] = expected_profit

    st.write(f"예상 수익 금액: {format_currency(expected_profit)} 원")

    total_category_budget = sum(component.get('budget', 0) for component in event_data.get('components', {}).values())
    if total_category_budget > event_data['contract_amount']:
        st.warning(f"주의: 카테고리별 예산 총액({format_currency(total_category_budget)} 원)이 총 계약 금액({format_currency(event_data['contract_amount'])} 원)을 초과합니다.")

def handle_video_production(event_data):
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("과업 시작일", 
                                   value=event_data.get('start_date', date.today()), 
                                   key="video_start_date")
    with col2:
        end_date = st.date_input("과업 종료일",
                                 value=max(event_data.get('end_date', start_date), start_date),
                                 min_value=start_date,
                                 key="video_end_date")

    event_data['start_date'] = start_date
    event_data['end_date'] = end_date

    duration = (end_date - start_date).days
    months, days = divmod(duration, 30)
    st.write(f"과업 기간: {months}개월 {days}일")

def handle_offline_event(event_data):
    st.subheader("오프라인 이벤트 정보")

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("시작 날짜",
                                   value=event_data.get('start_date', date.today()),
                                   key="start_date")

    with col2:
        end_date = st.date_input("종료 날짜",
                                 value=event_data.get('end_date', start_date),
                                 min_value=start_date,
                                 key="end_date")

    event_data['start_date'] = start_date
    event_data['end_date'] = end_date

    col3, col4 = st.columns(2)

    with col3:
        event_data['setup_start'] = render_option_menu("셋업 시작일", config['SETUP_OPTIONS'], "setup_start")

    with col4:
        event_data['teardown'] = render_option_menu("철수 마감일", config['TEARDOWN_OPTIONS'], "teardown")

    if event_data['setup_start'] == config['SETUP_OPTIONS'][0]:
        event_data['setup_date'] = start_date - timedelta(days=1)
    else:
        event_data['setup_date'] = start_date

    if event_data['teardown'] == config['TEARDOWN_OPTIONS'][0]:
        event_data['teardown_date'] = end_date
    else:
        event_data['teardown_date'] = end_date + timedelta(days=1)

    st.write(f"셋업 시작일: {event_data['setup_date']}")
    st.write(f"철수 마감일: {event_data['teardown_date']}")

    if event_data['setup_date'] > start_date:
        st.error("셋업 시작일은 이벤트 시작일보다 늦을 수 없습니다.")
    if end_date < start_date:
        st.error("이벤트 종료일은 시작일보다 빠를 수 없습니다.")
    if event_data['teardown_date'] < end_date:
        st.error("철수 마감일은 이벤트 종료일보다 빠를 수 없습니다.")

def venue_info():
    event_data = st.session_state.event_data
    st.header("장소 정보")

    guide_text = """
    - **장소 확정 상태**: 현재 장소 섭외 진행 상황을 선택하세요.
    - **희망하는 장소 유형**: 실내, 실외, 혼합, 온라인 중 선택하세요.
    - **예상 참여 관객 수**: 예상되는 참가자 수를 입력하세요.
    - **장소명과 주소**: 확정된 경우 정확한 정보를, 미확정 시 희망 사항을 입력하세요.
    """
    display_guide(guide_text)

    if event_data['event_type'] == "온라인 콘텐츠":
        handle_online_content_location(event_data)
    else:
        handle_offline_event_venue(event_data)

def handle_online_content_location(event_data):
    event_data['location_needed'] = render_option_menu(
        "로케이션 필요 여부",
        ["필요", "불필요"],
        "location_needed"
    )

    if event_data['location_needed'] == "필요":
        event_data['location_type'] = render_option_menu(
            "로케이션 유형",
            ["프로덕션이 알아서 구해오기", "직접 지정"],
            "location_type"
        )

        if event_data['location_type'] == "프로덕션이 알아서 구해오기":
            event_data['location_preference'] = render_option_menu(
                "로케이션 선호",
                ["실내", "실외"],
                "location_preference"
            )

            if event_data['location_preference'] == "실내":
                event_data['indoor_location_description'] = st.text_area(
                    "실내 로케이션 설명",
                    value=event_data.get('indoor_location_description', ''),
                    help="최소 50자 이상 입력해주세요.",
                    key="indoor_location_description"
                )
            else:
                event_data['outdoor_location_description'] = st.text_area(
                    "실외 로케이션 설명",
                    value=event_data.get('outdoor_location_description', ''),
                    help="최소 50자 이상 입력해주세요.",
                    key="outdoor_location_description"
                )
        else:
            event_data['location_name'] = st.text_input(
                "로케이션 이름",
                value=event_data.get('location_name', ''),
                key="location_name"
            )
            event_data['location_address'] = st.text_input(
                "로케이션 주소",
                value=event_data.get('location_address', ''),
                key="location_address"
            )
            event_data['location_status'] = render_option_menu(
                "로케이션 상태",
                ["확정", "미정"],
                "location_status"
            )

def handle_offline_event_venue(event_data):
    event_data['venue_status'] = render_option_menu(
        "장소 확정 상태",
        config['VENUE_STATUS_OPTIONS'],
        "venue_status"
    )

    event_data['venue_type'] = render_option_menu(
        "희망하는 장소 유형",
        config['VENUE_TYPE_OPTIONS'],
        "venue_type"
    )

    event_data['scale'] = st.number_input(
        "예상 참여 관객 수",
        min_value=0,
        value=event_data.get('scale', 0),
        step=10,
        key="scale"
    )

    if event_data['venue_status'] == "알 수 없는 상태":
        event_data['desired_region'] = st.text_input(
            "희망하는 지역",
            value=event_data.get('desired_region', ''),
            key="desired_region"
        )
        event_data['desired_capacity'] = st.number_input(
            "희망하는 수용 인원",
            min_value=0,
            value=event_data.get('desired_capacity', 0),
            step=10,
            key="desired_capacity"
        )
    else:
        handle_known_venue_status(event_data)

def handle_known_venue_status(event_data):
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
            st.experimental_rerun()

    if st.button("장소 추가"):
        event_data['venues'].append({'name': '', 'address': ''})
        st.experimental_rerun()

    handle_venue_facilities(event_data)

def handle_venue_facilities(event_data):
    if event_data['venue_type'] in ["실내", "혼합"]:
        facility_options = ["음향 시설", "조명 시설", "LED 시설", "빔프로젝트 시설", "주차", "Wifi", "기타"]
        event_data['facilities'] = st.multiselect("행사장 자체 보유 시설", facility_options, default=event_data.get('facilities', []), key="facilities")

        if "기타" in event_data['facilities']:
            event_data['other_facilities'] = st.text_input("기타 시설 입력", key="other_facility_input")

def service_components():
    event_data = st.session_state.event_data
    st.header("용역 구성 요소")

    event_name = event_data.get('event_name', '무제')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    summary_filename = f"이벤트_기획_정의서_{event_name}_{timestamp}.xlsx"

    try:
        create_excel_summary(event_data, summary_filename)
        st.success(f"엑셀 정의서가 성공적으로 생성되었습니다: {summary_filename}")

        with open(summary_filename, "rb") as file:
            st.download_button(label="전체 행사 요약 정의서 다운로드", data=file, file_name=summary_filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

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

def create_excel_summary(event_data, filename):
    # Implementation to create the summary Excel file
    pass

def create_category_excel(event_data, category, component, filename):
    # Implementation to create the category-specific Excel file
    pass

def check_required_fields(step):
    event_data = st.session_state.event_data
    missing_fields = []
    required_fields = config['REQUIRED_FIELDS']

    if step == 0:  # 기본 정보
        for field in required_fields['basic_info']:
            if not event_data.get(field):
                missing_fields.append(field)

    elif step == 1:  # 장소 정보
        if event_data.get('event_type') == "온라인 콘텐츠":
            for field in required_fields['online_content']:
                if not event_data.get(field):
                    missing_fields.append(field)
            if event_data.get('location_needed') == "필요":
                if event_data.get('location_type') == "프로덕션이 알아서 구해오기":
                    if event_data.get('location_preference') == "실내" and len(event_data.get('indoor_location_description', '')) < 50:
                        missing_fields.append('indoor_location_description')
                    elif event_data.get('location_preference') == "실외" and len(event_data.get('outdoor_location_description', '')) < 50:
                        missing_fields.append('outdoor_location_description')
                elif event_data.get('location_type') == "직접 지정":
                    for field in required_fields['online_content_location']:
                        if not event_data.get(field):
                            missing_fields.append(field)
        else:  # 오프라인 이벤트
            for field in required_fields['offline_event']:
                if not event_data.get(field):
                    missing_fields.append(field)
            if event_data.get('venue_status') == "알 수 없는 상태":
                if not event_data.get('desired_region'):
                    missing_fields.append('desired_region')
            elif event_data.get('venue_status') != "알 수 없는 상태":
                if not event_data.get('venues'):
                    missing_fields.append('venues')
                else:
                    for i, venue in enumerate(event_data['venues']):
                        if not venue.get('name'):
                            missing_fields.append(f'venues[{i}].name')
                        if not venue.get('address'):
                            missing_fields.append(f'venues[{i}].address')

    elif step == 2:  # 용역 구성 요소
        for field in required_fields['components']:
            if not event_data.get(field):
                missing_fields.append(field)
        if event_data.get('selected_categories'):
            for category in event_data.get('selected_categories'):
                if category not in event_data.get('components', {}):
                    missing_fields.append(f'components.{category}')
                else:
                    component = event_data['components'][category]
                    if not component.get('status'):
                        missing_fields.append(f'components.{category}.status')
                    if not component.get('items'):
                        missing_fields.append(f'components.{category}.items')

    return len(missing_fields) == 0, missing_fields

def highlight_missing_fields(missing_fields):
    field_names = config['FIELD_NAMES']

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

def service_components():
    event_data = st.session_state.event_data
    st.header("용역 구성 요소")

    guide_text = """
    - 필요한 모든 카테고리를 선택하세요.
    - 각 카테고리에 대해 상세 정보를 입력하세요.
    - 예산과 항목을 정확히 기입해주세요.
    """
    display_guide(guide_text)

    selected_categories = st.multiselect(
        "카테고리 선택",
        options=config['CATEGORIES'],
        default=event_data.get('selected_categories', []),
        key="selected_categories"
    )
    event_data['selected_categories'] = selected_categories

    for category in selected_categories:
        st.subheader(category)
        if category not in event_data.get('components', {}):
            event_data['components'][category] = {}
        
        component = event_data['components'][category]
        
        component['status'] = st.selectbox(
            f"{category} 상태",
            options=["확정", "미정"],
            key=f"{category}_status"
        )
        
        component['budget'] = st.number_input(
            f"{category} 예산",
            min_value=0,
            value=component.get('budget', 0),
            step=1000,
            format="%d",
            key=f"{category}_budget"
        )
        
        items = component.get('items', [])
        for i, item in enumerate(items):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                item['name'] = st.text_input("항목명", value=item['name'], key=f"{category}_item_name_{i}")
            with col2:
                item['quantity'] = st.number_input("수량", min_value=1, value=item['quantity'], key=f"{category}_item_quantity_{i}")
            with col3:
                item['unit'] = st.text_input("단위", value=item['unit'], key=f"{category}_item_unit_{i}")
            with col4:
                if st.button("삭제", key=f"{category}_item_delete_{i}"):
                    items.pop(i)
                    st.experimental_rerun()
        
        if st.button("항목 추가", key=f"{category}_add_item"):
            items.append({"name": "", "quantity": 1, "unit": ""})
            st.experimental_rerun()
        
        component['items'] = items

    save_event_data(event_data)