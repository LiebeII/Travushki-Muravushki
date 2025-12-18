def format_number(number: int) -> str:
    """
    Форматирует число в удобочитаемый вид с заглавными суффиксами
    Пример: 1500 -> 1.5K, 2500000 -> 2.5M
    """
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"
    else:
        return str(number)