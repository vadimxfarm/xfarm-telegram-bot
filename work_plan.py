from datetime import datetime

# База агрономічних робіт за культурами
AGRONOMY_PLAN = {
    "пшениця": [
        {"month": 9, "task": "Підготовка ґрунту під озиму пшеницю"},
        {"month": 10, "task": "Сівба озимої пшениці"},
        {"month": 3, "task": "Внесення азотних добрив"},
        {"month": 6, "task": "Захист від хвороб (фунгіциди)"},
        {"month": 7, "task": "Збір врожаю"}
    ],
    "кукурудза": [
        {"month": 4, "task": "Підготовка насіння (протруйнування)"},
        {"month": 5, "task": "Сівба кукурудзи"},
        {"month": 6, "task": "Міжрядна обробка"},
        {"month": 7, "task": "Позакореневе підживлення"},
        {"month": 9, "task": "Збір врожаю"}
    ],
    "соняшник": [
        {"month": 4, "task": "Обробка ґрунту"},
        {"month": 5, "task": "Сівба соняшнику"},
        {"month": 6, "task": "Захист від бур’янів"},
        {"month": 8, "task": "Контроль шкідників"},
        {"month": 9, "task": "Збір врожаю"}
    ],
    "буряк": [
        {"month": 4, "task": "Підготовка насіння"},
        {"month": 5, "task": "Сівба цукрових буряків"},
        {"month": 6, "task": "Прополка та захист від шкідників"},
        {"month": 8, "task": "Підживлення калійними добривами"},
        {"month": 9, "task": "Збір врожаю"}
    ]
}

def get_work_plan(crops: str):
    """Повертає список робіт для вказаних культур у поточному місяці."""
    current_month = datetime.now().month
    tasks = []
    
    # Розділяємо культури (наприклад: "пшениця, кукурудза")
    crop_list = [c.strip().lower() for c in crops.split(",") if c.strip()]
    
    for crop in crop_list:
        if crop in AGRONOMY_PLAN:
            for item in AGRONOMY_PLAN[crop]:
                if item["month"] == current_month:
                    tasks.append(f"• {item['task']} ({crop})")
    
    return tasks if tasks else ["Немає запланованих робіт у цьому місяці."]