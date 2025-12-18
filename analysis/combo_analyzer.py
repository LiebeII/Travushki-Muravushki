from typing import Dict, Tuple, Set, Any
from collections import defaultdict


def combos_counter(words_set: Set[str], max_length: int = 4) -> Dict[int, Dict[str, int]]:
    '''
    Получает множество со словами и максимальную длину комбинаций
    Возвращает словарь combos: длина_комбо -> {комбинация: количество}
    Анализирует по словам, а не по символам
    '''
    combos = {}
    
    for current_combos_length in range(2, max_length + 1):
        combos[current_combos_length] = defaultdict(int)
    
    for word in words_set:
        # Пропускаем короткие слова
        if len(word) < 2:
            continue
            
        # Анализируем комбинации символов внутри слова
        for current_combos_length in range(2, max_length + 1):
            if len(word) >= current_combos_length:
                for letter_number in range(len(word) - current_combos_length + 1):
                    combo = word[letter_number:letter_number + current_combos_length]
                    combos[current_combos_length][combo] += 1
    
    return combos


def scancode_from_char(char: str, layout_map: Dict[str, Any]) -> Any:
    '''
    Получает: символ, словарь
    Возвращает: сканкод для символа с учетом модификаторов
    '''
    if char in layout_map:
        scancode_info = layout_map[char]
        if isinstance(scancode_info, dict):
            # Возвращаем сканкод независимо от модификаторов
            return scancode_info.get('scancode')
        elif isinstance(scancode_info, list) and scancode_info:
            return scancode_info[0]
        else:
            return scancode_info
    return None


def key_from_value(item, the_dict):
    '''
    Получает: сканкод, словарь
    Возвращает: ключ, в значения которого входит сканкод
    '''
    for key, value in the_dict.items():
        if item in value:
            return key
    return None