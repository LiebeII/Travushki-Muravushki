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


def conditional_combos_counter(
        whole_combos_dict: Dict[int, Dict[str, int]], 
        layout_map: Dict[str, Any], 
        data: Any, 
        max_combos_length: int = 4) -> Tuple[Dict[int, Dict[str, int]], Dict[int, Dict[str, int]], Dict[int, Dict[str, int]], Dict[int, Dict[str, float]]]:
    '''
    Анализирует комбинации символов с расширенной классификацией
    '''
    one_hand_combos = {}
    comfort_combos = {}
    partial_comfort_combos = {}
    comfort_scores = {}
    
    for combos_length in range(2, max_combos_length + 1):
        one_hand_combos[combos_length] = {}
        comfort_combos[combos_length] = {}
        partial_comfort_combos[combos_length] = {}
        comfort_scores[combos_length] = {}
    
    for current_combos_length in range(2, max_combos_length + 1):
        combos_dict = whole_combos_dict.get(current_combos_length, {})
        
        for combo, encounters in combos_dict.items():
            # Пропускаем комбинации с неподдерживаемыми символами
            valid_combo = True
            for char in combo:
                if scancode_from_char(char, layout_map) is None:
                    valid_combo = False
                    break
            
            if not valid_combo:
                continue
            
            # Рассчитываем оценку удобства
            comfort_score, category = data.calculate_combo_comfort_score(combo, layout_map)
            comfort_scores[current_combos_length][combo] = comfort_score
            
            # Классифицируем по удобству
            if category == 'comfortable':
                if combo in comfort_combos[current_combos_length]:
                    comfort_combos[current_combos_length][combo] += encounters
                else:
                    comfort_combos[current_combos_length][combo] = encounters
            elif category == 'partially_comfortable':
                if combo in partial_comfort_combos[current_combos_length]:
                    partial_comfort_combos[current_combos_length][combo] += encounters
                else:
                    partial_comfort_combos[current_combos_length][combo] = encounters
            
            # Проверяем одноручные комбинации
            one_hand_valid = True
            hands_used = set()
            
            for i in range(len(combo) - 1):
                scancode1 = scancode_from_char(combo[i], layout_map)
                scancode2 = scancode_from_char(combo[i + 1], layout_map)
                
                if scancode1 is None or scancode2 is None:
                    one_hand_valid = False
                    break
                    
                hand1 = key_from_value(scancode1, data.key_hand)
                hand2 = key_from_value(scancode2, data.key_hand)
                
                if hand1 is None or hand2 is None:
                    one_hand_valid = False
                    break
                
                hands_used.add(hand1)
                hands_used.add(hand2)
                
                # Для одноручной комбинации все символы должны быть на одной руке
                if len(hands_used) > 1:
                    one_hand_valid = False
                    break
            
            if one_hand_valid and len(hands_used) == 1:
                if combo in one_hand_combos[current_combos_length]:
                    one_hand_combos[current_combos_length][combo] += encounters
                else:
                    one_hand_combos[current_combos_length][combo] = encounters
    
    return one_hand_combos, comfort_combos, partial_comfort_combos, comfort_scores


# Эти функции должны быть в layouts/layout_data.py, но они здесь для удобства
def scancode_from_char(char: str, layout_map: Dict[str, Any]) -> Any:
    '''
    Получает: символ, словарь
    Возвращает: сканкод для символа с учетом модификаторов
    '''
    if char in layout_map:
        scancode_info = layout_map[char]
        if isinstance(scancode_info, dict):
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


def combos_dict_to_combos_count_dict(
        hand_combos: Dict[int, Dict[str, int]], 
        comfort_combos: Dict[int, Dict[str, int]],
        partial_comfort_combos: Dict[int, Dict[str, int]]) -> Tuple[Dict[int, int], Dict[int, int], Dict[int, int]]:
    '''
    Преобразует словари комбинаций в словари количества комбинаций по длинам
    '''
    hand_combos_count, comfort_combos_count, partial_comfort_count = {}, {}, {}
    
    for combos_length in range(2, 5):
        hand_combos_count[combos_length] = sum(hand_combos.get(combos_length, {}).values())
        comfort_combos_count[combos_length] = sum(comfort_combos.get(combos_length, {}).values())
        partial_comfort_count[combos_length] = sum(partial_comfort_combos.get(combos_length, {}).values())
    
    return hand_combos_count, comfort_combos_count, partial_comfort_count