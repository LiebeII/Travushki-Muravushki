import re
from typing import Dict, Tuple, List, Set, Any, Optional
from collections import defaultdict


def key_from_value(item, the_dict):
    '''
    Получает: сканкод, словарь
    Возвращает: ключ, в значения которого входит сканкод
    '''
    for key, value in the_dict.items():
        if item in value:
            return key
    return None


def scancode_from_char(char: str, layout_map: Dict[str, Any]) -> Optional[str]:
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


def get_modifiers_for_char(char: str, layout_map: Dict[str, Any]) -> List[str]:
    '''
    Возвращает список модификаторов для символа
    '''
    if char in layout_map:
        scancode_info = layout_map[char]
        if isinstance(scancode_info, dict):
            return scancode_info.get('modifiers', [])
    return []


class LayoutData:
    """Класс для хранения данных о раскладках"""
    
    def __init__(self):
        # Карты всех раскладок
        self.layout_maps = {
            'ЙЦУКЕН': self.create_icuken_layout_map(),
            'Скоропись': self.create_scoropis_layout_map(),
            'Фонетическая (яВерт)': self.create_phonetic_vert_layout_map(),
            'Вызов': self.create_vyzov_layout_map(),
            'QWERTY': self.create_qwerty_layout_map(),
            'Dvorak': self.create_dvorak_layout_map(),
            'Colemak': self.create_colemak_layout_map(),
            'Workman': self.create_workman_layout_map()
        }
        
        # Улучшенное соответствие сканкодов пальцам для эргономики
        self.key_finger = {
            'left_pinky': ['02', '10', '1E', '2C'],
            'left_ring': ['03', '11', '1F', '2D'],
            'left_middle': ['04', '12', '20', '2E'],
            'left_index': ['05', '13', '21', '2F', '06', '14', '22', '30'],
            'left_thumb': ['39', '56'],
            
            'right_index': ['07', '15', '23', '31', '08', '16', '24', '32'],
            'right_middle': ['09', '17', '25', '33'],
            'right_ring': ['0A', '18', '26', '34'],
            'right_pinky': ['0B', '19', '27', '35', '0C', '1A', '28', '36'],
            'right_thumb': ['38', 'E0', 'E1', 'E2']
        }
        
        # Соответствие сканкодов рукам
        self.key_hand = {
            'left': ['02', '03', '04', '05', '06', '10', '11', '12', '13', '14', 
                    '1E', '1F', '20', '21', '22', '2C', '2D', '2E', '2F', '30',
                    '39', '56'],
            'right': ['07', '08', '09', '0A', '0B', '0C', '15', '16', '17', '18',
                     '19', '1A', '23', '24', '25', '26', '27', '28', '31', '32',
                     '33', '34', '35', '36', '38']
        }
        
        # Штрафы для пальцев (чем больше штраф, тем менее удобен палец)
        self.finger_penalties = {
            'left_pinky': 4.0,
            'left_ring': 2.0,
            'left_middle': 1.0,
            'left_index': 1.5,
            'left_thumb': 0.5,
            'right_index': 1.5,
            'right_middle': 1.0,
            'right_ring': 2.0,
            'right_pinky': 4.0,
            'right_thumb': 0.5
        }
        
        # Порядок пальцев для определения направления
        self.finger_order = [
            'left_pinky', 'left_ring', 'left_middle', 'left_index',
            'right_index', 'right_middle', 'right_ring', 'right_pinky'
        ]
    
    def calculate_finger_direction(self, finger1: str, finger2: str) -> int:
        """
        Определяет направление движения пальцев:
        1 = от мизинца к указательному (удобно)
        0 = то же место
        -1 = от указательного к мизинцу (менее удобно)
        None = разные руки
        """
        if finger1 not in self.finger_order or finger2 not in self.finger_order:
            return None
        
        idx1 = self.finger_order.index(finger1)
        idx2 = self.finger_order.index(finger2)
        
        # Проверяем, на одной ли руке пальцы
        left_fingers = ['left_pinky', 'left_ring', 'left_middle', 'left_index']
        right_fingers = ['right_index', 'right_middle', 'right_ring', 'right_pinky']
        
        is_left_hand = finger1 in left_fingers and finger2 in left_fingers
        is_right_hand = finger1 in right_fingers and finger2 in right_fingers
        
        if not (is_left_hand or is_right_hand):
            return None  # Разные руки
        
        if idx1 == idx2:
            return 0  # Тот же палец
        
        direction = idx2 - idx1
        
        # Для левой руки: от мизинца (0) к указательному (3) - положительное направление
        # Для правой руки: от указательного (4) к мизинцу (7) - положительное направление
        if is_left_hand:
            return 1 if direction > 0 else -1
        else:  # правая рука
            return 1 if direction < 0 else -1
    
    def calculate_combo_comfort_score(self, combo: str, layout_map: Dict[str, Any]) -> Tuple[float, str]:
        """
        Улучшенный расчет удобства комбинации по новым правилам:
        
        Правила:
        1. Удобные - пальцы одной руки идут в порядке от мизинца к указательному (во внутрь)
        2. Частично удобные - смена направления пальцев, но той же руки
        3. Неудобные - разные руки или неподходящие комбинации
        """
        if len(combo) < 2:
            return 0.0, 'uncomfortable'
        
        hand_history = []
        finger_history = []
        
        # Собираем информацию о пальцах и руках
        for char in combo:
            scancode = scancode_from_char(char, layout_map)
            
            if scancode is None:
                return 0.0, 'uncomfortable'
            
            hand = key_from_value(scancode, self.key_hand)
            finger = key_from_value(scancode, self.key_finger)
            
            if hand is None or finger is None:
                return 0.0, 'uncomfortable'
            
            hand_history.append(hand)
            finger_history.append(finger)
        
        # Анализируем комбинацию
        if len(combo) == 2:
            # Для двухсимвольных комбинаций
            finger1 = finger_history[0]
            finger2 = finger_history[1]
            hand1 = hand_history[0]
            hand2 = hand_history[1]
            
            # Проверяем, на одной ли руке
            if hand1 != hand2:
                return 0.0, 'uncomfortable'  # Разные руки - неудобно
            
            # Определяем направление
            direction = self.calculate_finger_direction(finger1, finger2)
            
            if direction == 1:
                return 1.0, 'comfortable'  # От мизинца к указательному - удобно
            elif direction == -1:
                return 0.5, 'partially_comfortable'  # Обратное направление - частично удобно
            elif direction == 0:
                return 0.3, 'partially_comfortable'  # Тот же палец - частично удобно
            else:
                return 0.0, 'uncomfortable'
        
        else:
            # Для комбинаций длиной 3-4 символа
            # Проверяем, что все символы на одной руке
            if len(set(hand_history)) > 1:
                return 0.0, 'uncomfortable'  # Разные руки - неудобно
            
            # Анализируем направления между последовательными парами
            directions = []
            for i in range(len(finger_history) - 1):
                direction = self.calculate_finger_direction(finger_history[i], finger_history[i + 1])
                if direction is None:
                    return 0.0, 'uncomfortable'
                directions.append(direction)
            
            # Проверяем, все ли направления удобные (1)
            if all(d == 1 for d in directions):
                return 1.0, 'comfortable'
            # Проверяем, есть ли смена направления
            elif any(d1 * d2 < 0 for d1, d2 in zip(directions[:-1], directions[1:])):
                return 0.5, 'partially_comfortable'
            # Все направления одинаковые, но не удобные
            elif all(d == -1 for d in directions):
                return 0.3, 'partially_comfortable'
            else:
                return 0.0, 'uncomfortable'
    
    def calculate_finger_load(self, text: str, layout_map: Dict[str, Any]) -> Dict[str, int]:
        """Подсчет нагрузки на пальцы (количество кликов)"""
        finger_load = defaultdict(int)
        
        for char in text:
            if char.strip():
                scancode = scancode_from_char(char, layout_map)
                if scancode:
                    finger = key_from_value(scancode, self.key_finger)
                    if finger:
                        finger_load[finger] += 1
        
        return finger_load
    
    def calculate_finger_penalties_total(self, text: str, layout_map: Dict[str, Any]) -> float:
        """Подсчет общего штрафа на пальцы"""
        total_penalty = 0.0
        
        for char in text:
            if char.strip():
                scancode = scancode_from_char(char, layout_map)
                if scancode:
                    finger = key_from_value(scancode, self.key_finger)
                    if finger and finger in self.finger_penalties:
                        total_penalty += self.finger_penalties[finger]
        
        return total_penalty
    
    def calculate_hand_penalty_distribution(self, text: str, layout_map: Dict[str, Any]) -> Dict[str, float]:
        """Подсчет распределения штрафов между руками"""
        hand_penalties = {'left': 0.0, 'right': 0.0}
        
        for char in text:
            if char.strip():
                scancode = scancode_from_char(char, layout_map)
                if scancode:
                    finger = key_from_value(scancode, self.key_finger)
                    hand = key_from_value(scancode, self.key_hand)
                    if finger and finger in self.finger_penalties and hand in hand_penalties:
                        hand_penalties[hand] += self.finger_penalties[finger]
        
        # Нормализуем
        total = sum(hand_penalties.values())
        if total > 0:
            hand_penalties['left_percent'] = (hand_penalties['left'] / total) * 100
            hand_penalties['right_percent'] = (hand_penalties['right'] / total) * 100
        
        return hand_penalties
    
    def analyze_two_char_combinations(self, combos_dict: Dict[str, int], layout_map: Dict[str, Any]) -> Dict[str, int]:
        """
        Анализ двухсимвольных комбинаций:
        - Одноручные комбинации
        - Удобные одноручные комбинации (от мизинца к указательному)
        - Неудобные: все остальные одноручные
        """
        results = {
            'one_hand_total': 0,
            'comfortable_one_hand': 0,
            'uncomfortable_one_hand': 0
        }
        
        for combo, count in combos_dict.items():
            if len(combo) != 2:
                continue
            
            scancode1 = scancode_from_char(combo[0], layout_map)
            scancode2 = scancode_from_char(combo[1], layout_map)
            
            if scancode1 is None or scancode2 is None:
                continue
            
            hand1 = key_from_value(scancode1, self.key_hand)
            hand2 = key_from_value(scancode2, self.key_hand)
            
            if hand1 is None or hand2 is None:
                continue
            
            # Проверяем одноручность
            if hand1 == hand2:
                results['one_hand_total'] += count
                
                # Определяем удобство
                finger1 = key_from_value(scancode1, self.key_finger)
                finger2 = key_from_value(scancode2, self.key_finger)
                
                if finger1 and finger2:
                    direction = self.calculate_finger_direction(finger1, finger2)
                    if direction == 1:
                        results['comfortable_one_hand'] += count
                    else:
                        # Все остальное - неудобно (обратное направление, тот же палец)
                        results['uncomfortable_one_hand'] += count
                else:
                    results['uncomfortable_one_hand'] += count
        
        return results
    
    def create_icuken_layout_map(self) -> Dict[str, Any]:
        """Создает полную карту раскладки ЙЦУКЕН с русскими и английскими символами"""
        return {
            # Русские буквы (нижний регистр)
            'й': {'scancode': '10', 'modifiers': []},
            'ц': {'scancode': '11', 'modifiers': []},
            'у': {'scancode': '12', 'modifiers': []},
            'к': {'scancode': '13', 'modifiers': []},
            'е': {'scancode': '14', 'modifiers': []},
            'н': {'scancode': '15', 'modifiers': []},
            'г': {'scancode': '16', 'modifiers': []},
            'ш': {'scancode': '17', 'modifiers': []},
            'щ': {'scancode': '18', 'modifiers': []},
            'з': {'scancode': '19', 'modifiers': []},
            'х': {'scancode': '1A', 'modifiers': []},
            'ъ': {'scancode': '1B', 'modifiers': []},
            'ф': {'scancode': '1E', 'modifiers': []},
            'ы': {'scancode': '1F', 'modifiers': []},
            'в': {'scancode': '20', 'modifiers': []},
            'а': {'scancode': '21', 'modifiers': []},
            'п': {'scancode': '22', 'modifiers': []},
            'р': {'scancode': '23', 'modifiers': []},
            'о': {'scancode': '24', 'modifiers': []},
            'л': {'scancode': '25', 'modifiers': []},
            'д': {'scancode': '26', 'modifiers': []},
            'ж': {'scancode': '27', 'modifiers': []},
            'э': {'scancode': '28', 'modifiers': []},
            'я': {'scancode': '2C', 'modifiers': []},
            'ч': {'scancode': '2D', 'modifiers': []},
            'с': {'scancode': '2E', 'modifiers': []},
            'м': {'scancode': '2F', 'modifiers': []},
            'и': {'scancode': '30', 'modifiers': []},
            'т': {'scancode': '31', 'modifiers': []},
            'ь': {'scancode': '32', 'modifiers': []},
            'б': {'scancode': '33', 'modifiers': []},
            'ю': {'scancode': '34', 'modifiers': []},
            'ё': {'scancode': '29', 'modifiers': []},
            
            # Заглавные русские буквы (Shift + буква)
            'Й': {'scancode': '10', 'modifiers': ['shift']},
            'Ц': {'scancode': '11', 'modifiers': ['shift']},
            'У': {'scancode': '12', 'modifiers': ['shift']},
            'К': {'scancode': '13', 'modifiers': ['shift']},
            'Е': {'scancode': '14', 'modifiers': ['shift']},
            'Н': {'scancode': '15', 'modifiers': ['shift']},
            'Г': {'scancode': '16', 'modifiers': ['shift']},
            'Ш': {'scancode': '17', 'modifiers': ['shift']},
            'Щ': {'scancode': '18', 'modifiers': ['shift']},
            'З': {'scancode': '19', 'modifiers': ['shift']},
            'Х': {'scancode': '1A', 'modifiers': ['shift']},
            'Ъ': {'scancode': '1B', 'modifiers': ['shift']},
            'Ф': {'scancode': '1E', 'modifiers': ['shift']},
            'Ы': {'scancode': '1F', 'modifiers': ['shift']},
            'В': {'scancode': '20', 'modifiers': ['shift']},
            'А': {'scancode': '21', 'modifiers': ['shift']},
            'П': {'scancode': '22', 'modifiers': ['shift']},
            'Р': {'scancode': '23', 'modifiers': ['shift']},
            'О': {'scancode': '24', 'modifiers': ['shift']},
            'Л': {'scancode': '25', 'modifiers': ['shift']},
            'Д': {'scancode': '26', 'modifiers': ['shift']},
            'Ж': {'scancode': '27', 'modifiers': ['shift']},
            'Э': {'scancode': '28', 'modifiers': ['shift']},
            'Я': {'scancode': '2C', 'modifiers': ['shift']},
            'Ч': {'scancode': '2D', 'modifiers': ['shift']},
            'С': {'scancode': '2E', 'modifiers': ['shift']},
            'М': {'scancode': '2F', 'modifiers': ['shift']},
            'И': {'scancode': '30', 'modifiers': ['shift']},
            'Т': {'scancode': '31', 'modifiers': ['shift']},
            'Ь': {'scancode': '32', 'modifiers': ['shift']},
            'Б': {'scancode': '33', 'modifiers': ['shift']},
            'Ю': {'scancode': '34', 'modifiers': ['shift']},
            'Ё': {'scancode': '29', 'modifiers': ['shift']},
            
            # Латинские буквы (нижний регистр) - для смешанного текста
            'q': {'scancode': '10', 'modifiers': []},
            'w': {'scancode': '11', 'modifiers': []},
            'e': {'scancode': '12', 'modifiers': []},
            'r': {'scancode': '13', 'modifiers': []},
            't': {'scancode': '14', 'modifiers': []},
            'y': {'scancode': '15', 'modifiers': []},
            'u': {'scancode': '16', 'modifiers': []},
            'i': {'scancode': '17', 'modifiers': []},
            'o': {'scancode': '18', 'modifiers': []},
            'p': {'scancode': '19', 'modifiers': []},
            'a': {'scancode': '1E', 'modifiers': []},
            's': {'scancode': '1F', 'modifiers': []},
            'd': {'scancode': '20', 'modifiers': []},
            'f': {'scancode': '21', 'modifiers': []},
            'g': {'scancode': '22', 'modifiers': []},
            'h': {'scancode': '23', 'modifiers': []},
            'j': {'scancode': '24', 'modifiers': []},
            'k': {'scancode': '25', 'modifiers': []},
            'l': {'scancode': '26', 'modifiers': []},
            'z': {'scancode': '2C', 'modifiers': []},
            'x': {'scancode': '2D', 'modifiers': []},
            'c': {'scancode': '2E', 'modifiers': []},
            'v': {'scancode': '2F', 'modifiers': []},
            'b': {'scancode': '30', 'modifiers': []},
            'n': {'scancode': '31', 'modifiers': []},
            'm': {'scancode': '32', 'modifiers': []},
            
            # Заглавные латинские буквы
            'Q': {'scancode': '10', 'modifiers': ['shift']},
            'W': {'scancode': '11', 'modifiers': ['shift']},
            'E': {'scancode': '12', 'modifiers': ['shift']},
            'R': {'scancode': '13', 'modifiers': ['shift']},
            'T': {'scancode': '14', 'modifiers': ['shift']},
            'Y': {'scancode': '15', 'modifiers': ['shift']},
            'U': {'scancode': '16', 'modifiers': ['shift']},
            'I': {'scancode': '17', 'modifiers': ['shift']},
            'O': {'scancode': '18', 'modifiers': ['shift']},
            'P': {'scancode': '19', 'modifiers': ['shift']},
            'A': {'scancode': '1E', 'modifiers': ['shift']},
            'S': {'scancode': '1F', 'modifiers': ['shift']},
            'D': {'scancode': '20', 'modifiers': ['shift']},
            'F': {'scancode': '21', 'modifiers': ['shift']},
            'G': {'scancode': '22', 'modifiers': ['shift']},
            'H': {'scancode': '23', 'modifiers': ['shift']},
            'J': {'scancode': '24', 'modifiers': ['shift']},
            'K': {'scancode': '25', 'modifiers': ['shift']},
            'L': {'scancode': '26', 'modifiers': ['shift']},
            'Z': {'scancode': '2C', 'modifiers': ['shift']},
            'X': {'scancode': '2D', 'modifiers': ['shift']},
            'C': {'scancode': '2E', 'modifiers': ['shift']},
            'V': {'scancode': '2F', 'modifiers': ['shift']},
            'B': {'scancode': '30', 'modifiers': ['shift']},
            'N': {'scancode': '31', 'modifiers': ['shift']},
            'M': {'scancode': '32', 'modifiers': ['shift']},
            
            # Цифры и специальные символы верхнего ряда
            '`': {'scancode': '29', 'modifiers': []},
            '~': {'scancode': '29', 'modifiers': ['shift']},
            '1': {'scancode': '02', 'modifiers': []},
            '!': {'scancode': '02', 'modifiers': ['shift']},
            '2': {'scancode': '03', 'modifiers': []},
            '@': {'scancode': '03', 'modifiers': ['shift']},
            '3': {'scancode': '04', 'modifiers': []},
            '#': {'scancode': '04', 'modifiers': ['shift']},
            '4': {'scancode': '05', 'modifiers': []},
            '$': {'scancode': '05', 'modifiers': ['shift']},
            '5': {'scancode': '06', 'modifiers': []},
            '%': {'scancode': '06', 'modifiers': ['shift']},
            '6': {'scancode': '07', 'modifiers': []},
            '^': {'scancode': '07', 'modifiers': ['shift']},
            '7': {'scancode': '08', 'modifiers': []},
            '&': {'scancode': '08', 'modifiers': ['shift']},
            '8': {'scancode': '09', 'modifiers': []},
            '*': {'scancode': '09', 'modifiers': ['shift']},
            '9': {'scancode': '0A', 'modifiers': []},
            '(': {'scancode': '0A', 'modifiers': ['shift']},
            '0': {'scancode': '0B', 'modifiers': []},
            ')': {'scancode': '0B', 'modifiers': ['shift']},
            '-': {'scancode': '0C', 'modifiers': []},
            '_': {'scancode': '0C', 'modifiers': ['shift']},
            '=': {'scancode': '0D', 'modifiers': []},
            '+': {'scancode': '0D', 'modifiers': ['shift']},
            
            # Специальные символы
            ' ': {'scancode': '39', 'modifiers': []},
            '[': {'scancode': '1A', 'modifiers': []},
            ']': {'scancode': '1B', 'modifiers': []},
            '{': {'scancode': '1A', 'modifiers': ['shift']},
            '}': {'scancode': '1B', 'modifiers': ['shift']},
            '\\': {'scancode': '2B', 'modifiers': []},
            '|': {'scancode': '2B', 'modifiers': ['shift']},
            ';': {'scancode': '27', 'modifiers': []},
            ':': {'scancode': '27', 'modifiers': ['shift']},
            "'": {'scancode': '28', 'modifiers': []},
            '"': {'scancode': '28', 'modifiers': ['shift']},
            ',': {'scancode': '33', 'modifiers': []},
            '<': {'scancode': '33', 'modifiers': ['shift']},
            '.': {'scancode': '34', 'modifiers': []},
            '>': {'scancode': '34', 'modifiers': ['shift']},
            '/': {'scancode': '35', 'modifiers': []},
            '?': {'scancode': '35', 'modifiers': ['shift']},
        }
    
    def create_scoropis_layout_map(self) -> Dict[str, Any]:
        """Создает карту раскладки Скоропись"""
        layout = {}
        
        # Основная раскладка Скорописи
        scoropis_mapping = {
            # Верхний ряд
            'ц': '02', 'у': '03', 'а': '04', 'о': '05', 'в': '06',
            'п': '07', 'р': '08', 'л': '09', 'д': '0A', 'ж': '0B', 'э': '0C',
            
            # Основной ряд
            'й': '10', 'к': '11', 'е': '12', 'н': '13', 'г': '14',
            'ш': '15', 'з': '16', 'х': '17', 'ъ': '18', 'ф': '19', 'ы': '1A',
            
            # Нижний ряд
            'я': '1E', 'ч': '1F', 'с': '20', 'м': '21', 'и': '22',
            'т': '23', 'ь': '24', 'б': '25', 'ю': '26', 'ё': '27',
            
            # Латинские буквы (нижний регистр)
            'q': '02', 'w': '03', 'e': '04', 'r': '05', 't': '06',
            'y': '07', 'u': '08', 'i': '09', 'o': '0A', 'p': '0B',
            'a': '10', 's': '11', 'd': '12', 'f': '13', 'g': '14',
            'h': '15', 'j': '16', 'k': '17', 'l': '18', ';': '19', "'": '1A',
            'z': '1E', 'x': '1F', 'c': '20', 'v': '21', 'b': '22',
            'n': '23', 'm': '24', ',': '25', '.': '26', '/': '27',
        }
        
        for char_lower, scancode in scoropis_mapping.items():
            if char_lower.isalpha():
                char_upper = char_lower.upper()
                layout[char_lower] = {'scancode': scancode, 'modifiers': []}
                layout[char_upper] = {'scancode': scancode, 'modifiers': ['shift']}
            else:
                layout[char_lower] = {'scancode': scancode, 'modifiers': []}
        
        # Цифры и специальные символы верхнего ряда
        layout.update({
            '`': {'scancode': '29', 'modifiers': []},
            '~': {'scancode': '29', 'modifiers': ['shift']},
            '1': {'scancode': '02', 'modifiers': ['shift']},
            '!': {'scancode': '02', 'modifiers': ['shift', 'shift']},
            '2': {'scancode': '03', 'modifiers': ['shift']},
            '@': {'scancode': '03', 'modifiers': ['shift', 'shift']},
            '3': {'scancode': '04', 'modifiers': ['shift']},
            '#': {'scancode': '04', 'modifiers': ['shift', 'shift']},
            '4': {'scancode': '05', 'modifiers': ['shift']},
            '$': {'scancode': '05', 'modifiers': ['shift', 'shift']},
            '5': {'scancode': '06', 'modifiers': ['shift']},
            '%': {'scancode': '06', 'modifiers': ['shift', 'shift']},
            '6': {'scancode': '07', 'modifiers': ['shift']},
            '^': {'scancode': '07', 'modifiers': ['shift', 'shift']},
            '7': {'scancode': '08', 'modifiers': ['shift']},
            '&': {'scancode': '08', 'modifiers': ['shift', 'shift']},
            '8': {'scancode': '09', 'modifiers': ['shift']},
            '*': {'scancode': '09', 'modifiers': ['shift', 'shift']},
            '9': {'scancode': '0A', 'modifiers': ['shift']},
            '(': {'scancode': '0A', 'modifiers': ['shift', 'shift']},
            '0': {'scancode': '0B', 'modifiers': ['shift']},
            ')': {'scancode': '0B', 'modifiers': ['shift', 'shift']},
            '-': {'scancode': '0C', 'modifiers': []},
            '_': {'scancode': '0C', 'modifiers': ['shift']},
            '=': {'scancode': '0D', 'modifiers': []},
            '+': {'scancode': '0D', 'modifiers': ['shift']},
        })
        
        # Дополнительные специальные символы
        layout.update({
            ' ': {'scancode': '39', 'modifiers': []},
            '[': {'scancode': '1A', 'modifiers': ['shift']},
            ']': {'scancode': '1B', 'modifiers': ['shift']},
            '{': {'scancode': '1A', 'modifiers': ['shift', 'shift']},
            '}': {'scancode': '1B', 'modifiers': ['shift', 'shift']},
            '\\': {'scancode': '2B', 'modifiers': []},
            '|': {'scancode': '2B', 'modifiers': ['shift']},
            ':': {'scancode': '27', 'modifiers': ['shift']},
            '"': {'scancode': '28', 'modifiers': ['shift']},
            '<': {'scancode': '33', 'modifiers': ['shift']},
            '>': {'scancode': '34', 'modifiers': ['shift']},
            '?': {'scancode': '35', 'modifiers': ['shift']},
        })
        
        return layout
    
    def create_phonetic_vert_layout_map(self) -> Dict[str, Any]:
        """Создает карту фонетической раскладки яВерт"""
        layout = {}
        
        # Фонетическая раскладка (я → q, в → w и т.д.)
        phonetic_mapping = {
            'я': '10', 'в': '11', 'е': '12', 'р': '13', 'т': '14',
            'ы': '15', 'у': '16', 'и': '17', 'о': '18', 'п': '19',
            'а': '1E', 'с': '1F', 'д': '20', 'ф': '21', 'г': '22',
            'х': '23', 'й': '24', 'к': '25', 'л': '26',
            'з': '2C', 'ь': '2D', 'ц': '2E', 'ж': '2F', 'б': '30',
            'н': '31', 'м': '32', 'ш': '33', 'щ': '34', 'ч': '35',
            'ю': '36', 'э': '37', 'ъ': '38', 'ё': '39',
            
            # Латинские буквы
            'q': '10', 'w': '11', 'e': '12', 'r': '13', 't': '14',
            'y': '15', 'u': '16', 'i': '17', 'o': '18', 'p': '19',
            'a': '1E', 's': '1F', 'd': '20', 'f': '21', 'g': '22',
            'h': '23', 'j': '24', 'k': '25', 'l': '26',
            'z': '2C', 'x': '2D', 'c': '2E', 'v': '2F', 'b': '30',
            'n': '31', 'm': '32', ',': '33', '.': '34', '/': '35',
            ';': '36', "'": '37', '[': '38', ']': '39',
        }
        
        for char_lower, scancode in phonetic_mapping.items():
            if char_lower.isalpha():
                char_upper = char_lower.upper()
                layout[char_lower] = {'scancode': scancode, 'modifiers': []}
                layout[char_upper] = {'scancode': scancode, 'modifiers': ['shift']}
            else:
                layout[char_lower] = {'scancode': scancode, 'modifiers': []}
        
        # Цифры и специальные символы верхнего ряда
        layout.update({
            '`': {'scancode': '29', 'modifiers': []},
            '~': {'scancode': '29', 'modifiers': ['shift']},
            '1': {'scancode': '02', 'modifiers': []},
            '!': {'scancode': '02', 'modifiers': ['shift']},
            '2': {'scancode': '03', 'modifiers': []},
            '@': {'scancode': '03', 'modifiers': ['shift']},
            '3': {'scancode': '04', 'modifiers': []},
            '#': {'scancode': '04', 'modifiers': ['shift']},
            '4': {'scancode': '05', 'modifiers': []},
            '$': {'scancode': '05', 'modifiers': ['shift']},
            '5': {'scancode': '06', 'modifiers': []},
            '%': {'scancode': '06', 'modifiers': ['shift']},
            '6': {'scancode': '07', 'modifiers': []},
            '^': {'scancode': '07', 'modifiers': ['shift']},
            '7': {'scancode': '08', 'modifiers': []},
            '&': {'scancode': '08', 'modifiers': ['shift']},
            '8': {'scancode': '09', 'modifiers': []},
            '*': {'scancode': '09', 'modifiers': ['shift']},
            '9': {'scancode': '0A', 'modifiers': []},
            '(': {'scancode': '0A', 'modifiers': ['shift']},
            '0': {'scancode': '0B', 'modifiers': []},
            ')': {'scancode': '0B', 'modifiers': ['shift']},
            '-': {'scancode': '0C', 'modifiers': []},
            '_': {'scancode': '0C', 'modifiers': ['shift']},
            '=': {'scancode': '0D', 'modifiers': []},
            '+': {'scancode': '0D', 'modifiers': ['shift']},
            
            # Дополнительные специальные символы
            ' ': {'scancode': '39', 'modifiers': []},
            '{': {'scancode': '1A', 'modifiers': ['shift']},
            '}': {'scancode': '1B', 'modifiers': ['shift']},
            '\\': {'scancode': '2B', 'modifiers': []},
            '|': {'scancode': '2B', 'modifiers': ['shift']},
            ':': {'scancode': '28', 'modifiers': ['shift']},
            '"': {'scancode': '28', 'modifiers': ['shift', 'shift']},
            '<': {'scancode': '33', 'modifiers': ['shift']},
            '>': {'scancode': '34', 'modifiers': ['shift']},
            '?': {'scancode': '35', 'modifiers': ['shift']},
        })
        
        return layout
    
    def create_vyzov_layout_map(self) -> Dict[str, Any]:
        """Создает полную карту раскладки Вызов с русскими и английскими символами"""
        layout = {}
        
        # Основная раскладка Вызов (русские буквы)
        vyzov_ru_mapping = {
            'б': '02', 'х': '03', 'т': '04', 'ч': '05', 'щ': '06',
            'ш': '07', 'г': '08', 'а': '09', 'у': '0A', 'э': '0B',
            'в': '10', 'н': '11', 'д': '12', 'р': '13', 'й': '14',
            'ж': '15', 'с': '16', 'о': '17', 'и': '18', 'я': '19',
            'к': '1E', 'п': '1F', 'м': '20', 'л': '21', 'ц': '22',
            'ф': '23', 'з': '24', 'ъ': '25', 'ы': '26', 'ю': '27',
            'ь': '2C', 'е': '2D', 'ё': '2E'
        }
        
        # Английские буквы на тех же клавишах
        vyzov_en_mapping = {
            'q': '02', 'w': '03', 'e': '04', 'r': '05', 't': '06',
            'y': '07', 'u': '08', 'i': '09', 'o': '0A', 'p': '0B',
            'a': '10', 's': '11', 'd': '12', 'f': '13', 'g': '14',
            'h': '15', 'j': '16', 'k': '17', 'l': '18', ';': '19',
            'z': '1E', 'x': '1F', 'c': '20', 'v': '21', 'b': '22',
            'n': '23', 'm': '24', ',': '25', '.': '26', '/': '27',
            "'": '2C', '[': '2D', ']': '2E'
        }
        
        # Русские буквы (с модификатором LAlt)
        for char_lower, scancode in vyzov_ru_mapping.items():
            char_upper = char_lower.upper()
            layout[char_lower] = {'scancode': scancode, 'modifiers': ['lalt']}
            layout[char_upper] = {'scancode': scancode, 'modifiers': ['shift', 'lalt']}
        
        # Английские буквы (без модификаторов)
        for char_lower, scancode in vyzov_en_mapping.items():
            if char_lower.isalpha():
                char_upper = char_lower.upper()
                layout[char_lower] = {'scancode': scancode, 'modifiers': []}
                layout[char_upper] = {'scancode': scancode, 'modifiers': ['shift']}
            else:
                layout[char_lower] = {'scancode': scancode, 'modifiers': []}
        
        # Цифры и специальные символы верхнего ряда
        layout.update({
            '`': {'scancode': '29', 'modifiers': []},
            '~': {'scancode': '29', 'modifiers': ['shift']},
            '1': {'scancode': '02', 'modifiers': ['shift']},
            '!': {'scancode': '02', 'modifiers': ['shift', 'shift']},
            '2': {'scancode': '03', 'modifiers': ['shift']},
            '@': {'scancode': '03', 'modifiers': ['shift', 'shift']},
            '3': {'scancode': '04', 'modifiers': ['shift']},
            '#': {'scancode': '04', 'modifiers': ['shift', 'shift']},
            '4': {'scancode': '05', 'modifiers': ['shift']},
            '$': {'scancode': '05', 'modifiers': ['shift', 'shift']},
            '5': {'scancode': '06', 'modifiers': ['shift']},
            '%': {'scancode': '06', 'modifiers': ['shift', 'shift']},
            '6': {'scancode': '07', 'modifiers': ['shift']},
            '^': {'scancode': '07', 'modifiers': ['shift', 'shift']},
            '7': {'scancode': '08', 'modifiers': ['shift']},
            '&': {'scancode': '08', 'modifiers': ['shift', 'shift']},
            '8': {'scancode': '09', 'modifiers': ['shift']},
            '*': {'scancode': '09', 'modifiers': ['shift', 'shift']},
            '9': {'scancode': '0A', 'modifiers': ['shift']},
            '(': {'scancode': '0A', 'modifiers': ['shift', 'shift']},
            '0': {'scancode': '0B', 'modifiers': ['shift']},
            ')': {'scancode': '0B', 'modifiers': ['shift', 'shift']},
            '-': {'scancode': '0C', 'modifiers': []},
            '_': {'scancode': '0C', 'modifiers': ['shift']},
            '=': {'scancode': '0D', 'modifiers': []},
            '+': {'scancode': '0D', 'modifiers': ['shift']},
        })
        
        # Дополнительные специальные символы
        layout.update({
            ' ': {'scancode': '39', 'modifiers': []},
            '{': {'scancode': '1A', 'modifiers': ['shift']},
            '}': {'scancode': '1B', 'modifiers': ['shift']},
            '\\': {'scancode': '2B', 'modifiers': []},
            '|': {'scancode': '2B', 'modifiers': ['shift']},
            ':': {'scancode': '28', 'modifiers': ['shift']},
            '"': {'scancode': '28', 'modifiers': ['shift', 'shift']},
            '<': {'scancode': '33', 'modifiers': ['shift']},
            '>': {'scancode': '34', 'modifiers': ['shift']},
            '?': {'scancode': '35', 'modifiers': ['shift']},
        })
        
        return layout
    
    def create_qwerty_layout_map(self) -> Dict[str, Any]:
        """Создает карту раскладки QWERTY"""
        layout = {}
        
        base_layout = {
            'q': '10', 'w': '11', 'e': '12', 'r': '13', 't': '14',
            'y': '15', 'u': '16', 'i': '17', 'o': '18', 'p': '19',
            'a': '1E', 's': '1F', 'd': '20', 'f': '21', 'g': '22',
            'h': '23', 'j': '24', 'k': '25', 'l': '26',
            'z': '2C', 'x': '2D', 'c': '2E', 'v': '2F', 'b': '30',
            'n': '31', 'm': '32'
        }
        
        for char_lower, scancode in base_layout.items():
            char_upper = char_lower.upper()
            layout[char_lower] = {'scancode': scancode, 'modifiers': []}
            layout[char_upper] = {'scancode': scancode, 'modifiers': ['shift']}
        
        # Цифры и специальные символы верхнего ряда
        layout.update({
            '`': {'scancode': '29', 'modifiers': []},
            '~': {'scancode': '29', 'modifiers': ['shift']},
            '1': {'scancode': '02', 'modifiers': []},
            '!': {'scancode': '02', 'modifiers': ['shift']},
            '2': {'scancode': '03', 'modifiers': []},
            '@': {'scancode': '03', 'modifiers': ['shift']},
            '3': {'scancode': '04', 'modifiers': []},
            '#': {'scancode': '04', 'modifiers': ['shift']},
            '4': {'scancode': '05', 'modifiers': []},
            '$': {'scancode': '05', 'modifiers': ['shift']},
            '5': {'scancode': '06', 'modifiers': []},
            '%': {'scancode': '06', 'modifiers': ['shift']},
            '6': {'scancode': '07', 'modifiers': []},
            '^': {'scancode': '07', 'modifiers': ['shift']},
            '7': {'scancode': '08', 'modifiers': []},
            '&': {'scancode': '08', 'modifiers': ['shift']},
            '8': {'scancode': '09', 'modifiers': []},
            '*': {'scancode': '09', 'modifiers': ['shift']},
            '9': {'scancode': '0A', 'modifiers': []},
            '(': {'scancode': '0A', 'modifiers': ['shift']},
            '0': {'scancode': '0B', 'modifiers': []},
            ')': {'scancode': '0B', 'modifiers': ['shift']},
            '-': {'scancode': '0C', 'modifiers': []},
            '_': {'scancode': '0C', 'modifiers': ['shift']},
            '=': {'scancode': '0D', 'modifiers': []},
            '+': {'scancode': '0D', 'modifiers': ['shift']},
            
            # Дополнительные специальные символы
            ' ': {'scancode': '39', 'modifiers': []},
            '[': {'scancode': '1A', 'modifiers': []},
            ']': {'scancode': '1B', 'modifiers': []},
            '{': {'scancode': '1A', 'modifiers': ['shift']},
            '}': {'scancode': '1B', 'modifiers': ['shift']},
            '\\': {'scancode': '2B', 'modifiers': []},
            '|': {'scancode': '2B', 'modifiers': ['shift']},
            ';': {'scancode': '27', 'modifiers': []},
            ':': {'scancode': '27', 'modifiers': ['shift']},
            "'": {'scancode': '28', 'modifiers': []},
            '"': {'scancode': '28', 'modifiers': ['shift']},
            ',': {'scancode': '33', 'modifiers': []},
            '<': {'scancode': '33', 'modifiers': ['shift']},
            '.': {'scancode': '34', 'modifiers': []},
            '>': {'scancode': '34', 'modifiers': ['shift']},
            '/': {'scancode': '35', 'modifiers': []},
            '?': {'scancode': '35', 'modifiers': ['shift']},
        })
        
        return layout
    
    def create_dvorak_layout_map(self) -> Dict[str, Any]:
        """Создает карту раскладки Dvorak"""
        layout = {}
        
        dvorak_mapping = {
            "'": '10', ',': '11', '.': '12', 'p': '13', 'y': '14',
            'f': '15', 'g': '16', 'c': '17', 'r': '18', 'l': '19',
            'a': '1E', 'o': '1F', 'e': '20', 'u': '21', 'i': '22',
            'd': '23', 'h': '24', 't': '25', 'n': '26', 's': '27',
            ';': '2C', 'q': '2D', 'j': '2E', 'k': '2F', 'x': '30',
            'b': '31', 'm': '32', 'w': '33', 'v': '34', 'z': '35'
        }
        
        for char, scancode in dvorak_mapping.items():
            if char.isalpha():
                layout[char.lower()] = {'scancode': scancode, 'modifiers': []}
                layout[char.upper()] = {'scancode': scancode, 'modifiers': ['shift']}
            else:
                layout[char] = {'scancode': scancode, 'modifiers': []}
        
        # Цифры и специальные символы верхнего ряда
        layout.update({
            '`': {'scancode': '29', 'modifiers': []},
            '~': {'scancode': '29', 'modifiers': ['shift']},
            '1': {'scancode': '02', 'modifiers': []},
            '!': {'scancode': '02', 'modifiers': ['shift']},
            '2': {'scancode': '03', 'modifiers': []},
            '@': {'scancode': '03', 'modifiers': ['shift']},
            '3': {'scancode': '04', 'modifiers': []},
            '#': {'scancode': '04', 'modifiers': ['shift']},
            '4': {'scancode': '05', 'modifiers': []},
            '$': {'scancode': '05', 'modifiers': ['shift']},
            '5': {'scancode': '06', 'modifiers': []},
            '%': {'scancode': '06', 'modifiers': ['shift']},
            '6': {'scancode': '07', 'modifiers': []},
            '^': {'scancode': '07', 'modifiers': ['shift']},
            '7': {'scancode': '08', 'modifiers': []},
            '&': {'scancode': '08', 'modifiers': ['shift']},
            '8': {'scancode': '09', 'modifiers': []},
            '*': {'scancode': '09', 'modifiers': ['shift']},
            '9': {'scancode': '0A', 'modifiers': []},
            '(': {'scancode': '0A', 'modifiers': ['shift']},
            '0': {'scancode': '0B', 'modifiers': []},
            ')': {'scancode': '0B', 'modifiers': ['shift']},
            '[': {'scancode': '1A', 'modifiers': []},
            ']': {'scancode': '1B', 'modifiers': []},
            '{': {'scancode': '1A', 'modifiers': ['shift']},
            '}': {'scancode': '1B', 'modifiers': ['shift']},
            
            # Дополнительные специальные символы
            ' ': {'scancode': '39', 'modifiers': []},
            '\\': {'scancode': '2B', 'modifiers': []},
            '|': {'scancode': '2B', 'modifiers': ['shift']},
            ':': {'scancode': '27', 'modifiers': ['shift']},
            '"': {'scancode': '28', 'modifiers': ['shift']},
            '<': {'scancode': '33', 'modifiers': ['shift']},
            '>': {'scancode': '34', 'modifiers': ['shift']},
            '?': {'scancode': '35', 'modifiers': ['shift']},
            '-': {'scancode': '0C', 'modifiers': []},
            '_': {'scancode': '0C', 'modifiers': ['shift']},
            '=': {'scancode': '0D', 'modifiers': []},
            '+': {'scancode': '0D', 'modifiers': ['shift']},
            '/': {'scancode': '35', 'modifiers': []},
        })
        
        return layout
    
    def create_colemak_layout_map(self) -> Dict[str, Any]:
        """Создает карту раскладки Colemak"""
        layout = {}
        
        colemak_mapping = {
            'q': '10', 'w': '11', 'f': '12', 'p': '13', 'g': '14',
            'j': '15', 'l': '16', 'u': '17', 'y': '18', ';': '19',
            'a': '1E', 'r': '1F', 's': '20', 't': '21', 'd': '22',
            'h': '23', 'n': '24', 'e': '25', 'i': '26', 'o': '27',
            'z': '2C', 'x': '2D', 'c': '2E', 'v': '2F', 'b': '30',
            'k': '31', 'm': '32'
        }
        
        for char_lower, scancode in colemak_mapping.items():
            if char_lower.isalpha():
                char_upper = char_lower.upper()
                layout[char_lower] = {'scancode': scancode, 'modifiers': []}
                layout[char_upper] = {'scancode': scancode, 'modifiers': ['shift']}
            else:
                layout[char_lower] = {'scancode': scancode, 'modifiers': []}
        
        # Цифры и специальные символы верхнего ряда
        layout.update({
            '`': {'scancode': '29', 'modifiers': []},
            '~': {'scancode': '29', 'modifiers': ['shift']},
            '1': {'scancode': '02', 'modifiers': []},
            '!': {'scancode': '02', 'modifiers': ['shift']},
            '2': {'scancode': '03', 'modifiers': []},
            '@': {'scancode': '03', 'modifiers': ['shift']},
            '3': {'scancode': '04', 'modifiers': []},
            '#': {'scancode': '04', 'modifiers': ['shift']},
            '4': {'scancode': '05', 'modifiers': []},
            '$': {'scancode': '05', 'modifiers': ['shift']},
            '5': {'scancode': '06', 'modifiers': []},
            '%': {'scancode': '06', 'modifiers': ['shift']},
            '6': {'scancode': '07', 'modifiers': []},
            '^': {'scancode': '07', 'modifiers': ['shift']},
            '7': {'scancode': '08', 'modifiers': []},
            '&': {'scancode': '08', 'modifiers': ['shift']},
            '8': {'scancode': '09', 'modifiers': []},
            '*': {'scancode': '09', 'modifiers': ['shift']},
            '9': {'scancode': '0A', 'modifiers': []},
            '(': {'scancode': '0A', 'modifiers': ['shift']},
            '0': {'scancode': '0B', 'modifiers': []},
            ')': {'scancode': '0B', 'modifiers': ['shift']},
            '-': {'scancode': '0C', 'modifiers': []},
            '_': {'scancode': '0C', 'modifiers': ['shift']},
            '=': {'scancode': '0D', 'modifiers': []},
            '+': {'scancode': '0D', 'modifiers': ['shift']},
            
            # Дополнительные специальные символы
            ' ': {'scancode': '39', 'modifiers': []},
            '[': {'scancode': '1A', 'modifiers': []},
            ']': {'scancode': '1B', 'modifiers': []},
            '{': {'scancode': '1A', 'modifiers': ['shift']},
            '}': {'scancode': '1B', 'modifiers': ['shift']},
            '\\': {'scancode': '2B', 'modifiers': []},
            '|': {'scancode': '2B', 'modifiers': ['shift']},
            ':': {'scancode': '27', 'modifiers': ['shift']},
            '"': {'scancode': '28', 'modifiers': ['shift']},
            ',': {'scancode': '33', 'modifiers': []},
            '<': {'scancode': '33', 'modifiers': ['shift']},
            '.': {'scancode': '34', 'modifiers': []},
            '>': {'scancode': '34', 'modifiers': ['shift']},
            '/': {'scancode': '35', 'modifiers': []},
            '?': {'scancode': '35', 'modifiers': ['shift']},
        })
        
        return layout
    
    def create_workman_layout_map(self) -> Dict[str, Any]:
        """Создает карту раскладки Workman"""
        layout = {}
        
        workman_mapping = {
            'q': '10', 'd': '11', 'r': '12', 'w': '13', 'b': '14',
            'j': '15', 'f': '16', 'u': '17', 'p': '18', ';': '19',
            'a': '1E', 's': '1F', 'h': '20', 't': '21', 'g': '22',
            'y': '23', 'n': '24', 'e': '25', 'o': '26', 'i': '27',
            'z': '2C', 'x': '2D', 'm': '2E', 'c': '2F', 'v': '30',
            'k': '31', 'l': '32'
        }
        
        for char_lower, scancode in workman_mapping.items():
            if char_lower.isalpha():
                char_upper = char_lower.upper()
                layout[char_lower] = {'scancode': scancode, 'modifiers': []}
                layout[char_upper] = {'scancode': scancode, 'modifiers': ['shift']}
            else:
                layout[char_lower] = {'scancode': scancode, 'modifiers': []}
        
        # Цифры и специальные символы верхнего ряда
        layout.update({
            '`': {'scancode': '29', 'modifiers': []},
            '~': {'scancode': '29', 'modifiers': ['shift']},
            '1': {'scancode': '02', 'modifiers': []},
            '!': {'scancode': '02', 'modifiers': ['shift']},
            '2': {'scancode': '03', 'modifiers': []},
            '@': {'scancode': '03', 'modifiers': ['shift']},
            '3': {'scancode': '04', 'modifiers': []},
            '#': {'scancode': '04', 'modifiers': ['shift']},
            '4': {'scancode': '05', 'modifiers': []},
            '$': {'scancode': '05', 'modifiers': ['shift']},
            '5': {'scancode': '06', 'modifiers': []},
            '%': {'scancode': '06', 'modifiers': ['shift']},
            '6': {'scancode': '07', 'modifiers': []},
            '^': {'scancode': '07', 'modifiers': ['shift']},
            '7': {'scancode': '08', 'modifiers': []},
            '&': {'scancode': '08', 'modifiers': ['shift']},
            '8': {'scancode': '09', 'modifiers': []},
            '*': {'scancode': '09', 'modifiers': ['shift']},
            '9': {'scancode': '0A', 'modifiers': []},
            '(': {'scancode': '0A', 'modifiers': ['shift']},
            '0': {'scancode': '0B', 'modifiers': []},
            ')': {'scancode': '0B', 'modifiers': ['shift']},
            '-': {'scancode': '0C', 'modifiers': []},
            '_': {'scancode': '0C', 'modifiers': ['shift']},
            '=': {'scancode': '0D', 'modifiers': []},
            '+': {'scancode': '0D', 'modifiers': ['shift']},
            
            # Дополнительные специальные символы
            ' ': {'scancode': '39', 'modifiers': []},
            '[': {'scancode': '1A', 'modifiers': []},
            ']': {'scancode': '1B', 'modifiers': []},
            '{': {'scancode': '1A', 'modifiers': ['shift']},
            '}': {'scancode': '1B', 'modifiers': ['shift']},
            '\\': {'scancode': '2B', 'modifiers': []},
            '|': {'scancode': '2B', 'modifiers': ['shift']},
            ':': {'scancode': '27', 'modifiers': ['shift']},
            '"': {'scancode': '28', 'modifiers': ['shift']},
            ',': {'scancode': '33', 'modifiers': []},
            '<': {'scancode': '33', 'modifiers': ['shift']},
            '.': {'scancode': '34', 'modifiers': []},
            '>': {'scancode': '34', 'modifiers': ['shift']},
            '/': {'scancode': '35', 'modifiers': []},
            '?': {'scancode': '35', 'modifiers': ['shift']},
        })
        
        return layout