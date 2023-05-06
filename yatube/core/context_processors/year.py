from datetime import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    today_year = datetime.now().year
    return {
        'year': today_year
    }
