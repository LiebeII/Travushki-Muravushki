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
        # Карты всех раскладок (ТОЛЬКО БУКВЫ И ЦИФРЫ)
        self.layout_maps = {
            'ЙЦУКЕН': self.create_icuken_layout_map(),
            'Скоропись': self.create_scoropis_layout_map(),
            'Фонетическая (яВерт)': self.create_phonetic_vert_layout_map(),
            'Диктор': self.create_diktor_layout_map(),
            'QWERTY': self.create_qwerty_layout_map(),
            'Dvorak': self.create_dvorak_layout_map(),
            'Colemak': self.create_colemak_layout_map(),
            'Workman': self.create_workman_layout_map()
        }
        
        # Соответствие сканкодов пальцам (БЕЗ БОЛЬШИХ ПАЛЬЦЕВ)
        self.key_finger = {
            'left_pinky': ['02', '10', '1E', '2C', '38'],
            'left_ring': ['03', '11', '1F', '2D'],
            'left_middle': ['04', '12', '20', '2E'],
            'left_index': ['05', '13', '21', '2F', '06', '14', '22', '30'],
            
            'right_index': ['07', '15', '23', '31', '08', '16', '24', '32'],
            'right_middle': ['09', '17', '25', '33'],
            'right_ring': ['0A', '18', '26', '34'],
            'right_pinky': ['0B', '19', '27', '35', '0C', '1A', '28', '36', '29', '0D', '1B', '37'],
        }
        
        # Соответствие сканкодов рукам (БЕЗ БОЛЬШИХ ПАЛЬЦЕВ)
        self.key_hand = {
            'left': ['02', '03', '04', '05', '06', '10', '11', '12', '13', '14', 
                    '1E', '1F', '20', '21', '22', '2C', '2D', '2E', '2F', '30', '38'],
            'right': ['07', '08', '09', '0A', '0B', '0C', '0D', '15', '16', '17', '18',
                     '19', '1A', '1B', '23', '24', '25', '26', '27', '28', '29',
                     '31', '32', '33', '34', '35', '36', '37']
        }
        
        # Порядок пальцев для определения направления
        self.finger_order = [
            'left_pinky', 'left_ring', 'left_middle', 'left_index',
            'right_index', 'right_middle', 'right_ring', 'right_pinky'
        ]
    
    def get_finger_for_scancode(self, scancode: str) -> str:
        """Получает палец для сканкода"""
        for finger, scancodes in self.key_finger.items():
            if scancode in scancodes:
                return finger
        return None
    
    def get_hand_for_scancode(self, scancode: str) -> str:
        """Получает руку для сканкода"""
        for hand, scancodes in self.key_hand.items():
            if scancode in scancodes:
                return hand
        return None
    
    def calculate_finger_direction(self, finger1: str, finger2: str) -> int:
        """
        Определяет направление движения пальцев:
        1 = от мизинца к указательному (удобно, вовнутрь)
        0 = то же место (тот же палец)
        -1 = от указательного к мизинцу (менее удобно, наружу)
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
        
        # Для левой руки: от мизинца (0) к указательному (3) - положительное направление (1)
        # Для правой руки: от мизинца (7) к указательному (4) - отрицательное направление (-1)
        if is_left_hand:
            return 1 if direction > 0 else -1
        else:  # правая рука
            return -1 if direction > 0 else 1  # Обратное направление для правой руки
    
    def calculate_dynamic_penalties(self, words_set: Set[str], layout_map: Dict[str, Any]) -> Tuple[Dict[str, int], Dict[str, int], Dict[str, int], Dict[str, float]]:
        """
        Рассчитывает динамические штрафы по правилам:
        - Удобные: нет смены рук и пальцы идут вовнутрь
        - Частично удобные: смена направления пальцев, но той же руки
        - Неудобные: разные руки
        
        Возвращает словари комбинаций и оценок
        """
        comfort_combos = defaultdict(int)
        partial_combos = defaultdict(int)
        uncomfortable_combos = defaultdict(int)
        dynamic_scores = {}
        
        for word in words_set:
            if len(word) < 2:  # Пропускаем односимвольные слова
                continue
            
            # Анализируем все последовательные пары символов в слове
            for i in range(len(word) - 1):
                combo = word[i:i+2]
                
                # Пропускаем комбинации с пробелами или неподдерживаемыми символами
                if ' ' in combo:
                    continue
                
                valid = True
                for char in combo:
                    if scancode_from_char(char, layout_map) is None:  # Используем функцию из этого же файла
                        valid = False
                        break
                
                if not valid:
                    continue
                
                # Определяем удобство комбинации
                comfort_score, category = self.calculate_combo_comfort_dynamic(combo, layout_map)
                dynamic_scores[combo] = comfort_score
                
                # Добавляем в соответствующий словарь
                if category == 'comfortable':
                    comfort_combos[combo] += 1
                elif category == 'partially_comfortable':
                    partial_combos[combo] += 1
                elif category == 'uncomfortable':
                    uncomfortable_combos[combo] += 1
        
        return comfort_combos, partial_combos, uncomfortable_combos, dynamic_scores
    
    def calculate_combo_comfort_dynamic(self, combo: str, layout_map: Dict[str, Any]) -> Tuple[float, str]:
        """
        Улучшенный расчет удобства комбинации:
        
        Правила:
        1. Удобные - нет смены рук и пальцы идут от мизинца к указательному (во внутрь)
        2. Частично удобные - смена направления пальцев, но той же руки
        3. Неудобные - разные руки
        
        Для двухсимвольных комбинаций
        """
        if len(combo) != 2:
            return 0.0, 'uncomfortable'
        
        char1, char2 = combo[0], combo[1]
        
        # Получаем сканкоды
        scancode1 = scancode_from_char(char1, layout_map)
        scancode2 = scancode_from_char(char2, layout_map)
        
        if scancode1 is None or scancode2 is None:
            return 0.0, 'uncomfortable'
        
        # Определяем пальцы
        finger1 = self.get_finger_for_scancode(scancode1)
        finger2 = self.get_finger_for_scancode(scancode2)
        
        if finger1 is None or finger2 is None:
            return 0.0, 'uncomfortable'
        
        # Проверяем смену рук (неудобно)
        hand1 = self.get_hand_for_scancode(scancode1)
        hand2 = self.get_hand_for_scancode(scancode2)
        
        if hand1 != hand2:
            return 0.0, 'uncomfortable'
        
        # Проверяем тот же палец (частично удобно)
        if finger1 == finger2:
            return 0.5, 'partially_comfortable'
        
        # Определяем направление
        direction = self.calculate_finger_direction(finger1, finger2)
        
        if direction == 1:
            # От мизинца к указательному (удобно)
            return 1.0, 'comfortable'
        elif direction == -1:
            # От указательного к мизинцу (частично удобно)
            return 0.3, 'partially_comfortable'
        else:
            # Неопределенное направление
            return 0.0, 'uncomfortable'
    
    def calculate_hand_balance(self, text: str, layout_map: Dict[str, Any]) -> Dict[str, Any]:
        """Рассчитывает баланс между руками (без учета больших пальцев)"""
        hand_counts = {'left': 0, 'right': 0}
        
        # Разбиваем текст на слова (только буквы)
        words = re.findall(r'[а-яА-ЯёЁa-zA-Z]+', text)
        
        for word in words:
            if len(word) < 2:  # Пропускаем односимвольные слова
                continue
            
            for char in word:
                if char.strip() and char != ' ':
                    scancode = scancode_from_char(char, layout_map)
                    if scancode and scancode != '39':  # Игнорируем пробел
                        hand = self.get_hand_for_scancode(scancode)
                        if hand in hand_counts:
                            hand_counts[hand] += 1
        
        total = hand_counts['left'] + hand_counts['right']
        
        if total > 0:
            left_percent = (hand_counts['left'] / total) * 100
            right_percent = (hand_counts['right'] / total) * 100
            
            # Рассчитываем балл баланса (чем ближе к 50%, тем лучше)
            balance_score = 100 - abs(left_percent - 50) * 2
            
            # Определяем, хороший ли баланс (45-55%)
            is_good = 45 <= left_percent <= 55
            
            return {
                'left_count': hand_counts['left'],
                'right_count': hand_counts['right'],
                'left_percent': left_percent,
                'right_percent': right_percent,
                'balance_score': balance_score,
                'is_good': is_good
            }
        
        return {
            'left_count': 0,
            'right_count': 0,
            'left_percent': 50,
            'right_percent': 50,
            'balance_score': 100,
            'is_good': True
        }
    
    def analyze_two_char_combinations(self, combos_dict: Dict[str, int], layout_map: Dict[str, Any]) -> Dict[str, int]:
        """
        Анализ двухсимвольных комбинаций:
        - Одноручные комбинации
        """
        results = {
            'one_hand_total': 0,
        }
        
        for combo, count in combos_dict.items():
            if len(combo) != 2:
                continue
            
            scancode1 = scancode_from_char(combo[0], layout_map)
            scancode2 = scancode_from_char(combo[1], layout_map)
            
            if scancode1 is None or scancode2 is None:
                continue
            
            hand1 = self.get_hand_for_scancode(scancode1)
            hand2 = self.get_hand_for_scancode(scancode2)
            
            if hand1 is None or hand2 is None:
                continue
            
            # Проверяем одноручность
            if hand1 == hand2:
                results['one_hand_total'] += count
        
        return results
    
    # МЕТОДЫ СОЗДАНИЯ РАСКЛАДОК (ТОЛЬКО БУКВЫ И ЦИФРЫ)
    
    def create_icuken_layout_map(self) -> Dict[str, Any]:
        """Создает карту раскладки ЙЦУКЕН (только буквы и цифры)"""
        layout = {}
        
        # Русские буквы нижний регистр
        ru_lower = {
            'й': '10', 'ц': '11', 'у': '12', 'к': '13', 'е': '14',
            'н': '15', 'г': '16', 'ш': '17', 'щ': '18', 'з': '19',
            'х': '1A', 'ъ': '1B', 'ф': '1E', 'ы': '1F', 'в': '20',
            'а': '21', 'п': '22', 'р': '23', 'о': '24', 'л': '25',
            'д': '26', 'ж': '27', 'э': '28', 'я': '2C', 'ч': '2D',
            'с': '2E', 'м': '2F', 'и': '30', 'т': '31', 'ь': '32',
            'б': '33', 'ю': '34', 'ё': '29'
        }
        
        # Добавляем русские буквы нижнего и верхнего регистра
        for char_lower, scancode in ru_lower.items():
            layout[char_lower] = {'scancode': scancode, 'modifiers': []}
            layout[char_lower.upper()] = {'scancode': scancode, 'modifiers': ['shift']}
        
        # Цифры
        digits = {
            '1': '02', '2': '03', '3': '04', '4': '05', '5': '06',
            '6': '07', '7': '08', '8': '09', '9': '0A', '0': '0B'
        }
        
        for digit, scancode in digits.items():
            layout[digit] = {'scancode': scancode, 'modifiers': []}
        
        # Пробел
        layout[' '] = {'scancode': '39', 'modifiers': []}
        
        return layout
    
    def create_scoropis_layout_map(self) -> Dict[str, Any]:
        """Создает карту раскладки Скоропись (только буквы и цифры)"""
        layout = {}
        
        # Русские буквы Скоропись
        scoropis_lower = {
            'ц': '10', 'у': '11', 'а': '12', 'о': '13', 'в': '14',
            'п': '15', 'р': '16', 'л': '17', 'д': '18', 'ж': '19', 'э': '1A',
            'й': '1E', 'к': '1F', 'е': '20', 'н': '21', 'г': '22',
            'ш': '23', 'з': '24', 'х': '25', 'ъ': '26', 'ф': '27', 'ы': '28',
            'я': '2C', 'ч': '2D', 'с': '2E', 'м': '2F', 'и': '30',
            'т': '31', 'ь': '32', 'б': '33', 'ю': '34', 'ё': '35'
        }
        
        # Добавляем русские буквы
        for char_lower, scancode in scoropis_lower.items():
            layout[char_lower] = {'scancode': scancode, 'modifiers': []}
            layout[char_lower.upper()] = {'scancode': scancode, 'modifiers': ['shift']}
        
        # Цифры
        digits = {
            '1': '02', '2': '03', '3': '04', '4': '05', '5': '06',
            '6': '07', '7': '08', '8': '09', '9': '0A', '0': '0B'
        }
        
        for digit, scancode in digits.items():
            layout[digit] = {'scancode': scancode, 'modifiers': []}
        
        # Пробел
        layout[' '] = {'scancode': '39', 'modifiers': []}
        
        return layout
    
    def create_phonetic_vert_layout_map(self) -> Dict[str, Any]:
        """Создает карту фонетической раскладки яВерт (только буквы и цифры)"""
        layout = {}
        
        # Русские буквы Фонетическая яВерт
        phonetic_lower = {
            'я': '10', 'в': '11', 'е': '12', 'р': '13', 'т': '14',
            'ы': '15', 'у': '16', 'и': '17', 'о': '18', 'п': '19',
            'а': '1E', 'с': '1F', 'д': '20', 'ф': '21', 'г': '22',
            'х': '23', 'й': '24', 'к': '25', 'л': '26',
            'з': '2C', 'ь': '2D', 'ц': '2E', 'ж': '2F', 'б': '30',
            'н': '31', 'м': '32', 'ш': '33', 'щ': '34', 'ч': '35'
        }
        
        # Добавляем русские буквы
        for char_lower, scancode in phonetic_lower.items():
            layout[char_lower] = {'scancode': scancode, 'modifiers': []}
            layout[char_lower.upper()] = {'scancode': scancode, 'modifiers': ['shift']}
        
        # Добавляем недостающие буквы
        layout['э'] = {'scancode': '28', 'modifiers': []}
        layout['Э'] = {'scancode': '28', 'modifiers': ['shift']}
        layout['ъ'] = {'scancode': '29', 'modifiers': []}
        layout['Ъ'] = {'scancode': '29', 'modifiers': ['shift']}
        layout['ё'] = {'scancode': '35', 'modifiers': []}
        layout['Ё'] = {'scancode': '35', 'modifiers': ['shift']}
        
        # Цифры
        digits = {
            '1': '02', '2': '03', '3': '04', '4': '05', '5': '06',
            '6': '07', '7': '08', '8': '09', '9': '0A', '0': '0B'
        }
        
        for digit, scancode in digits.items():
            layout[digit] = {'scancode': scancode, 'modifiers': []}
        
        # Пробел
        layout[' '] = {'scancode': '39', 'modifiers': []}
        
        return layout
    
    def create_diktor_layout_map(self) -> Dict[str, Any]:
        """Создает карту раскладки Диктор"""
        layout = {}
        
        # Русские буквы Диктор
        diktor_lower = {
            'н': '10', 'т': '11', 'с': '12', 'р': '13', 'в': '14',
            'м': '15', 'д': '16', 'п': '17', 'л': '18', 'г': '19',
            'б': '1A', 'ь': '1B', 'о': '1E', 'а': '1F', 'е': '20',
            'и': '21', 'у': '22', 'к': '23', 'я': '24', 'ы': '25',
            'з': '26', 'ж': '27', 'э': '28', 'й': '2C', 'ч': '2D',
            'х': '2E', 'ц': '2F', 'ф': '30', 'ш': '31', 'щ': '32',
            'ю': '33', 'ъ': '34', 'ё': '35'
        }
        
        # Добавляем русские буквы
        for char_lower, scancode in diktor_lower.items():
            layout[char_lower] = {'scancode': scancode, 'modifiers': []}
            layout[char_lower.upper()] = {'scancode': scancode, 'modifiers': ['shift']}
        
        # Цифры
        digits = {
            '1': '02', '2': '03', '3': '04', '4': '05', '5': '06',
            '6': '07', '7': '08', '8': '09', '9': '0A', '0': '0B'
        }
        
        for digit, scancode in digits.items():
            layout[digit] = {'scancode': scancode, 'modifiers': []}
        
        # Пробел
        layout[' '] = {'scancode': '39', 'modifiers': []}
        
        return layout
    
    def create_qwerty_layout_map(self) -> Dict[str, Any]:
        """Создает карту раскладки QWERTY (только буквы и цифры)"""
        layout = {}
        
        # Английские буквы
        en_lower = {
            'q': '10', 'w': '11', 'e': '12', 'r': '13', 't': '14',
            'y': '15', 'u': '16', 'i': '17', 'o': '18', 'p': '19',
            'a': '1E', 's': '1F', 'd': '20', 'f': '21', 'g': '22',
            'h': '23', 'j': '24', 'k': '25', 'l': '26',
            'z': '2C', 'x': '2D', 'c': '2E', 'v': '2F', 'b': '30',
            'n': '31', 'm': '32'
        }
        
        # Добавляем английские буквы
        for char_lower, scancode in en_lower.items():
            layout[char_lower] = {'scancode': scancode, 'modifiers': []}
            layout[char_lower.upper()] = {'scancode': scancode, 'modifiers': ['shift']}
        
        # Цифры
        digits = {
            '1': '02', '2': '03', '3': '04', '4': '05', '5': '06',
            '6': '07', '7': '08', '8': '09', '9': '0A', '0': '0B'
        }
        
        for digit, scancode in digits.items():
            layout[digit] = {'scancode': scancode, 'modifiers': []}
        
        # Пробел
        layout[' '] = {'scancode': '39', 'modifiers': []}
        
        return layout
    
    def create_dvorak_layout_map(self) -> Dict[str, Any]:
        """Создает карту раскладки Dvorak (только буквы и цифры)"""
        layout = {}
        
        # Dvorak буквы (только буквы)
        dvorak_lower_letters = {
            'p': '10', 'y': '11', 'f': '12', 'g': '13', 'c': '14',
            'r': '15', 'l': '16', 'a': '1E', 'o': '1F', 'e': '20',
            'u': '21', 'i': '22', 'd': '23', 'h': '24', 't': '25',
            'n': '26', 's': '27', 'q': '2C', 'j': '2D', 'k': '2E',
            'x': '2F', 'b': '30', 'm': '31', 'w': '32', 'v': '33',
            'z': '34'
        }
        
        # Добавляем Dvorak буквы
        for char_lower, scancode in dvorak_lower_letters.items():
            layout[char_lower] = {'scancode': scancode, 'modifiers': []}
            layout[char_lower.upper()] = {'scancode': scancode, 'modifiers': ['shift']}
        
        # Цифры
        digits = {
            '1': '02', '2': '03', '3': '04', '4': '05', '5': '06',
            '6': '07', '7': '08', '8': '09', '9': '0A', '0': '0B'
        }
        
        for digit, scancode in digits.items():
            layout[digit] = {'scancode': scancode, 'modifiers': []}
        
        # Пробел
        layout[' '] = {'scancode': '39', 'modifiers': []}
        
        return layout
    
    def create_colemak_layout_map(self) -> Dict[str, Any]:
        """Создает карту раскладки Colemak (только буквы и цифры)"""
        layout = {}
        
        # Colemak буквы
        colemak_lower = {
            'q': '10', 'w': '11', 'f': '12', 'p': '13', 'g': '14',
            'j': '15', 'l': '16', 'u': '17', 'y': '18', 'a': '1E',
            'r': '1F', 's': '20', 't': '21', 'd': '22', 'h': '23',
            'n': '24', 'e': '25', 'i': '26', 'o': '27', 'z': '2C',
            'x': '2D', 'c': '2E', 'v': '2F', 'b': '30', 'k': '31',
            'm': '32'
        }
        
        # Добавляем Colemak буквы
        for char_lower, scancode in colemak_lower.items():
            if char_lower.isalpha():
                layout[char_lower] = {'scancode': scancode, 'modifiers': []}
                layout[char_lower.upper()] = {'scancode': scancode, 'modifiers': ['shift']}
        
        # Цифры
        digits = {
            '1': '02', '2': '03', '3': '04', '4': '05', '5': '06',
            '6': '07', '7': '08', '8': '09', '9': '0A', '0': '0B'
        }
        
        for digit, scancode in digits.items():
            layout[digit] = {'scancode': scancode, 'modifiers': []}
        
        # Пробел
        layout[' '] = {'scancode': '39', 'modifiers': []}
        
        return layout
    
    def create_workman_layout_map(self) -> Dict[str, Any]:
        """Создает карту раскладки Workman (только буквы и цифры)"""
        layout = {}
        
        # Workman буквы
        workman_lower = {
            'q': '10', 'd': '11', 'r': '12', 'w': '13', 'b': '14',
            'j': '15', 'f': '16', 'u': '17', 'p': '18', 'a': '1E',
            's': '1F', 'h': '20', 't': '21', 'g': '22', 'y': '23',
            'n': '24', 'e': '25', 'o': '26', 'i': '27', 'z': '2C',
            'x': '2D', 'm': '2E', 'c': '2F', 'v': '30', 'k': '31',
            'l': '32'
        }
        
        # Добавляем Workman буквы
        for char_lower, scancode in workman_lower.items():
            if char_lower.isalpha():
                layout[char_lower] = {'scancode': scancode, 'modifiers': []}
                layout[char_lower.upper()] = {'scancode': scancode, 'modifiers': ['shift']}
        
        # Цифры
        digits = {
            '1': '02', '2': '03', '3': '04', '4': '05', '5': '06',
            '6': '07', '7': '08', '8': '09', '9': '0A', '0': '0B'
        }
        
        for digit, scancode in digits.items():
            layout[digit] = {'scancode': scancode, 'modifiers': []}
        
        # Пробел
        layout[' '] = {'scancode': '39', 'modifiers': []}
        
        return layout