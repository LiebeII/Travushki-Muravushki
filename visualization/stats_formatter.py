def format_number(num: int) -> str:
    """
    Форматирует числа: заменяет тысячные части на k, миллионные на m
    """
    if num >= 1000000:
        return f"{num/1000000:.1f}m".replace('.0m', 'm')
    elif num >= 1000:
        return f"{num/1000:.1f}k".replace('.0k', 'k')
    else:
        return str(num)


def format_percent(num: float) -> str:
    """
    Форматирует проценты
    """
    return f"{num:.1f}%"