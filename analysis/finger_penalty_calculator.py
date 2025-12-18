"""
Расчет штрафа на основе расстояния от домашнего ряда
"""

from typing import Dict, Any, Tuple, List
from collections import defaultdict


class FingerPenaltyCalculator:
    """Класс для расчета штрафов на основе расстояния от домашнего ряда"""
    
    def __init__(self):
        # Соответствие сканкодов позициям на клавиатуре (ряд, колонка)
        # Основано на стандартной QWERTY раскладке
        self.key_positions = {
            # Цифровой ряд (ряд 2)
            '02': (2, 0), '03': (2, 1), '04': (2, 2), '05': (2, 3), '06': (2, 4),
            '07': (2, 5), '08': (2, 6), '09': (2, 7), '0A': (2, 8), '0B': (2, 9),
            
            # Верхний ряд (ряд 1)
            '10': (1, 0), '11': (1, 1), '12': (1, 2), '13': (1, 3), '14': (1, 4),
            '15': (1, 5), '16': (1, 6), '17': (1, 7), '18': (1, 8), '19': (1, 9),
            '1A': (1, 10), '1B': (1, 11),
            
            # Домашний ряд (ряд 0)
            '1E': (0, 0), '1F': (0, 1), '20': (0, 2), '21': (0, 3), '22': (0, 4),
            '23': (0, 5), '24': (0, 6), '25': (0, 7), '26': (0, 8), '27': (0, 9),
            '28': (0, 10), '29': (0, 11),
            
            # Нижний ряд (ряд -1)
            '2C': (-1, 0), '2D': (-1, 1), '2E': (-1, 2), '2F': (-1, 3), '30': (-1, 4),
            '31': (-1, 5), '32': (-1, 6), '33': (-1, 7), '34': (-1, 8), '35': (-1, 9),
            '36': (-1, 10), '37': (-1, 11),
            
            # LAlt для раскладок с двумя буквами на одной позиции
            '38': (-1, 0),
            
            # Пробел
            '39': (-2, 5),
        }
        
        # Домашняя позиция для каждого пальца (ряд, колонка) для стандартной QWERTY
        self.home_positions = {
            'left_pinky': (0, 0),   # A
            'left_ring': (0, 1),    # S
            'left_middle': (0, 2),  # D
            'left_index': (0, 3),   # F
            
            'right_index': (0, 5),  # J
            'right_middle': (0, 6), # K
            'right_ring': (0, 7),   # L
            'right_pinky': (0, 8),  # ;
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
        
        # Дополнительный штраф за использование Shift мизинцем
        self.shift_penalty = 3.0
        
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
    
    def get_key_position(self, scancode: str) -> Tuple[int, int]:
        """Получает позицию клавиши (ряд, колонка)"""
        return self.key_positions.get(scancode, (0, 0))
    
    def get_home_position(self, finger: str) -> Tuple[int, int]:
        """Получает домашнюю позицию для пальца"""
        return self.home_positions.get(finger, (0, 0))
    
    def calculate_distance(self, scancode: str, finger: str) -> int:
        """
        Рассчитывает расстояние от домашнего ряда
        Правило: считаем количество клавиш, которые нужно пройти
        """
        if not scancode or not finger or finger not in self.home_positions:
            return 0
        
        # Получаем позиции
        key_pos = self.get_key_position(scancode)
        home_pos = self.get_home_position(finger)
        
        # Если это домашняя позиция для этого пальца
        if key_pos == home_pos:
            return 0
        
        # Расчет расстояния (манхэттенское расстояние)
        # Расстояние по рядам + расстояние по колонкам
        row_distance = abs(key_pos[0] - home_pos[0])
        col_distance = abs(key_pos[1] - home_pos[1])
        
        # Общее расстояние = сумма расстояний по рядам и колонкам
        # Это и есть количество клавиш, которые нужно пройти
        total_distance = row_distance + col_distance
        
        return total_distance
    
    def calculate_shift_penalty(self, char: str, layout_map: Dict[str, Any]) -> float:
        """Рассчитывает штраф за использование Shift и Alt"""
        if char in layout_map:
            scancode_info = layout_map[char]
            if isinstance(scancode_info, dict):
                modifiers = scancode_info.get('modifiers', [])
                scancode = scancode_info.get('scancode')
                
                total_penalty = 0.0
                
                # Штраф за Shift
                if 'shift' in modifiers:
                    if scancode:
                        finger = self.get_finger_for_scancode(scancode)
                        # Штраф за Shift выше, если используется мизинец
                        if finger in ['left_pinky', 'right_pinky']:
                            total_penalty += self.shift_penalty
                        else:
                            total_penalty += self.shift_penalty * 0.5
                
                # Штраф за Alt (меньше, чем за Shift, так как Alt обычно нажимается большим пальцем)
                if 'alt' in modifiers:
                    # Alt нажимается большим пальцем, который не учитывается в штрафах за пальцы
                    # Но сам факт использования модификатора дает небольшой штраф
                    total_penalty += 0.5  # Небольшой штраф за использование Alt
                
                return total_penalty
        return 0.0
    
    def calculate_penalty_for_char(self, char: str, layout_map: Dict[str, Any]) -> float:
        """Рассчитывает штраф для символа"""
        if not char or char == ' ':
            return 0.0
        
        if char in layout_map:
            scancode_info = layout_map[char]
            if isinstance(scancode_info, dict):
                scancode = scancode_info.get('scancode')
                modifiers = scancode_info.get('modifiers', [])
                
                if scancode and scancode != '39':  # Игнорируем пробел
                    # Определяем палец для этого сканкода
                    finger = self.get_finger_for_scancode(scancode)
                    if finger:
                        # Штраф = расстояние от домашнего ряда
                        distance = self.calculate_distance(scancode, finger)
                        
                        # Дополнительный штраф за модификаторы
                        modifier_penalty = 0.0
                        
                        if 'shift' in modifiers:
                            # Штраф за Shift выше, если используется мизинец
                            if finger in ['left_pinky', 'right_pinky']:
                                modifier_penalty += self.shift_penalty
                            else:
                                modifier_penalty += self.shift_penalty * 0.5
                        
                        if 'alt' in modifiers:
                            # Небольшой штраф за использование Alt
                            modifier_penalty += 0.5
                        
                        # Общий штраф = расстояние + штраф за модификаторы
                        return distance + modifier_penalty
        
        return 0.0
    
    def calculate_finger_penalty(self, text: str, layout_map: Dict[str, Any]) -> float:
        """
        Рассчитывает общий штраф для текста
        Штраф накапливается для каждого символа
        """
        total_penalty = 0.0
        char_count = 0
        
        for char in text:
            if char.strip() and char != ' ':
                penalty = self.calculate_penalty_for_char(char, layout_map)
                total_penalty += penalty
                char_count += 1
        
        # Возвращаем суммарный штраф (не средний!)
        return total_penalty
    
    def calculate_finger_load(self, text: str, layout_map: Dict[str, Any]) -> Dict[str, int]:
        """Подсчет нагрузки на пальцы (количество кликов)"""
        finger_load = defaultdict(int)
        
        for char in text:
            if char.strip() and char != ' ':
                if char in layout_map:
                    scancode_info = layout_map[char]
                    if isinstance(scancode_info, dict):
                        scancode = scancode_info.get('scancode')
                        if scancode and scancode != '39':  # Игнорируем пробел
                            finger = self.get_finger_for_scancode(scancode)
                            if finger:
                                finger_load[finger] += 1
        
        return finger_load