import os

# 디렉토리와 파일 리스트
structure = {
    "event_planner": [
        "main.py",
        "requirements.txt",
        "database.py",
        "utils.py",
        "ui_components.py",
        "excel_generator.py",
        {"config": [
            "categories.json",
            "app_config.py"
        ]},
        {"pages": [
            "basic_info.py",
            "venue_info.py",
            "budget_info.py",
            "service_components.py",
            "progress_tracking.py"
        ]},
        {"data": [
            "event_planner.db"
        ]}
    ]
}

def create_structure(base_path, structure):
    for item in structure:
        if isinstance(item, dict):
            for dir_name, sub_items in item.items():
                dir_path = os.path.join(base_path, dir_name)
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                create_structure(dir_path, sub_items)
        else:
            file_path = os.path.join(base_path, item)
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    pass

base_path = "."
create_structure(base_path, structure)
print("구조 생성 완료")

