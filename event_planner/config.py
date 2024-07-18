import os

EVENT_TABLE_COLUMNS = [
    'event_name', 'client_name', 'manager_name', 'manager_contact', 'event_type',
    'contract_type', 'scale', 'start_date', 'end_date', 'setup_start', 'teardown',
    'venue_name', 'venue_type', 'address', 'capacity', 'facilities',
    'contract_amount', 'expected_profit', 'components'
]

JSON_PATH = os.path.join(os.path.dirname(__file__), 'item_options.json')
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

config = {
    'CONTRACT_STATUS_OPTIONS': ["확정", "추가 예정"],
    'VAT_OPTIONS': ["포함", "미포함"],
    'SETUP_OPTIONS': ["전일", "당일"],
    'TEARDOWN_OPTIONS': ["당일", "익일"],
    'REQUIRED_FIELDS': {
        'basic_info': ['event_name', 'client_name', 'manager_name', 'manager_contact', 'event_type', 'contract_type'],
        'online_content': ['event_name', 'client_name', 'manager_name', 'manager_contact', 'event_type', 'contract_type', 'online_platform', 'streaming_method'],
        'online_content_location': ['location_name', 'location_status'],
        'offline_event': ['event_name', 'client_name', 'manager_name', 'manager_contact', 'event_type', 'contract_type', 'venue_status', 'venue_type'],
        'components': ['selected_categories']
    },
    'FIELD_NAMES': {
        'event_name': '용역명',
        'client_name': '클라이언트명',
        'manager_name': '담당 PM',
        'manager_contact': '담당자 연락처',
        'event_type': '용역 유형',
        'contract_type': '용역 종류',
        'online_platform': '온라인 플랫폼',
        'streaming_method': '스트리밍 방식',
        'location_name': '촬영 로케이션',
        'location_status': '로케이션 상태',
        'venue_status': '장소 확정 상태',
        'venue_type': '장소 유형',
        'selected_categories': '카테고리'
    }
}
