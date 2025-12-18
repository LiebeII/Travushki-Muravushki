import json
import matplotlib.pyplot as plt
from typing import Dict, List, Any
import numpy as np
from collections import defaultdict
import re
import os
import glob

from visualization.stats_formatter import format_number
from visualization.charts import visualize_finger_statistics, visualize_combo_distribution
from analysis.text_processor import file_to_words_set, detect_language_ratio
from analysis.combo_analyzer import combos_counter, scancode_from_char, key_from_value
from analysis.finger_penalty_calculator import FingerPenaltyCalculator
from layouts.layout_data import LayoutData


class LayoutEvaluator:
    def __init__(self):
        # Загрузка предустановленных раскладок
        self.layouts = self.load_default_layouts()
        self.current_layout = None
        self.data = LayoutData()
        self.penalty_calculator = FingerPenaltyCalculator()
        self.max_combos_length = 4
        
        # Статистика для всех раскладок
        self.all_layouts_stats = {}
        
        # Языки раскладок
        self.layout_languages = {
            'ЙЦУКЕН': 'russian',
            'Скоропись': 'russian',
            'Фонетическая (яВерт)': 'russian',
            'Диктор': 'russian',
            'QWERTY': 'english',
            'Dvorak': 'english',
            'Colemak': 'english',
            'Workman': 'english'
        }
        
        # Автоматический импорт раскладок из папки
        self.import_layouts_from_folder()
    
    def import_layouts_from_folder(self):
        """Автоматически импортирует все .json файлы из папки ready_made_layouts"""
        folder_path = 'ready_made_layouts'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Создана папка {folder_path}")
            return
        
        json_files = glob.glob(os.path.join(folder_path, '*.json'))
        for json_file in json_files:
            try:
                layout_name = self.load_custom_layout(json_file)
                if layout_name:
                    print(f"Автоматически загружена раскладка: {layout_name}")
            except Exception as e:
                print(f"Ошибка при загрузке {json_file}: {e}")
    
    def load_default_layouts(self) -> Dict[str, Any]:
        """Загружает предустановленные раскладки (ТОЛЬКО ЦИФРЫ И БУКВЫ)"""
        default_layouts = {}
        
        # ЙЦУКЕН (стандартная русская) - ТОЛЬКО ЦИФРЫ И БУКВЫ
        default_layouts['ЙЦУКЕН'] = {
            "name": "ЙЦУКЕН",
            "language": "russian",
            "layout": [
                ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                ["й", "ц", "у", "к", "е", "н", "г", "ш", "щ", "з", "х", "ъ"],
                ["ф", "ы", "в", "а", "п", "р", "о", "л", "д", "ж", "э"],
                ["я", "ч", "с", "м", "и", "т", "ь", "б", "ю"]
            ]
        }
        
        # Скоропись (русская эргономичная) - ТОЛЬКО ЦИФРЫ И БУКВЫ
        default_layouts['Скоропись'] = {
            "name": "Скоропись",
            "language": "russian",
            "layout": [
                ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                ["ц", "у", "а", "о", "в", "п", "р", "л", "д", "ж", "э"],
                ["й", "к", "е", "н", "г", "ш", "з", "х", "ъ", "ф", "ы"],
                ["я", "ч", "с", "м", "и", "т", "ь", "б", "ю"]
            ]
        }
        
        # Фонетическая (яВерт) - ТОЛЬКО ЦИФРЫ И БУКВЫ
        default_layouts['Фонетическая (яВерт)'] = {
            "name": "Фонетическая (яВерт)",
            "language": "russian",
            "layout": [
                ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                ["я", "в", "е", "р", "т", "ы", "у", "и", "о", "п"],
                ["а", "с", "д", "ф", "г", "х", "й", "к", "л"],
                ["з", "ь", "ц", "ж", "б", "н", "м", "ш", "щ", "ч"]
            ]
        }
        
        # Диктор (русская эргономичная для диктовки) - ТОЛЬКО ЦИФРЫ И БУКВЫ
        default_layouts['Диктор'] = {
            "name": "Диктор",
            "language": "russian",
            "layout": [
                ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                ["н", "т", "с", "р", "в", "м", "д", "п", "л", "г", "б", "ь"],
                ["о", "а", "е", "и", "у", "к", "я", "ы", "з", "ж", "э"],
                ["й", "ч", "х", "ц", "ф", "ш", "щ", "ю"]
            ]
        }
        
        # QWERTY (английская) - ТОЛЬКО ЦИФРЫ И БУКВЫ
        default_layouts['QWERTY'] = {
            "name": "QWERTY",
            "language": "english",
            "layout": [
                ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
                ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
                ["z", "x", "c", "v", "b", "n", "m"]
            ]
        }
        
        # Dvorak (эргономичная английская) - ТОЛЬКО ЦИФРЫ И БУКВЫ
        default_layouts['Dvorak'] = {
            "name": "Dvorak",
            "language": "english",
            "layout": [
                ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                ["p", "y", "f", "g", "c", "r", "l"],
                ["a", "o", "e", "u", "i", "d", "h", "t", "n", "s"],
                ["q", "j", "k", "x", "b", "m", "w", "v", "z"]
            ]
        }
        
        # Colemak (эргономичная английская) - ТОЛЬКО ЦИФРЫ И БУКВЫ
        default_layouts['Colemak'] = {
            "name": "Colemak",
            "language": "english",
            "layout": [
                ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                ["q", "w", "f", "p", "g", "j", "l", "u", "y"],
                ["a", "r", "s", "t", "d", "h", "n", "e", "i", "o"],
                ["z", "x", "c", "v", "b", "k", "m"]
            ]
        }
        
        # Workman (эргономичная английская) - ТОЛЬКО ЦИФРЫ И БУКВЫ
        default_layouts['Workman'] = {
            "name": "Workman",
            "language": "english",
            "layout": [
                ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                ["q", "d", "r", "w", "b", "j", "f", "u", "p"],
                ["a", "s", "h", "t", "g", "y", "n", "e", "o", "i"],
                ["z", "x", "m", "c", "v", "k", "l"]
            ]
        }
        
        print(f"Загружено {len(default_layouts)} предустановленных раскладок")
        return default_layouts
    
    def show_all_layouts(self):
        """Показывает все доступные раскладки"""
        print("\n" + "="*60)
        print("ДОСТУПНЫЕ РАСКЛАДКИ")
        print("="*60)
        
        for name in self.layouts.keys():
            self.standardize_layout_display(name)
    
    def standardize_layout_display(self, layout_name: str):
        """Стандартизирует отображение раскладки (только буквы и цифры)"""
        if layout_name in self.layouts:
            layout = self.layouts[layout_name]
            rows = layout.get('layout', [])
            
            print(f"\n{layout_name} ({self.layout_languages.get(layout_name, 'неизвестен')}):")
            
            for row_idx, row in enumerate(rows):
                # Фильтруем только буквы и цифры для отображения
                filtered_row = [char for char in row if char.isalnum()]
                if filtered_row:  # Показываем только если есть буквы/цифры
                    print(f"  Ряд {row_idx + 1}: {' '.join(filtered_row)}")
    
    def load_custom_layout(self, layout_file: str):
        """Загружает кастомную раскладку из JSON файла"""
        try:
            with open(layout_file, 'r', encoding='utf-8') as f:
                layout_data = json.load(f)
            
            layout_name = layout_data.get('name', os.path.basename(layout_file).replace('.json', ''))
            self.layouts[layout_name] = layout_data
            
            # Определяем язык раскладки
            language = layout_data.get('language', 'unknown')
            self.layout_languages[layout_name] = language
            
            # Создаем карту раскладки если ее нет
            if layout_name not in self.data.layout_maps:
                self.data.layout_maps[layout_name] = self.create_layout_map_from_data(layout_data)
            
            print(f"Раскладка '{layout_name}' загружена успешно")
            return layout_name
            
        except FileNotFoundError:
            print(f"Файл {layout_file} не найден")
            return None
        except json.JSONDecodeError:
            print(f"Ошибка чтения JSON файла {layout_file}")
            return None
    
    def create_layout_map_from_data(self, layout_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создает карту раскладки из данных (только буквы и цифры) с учетом второго слоя через LAlt"""
        layout_map = {}
        
        # Собираем все символы из раскладки
        if 'layout' in layout_data:
            scancodes = [
                '02', '03', '04', '05', '06', '07', '08', '09', '0A', '0B',  # цифровой ряд
                '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '1A', '1B',  # верхний ряд
                '1E', '1F', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29',  # домашний ряд
                '2C', '2D', '2E', '2F', '30', '31', '32', '33', '34', '35', '36', '37',  # нижний ряд
                '38'  # LAlt
            ]
            
            scancode_idx = 0
            
            for row in layout_data['layout']:
                for cell in row:
                    if cell.strip():
                        if scancode_idx < len(scancodes):
                            scancode = scancodes[scancode_idx]
                            scancode_idx += 1
                            
                            # Обрабатываем клетки с двумя символами через "/"
                            if '/' in cell:
                                parts = cell.split('/')
                                if len(parts) >= 2:
                                    # Первый символ - основной (без модификаторов)
                                    primary_char = parts[0].strip()
                                    # Второй символ - с Alt
                                    alt_char = parts[1].strip() if len(parts) > 1 else ''
                                    
                                    # Добавляем основной символ (если еще не добавлен)
                                    if primary_char and len(primary_char) == 1:
                                        self._add_char_to_layout(layout_map, primary_char, scancode, [])
                                    
                                    # Добавляем Alt-символ (если еще не добавлен)
                                    if alt_char and len(alt_char) == 1:
                                        self._add_char_to_layout(layout_map, alt_char, scancode, ['alt'])
                            else:
                                # Одиночный символ
                                char = cell.strip()
                                if len(char) == 1:
                                    self._add_char_to_layout(layout_map, char, scancode, [])
        
        # Добавляем пробел
        layout_map[' '] = {'scancode': '39', 'modifiers': []}
        
        return layout_map
    
    def _add_char_to_layout(self, layout_map: Dict[str, Any], char: str, scancode: str, base_modifiers: List[str]) -> None:
        """Добавляет символ в карту раскладки, выбирая вариант с наименьшим штрафом"""
        # Вычисляем штраф для этого варианта
        penalty = self._calculate_penalty_for_scancode(scancode, base_modifiers)
        
        # Проверяем, есть ли уже этот символ в карте
        if char in layout_map:
            existing_entry = layout_map[char]
            existing_scancode = existing_entry.get('scancode')
            existing_modifiers = existing_entry.get('modifiers', [])
            
            # Вычисляем штраф для существующего варианта
            existing_penalty = self._calculate_penalty_for_scancode(existing_scancode, existing_modifiers)
            
            # Выбираем вариант с наименьшим штрафом
            if penalty < existing_penalty:
                layout_map[char] = {'scancode': scancode, 'modifiers': base_modifiers.copy()}
                
                # Также добавляем вариант с Shift, если это буква
                if char.isalpha() and char.islower():
                    upper_char = char.upper()
                    if upper_char not in layout_map or penalty < self._calculate_penalty_for_scancode(
                        layout_map[upper_char].get('scancode'), layout_map[upper_char].get('modifiers', [])
                    ):
                        layout_map[upper_char] = {'scancode': scancode, 'modifiers': base_modifiers + ['shift']}
                        
        else:
            # Добавляем новый символ
            layout_map[char] = {'scancode': scancode, 'modifiers': base_modifiers.copy()}
            
            # Также добавляем вариант с Shift, если это буква
            if char.isalpha() and char.islower():
                layout_map[char.upper()] = {'scancode': scancode, 'modifiers': base_modifiers + ['shift']}
            elif char.isalpha() and char.isupper():
                layout_map[char.lower()] = {'scancode': scancode, 'modifiers': base_modifiers}
    
    def _calculate_penalty_for_scancode(self, scancode: str, modifiers: List[str]) -> float:
        """Рассчитывает штраф для сканкода с модификаторами"""
        # Базовая логика расчета штрафа
        penalty = 0.0
        
        if not scancode:
            return 9999.0  # Большой штраф для невалидного сканкода
        
        # Расчет штрафа за модификаторы
        if 'shift' in modifiers:
            # Штраф за Shift зависит от пальца
            finger = self._get_finger_for_scancode_temp(scancode)
            if finger in ['left_pinky', 'right_pinky']:
                penalty += 3.0  # Shift penalty
            else:
                penalty += 1.5
        
        if 'alt' in modifiers:
            # Небольшой штраф за Alt
            penalty += 0.5
        
        # Штраф за расстояние от домашнего ряда (упрощенный)
        # Можно добавить более сложную логику при необходимости
        
        return penalty
    
    def _get_finger_for_scancode_temp(self, scancode: str) -> str:
        """Вспомогательная функция для определения пальца по сканкоду"""
        # Временная реализация - можно вынести в отдельный класс
        key_finger = {
            'left_pinky': ['02', '10', '1E', '2C', '38'],
            'left_ring': ['03', '11', '1F', '2D'],
            'left_middle': ['04', '12', '20', '2E'],
            'left_index': ['05', '13', '21', '2F', '06', '14', '22', '30'],
            'right_index': ['07', '15', '23', '31', '08', '16', '24', '32'],
            'right_middle': ['09', '17', '25', '33'],
            'right_ring': ['0A', '18', '26', '34'],
            'right_pinky': ['0B', '19', '27', '35', '0C', '1A', '28', '36', '29', '0D', '1B', '37'],
        }
        
        for finger, scancodes in key_finger.items():
            if scancode in scancodes:
                return finger
        return None
    
    def set_layout(self, layout_name: str):
        """Устанавливает текущую раскладку"""
        if layout_name in self.layouts:
            self.current_layout = self.layouts[layout_name]
            print(f"Текущая раскладка: {layout_name}")
        else:
            print(f"Раскладка '{layout_name}' не найдена")
    
    def filter_layouts_by_language(self, text_file: str) -> List[str]:
        """Фильтрует раскладки по языку текста"""
        try:
            with open(text_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            language_ratio = detect_language_ratio(text)
            print(f"Языковой состав текста: Русский {language_ratio['russian']*100:.1f}%, Английский {language_ratio['english']*100:.1f}%")
            
            # Фильтруем раскладки
            filtered_layouts = []
            for layout_name in self.layouts.keys():
                layout_lang = self.layout_languages.get(layout_name, 'unknown')
                
                if layout_lang == 'russian' and language_ratio['russian'] >= 0.1:
                    filtered_layouts.append(layout_name)
                elif layout_lang == 'english' and language_ratio['english'] >= 0.1:
                    filtered_layouts.append(layout_name)
                elif layout_lang == 'unknown':
                    filtered_layouts.append(layout_name)
            
            print(f"Для анализа выбрано {len(filtered_layouts)} раскладок (из {len(self.layouts)})")
            return filtered_layouts
            
        except Exception as e:
            print(f"Ошибка при анализе языка текста: {e}")
            return list(self.layouts.keys())
    
    def analyze_combinations_all_layouts(self, text_file: str = None):
        """Анализирует комбинации символов для всех раскладок"""
        print("\n" + "="*60)
        print("АНАЛИЗ КОМБИНАЦИЙ СИМВОЛОВ ДЛЯ ВСЕХ РАСКЛАДОК")
        print("="*60)
        
        # Определяем какой файл использовать
        if text_file:
            source_file = text_file
        else:
            # Пробуем загрузить данные из разных файлов
            files_to_try = ['1grams-3.txt', 'sortchbukw.csv', 'test_text.txt']
            source_file = None
            
            for file_name in files_to_try:
                try:
                    with open(file_name, 'r', encoding='utf-8') as f:
                        text = f.read()
                    source_file = file_name
                    break
                except:
                    continue
            
            if not source_file:
                print("Создание тестовых файлов...")
                self.create_test_files()
                source_file = 'test_text.txt'
        
        # Загрузка данных
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            print(f"Файл {source_file} не найден")
            return
        
        words_set = file_to_words_set(source_file, min_length=2)  # Отбрасываем односимвольные слова
        
        if not words_set:
            print("Не удалось загрузить данные для анализа")
            return
        
        print(f"Загружено {len(words_set)} уникальных слов из файла {source_file}")
        print(f"Проанализировано слов: {format_number(len(words_set))}")
        
        # Фильтруем раскладки по языку текста
        if text_file:
            layouts_to_analyze = self.filter_layouts_by_language(text_file)
        else:
            layouts_to_analyze = list(self.layouts.keys())
        
        # Подсчет комбинаций
        combos = combos_counter(words_set, self.max_combos_length)
        
        # Анализ для каждой раскладки
        layouts_stats = {}
        
        for layout_name in layouts_to_analyze:
            print(f"\nАнализ для раскладки: {layout_name}")
            
            layout_map = self.data.layout_maps.get(layout_name)
            if not layout_map:
                print(f"  Нет карты для раскладки {layout_name}")
                continue
            
            # Анализируем комбинации с динамическими штрафами
            comfort_combos, partial_combos, uncomfortable_combos, dynamic_scores = self.data.calculate_dynamic_penalties(
                words_set, layout_map
            )
            
            # Преобразуем в формат для статистики
            total_comfort = sum(comfort_combos.values())
            total_partial = sum(partial_combos.values())
            total_uncomfortable = sum(uncomfortable_combos.values())
            
            # Подсчет штрафа на пальцы (расстояние от домашнего ряда)
            finger_penalty = self.penalty_calculator.calculate_finger_penalty(text, layout_map)
            
            # Статистика по пальцам
            finger_load = self.penalty_calculator.calculate_finger_load(text, layout_map)
            
            # Анализ баланса рук
            hand_balance = self.data.calculate_hand_balance(text, layout_map)
            
            # Анализ двухсимвольных комбинаций
            two_char_analysis = self.data.analyze_two_char_combinations(
                combos.get(2, {}), layout_map
            )
            
            layouts_stats[layout_name] = {
                'comfort_combos': comfort_combos,
                'partial_combos': partial_combos,
                'uncomfortable_combos': uncomfortable_combos,
                'total_comfort': total_comfort,
                'total_partial': total_partial,
                'total_uncomfortable': total_uncomfortable,
                'two_char_analysis': two_char_analysis,
                'finger_load': finger_load,
                'finger_penalty': finger_penalty,
                'hand_balance': hand_balance,
                'avg_dynamic_score': np.mean(list(dynamic_scores.values())) if dynamic_scores else 0
            }
            
            total_combinations = total_comfort + total_partial + total_uncomfortable
            if total_combinations > 0:
                comfort_percent = total_comfort / total_combinations * 100
                partial_percent = total_partial / total_combinations * 100
                uncomfortable_percent = total_uncomfortable / total_combinations * 100
            else:
                comfort_percent = partial_percent = uncomfortable_percent = 0
            
            print(f"  Всего комбинаций: {format_number(total_combinations)}")
            print(f"  Удобные: {format_number(total_comfort)} ({comfort_percent:.1f}%)")
            print(f"  Частично удобные: {format_number(total_partial)} ({partial_percent:.1f}%)")
            print(f"  Неудобные: {format_number(total_uncomfortable)} ({uncomfortable_percent:.1f}%)")
            print(f"  Штраф на пальцы: {finger_penalty:.0f}")
            print(f"  Баланс рук: {hand_balance['left_percent']:.1f}% левая, {hand_balance['right_percent']:.1f}% правая")
            if hand_balance['is_good']:
                print(f"  ✓ Хороший баланс рук (в пределах 45-55%)")
            else:
                print(f"  ✗ Плохой баланс рук")
            print(f"  Двухсимвольные комбинации: {format_number(two_char_analysis['one_hand_total'])} одноручных")
        
        # Сохраняем статистику
        self.all_layouts_stats = layouts_stats
        
        # Выводим сравнение
        self.print_combinations_comparison(layouts_stats)
        
        # Визуализация
        if layouts_stats:
            visualize_finger_statistics(layouts_stats, source_file)
            visualize_combo_distribution(layouts_stats, source_file)
    
    def print_combinations_comparison(self, layouts_stats: Dict[str, Any]):
        """Выводит сравнение результатов анализа комбинаций с правильными рейтингами"""
        print("\n" + "="*120)
        print("СРАВНЕНИЕ РАСКЛАДОК ПО КОМБИНАЦИЯМ СИМВОЛОВ")
        print("="*120)
        
        # Собираем данные по всем раскладкам
        layout_data = []
        
        for layout_name, stats in layouts_stats.items():
            total_combinations = stats['total_comfort'] + stats['total_partial'] + stats['total_uncomfortable']
            finger_penalty = stats['finger_penalty']
            
            if total_combinations > 0:
                comfort_percent = stats['total_comfort'] / total_combinations * 100
            else:
                comfort_percent = 0
            
            # Нагрузка на пальцы: вычисляем равномерность распределения
            finger_load = stats['finger_load']
            
            # Список всех пальцев (без больших пальцев)
            fingers = ['left_pinky', 'left_ring', 'left_middle', 'left_index',
                      'right_index', 'right_middle', 'right_ring', 'right_pinky']
            
            # Собираем значения нагрузки для всех пальцев
            finger_values = []
            for finger in fingers:
                finger_values.append(finger_load.get(finger, 0))
            
            # Вычисляем стандартное отклонение для оценки равномерности
            # Чем меньше стандартное отклонение, тем равномернее нагрузка
            if len(finger_values) > 1:
                std_dev = np.std(finger_values)
                # Преобразуем в балл равномерности (чем меньше std_dev, тем выше балл)
                max_value = max(finger_values) if max(finger_values) > 0 else 1
                uniformity_score = 100 * (1 - (std_dev / max_value))
            else:
                uniformity_score = 0
            
            # Баланс рук
            hand_balance = stats['hand_balance']
            left_percent = hand_balance.get('left_percent', 50)
            right_percent = hand_balance.get('right_percent', 50)
            balance_score = hand_balance.get('balance_score', 0)
            
            # Общая нагрузка (для информации)
            total_finger_load = sum(finger_values)
            
            layout_data.append({
                'name': layout_name,
                'comfort_percent': comfort_percent,
                'finger_penalty': finger_penalty,
                'uniformity_score': uniformity_score,
                'total_finger_load': total_finger_load,
                'balance_score': balance_score,
                'is_good_balance': hand_balance.get('is_good', False),
                'finger_values': finger_values
            })
        
        # Рассчитываем места по каждой категории
        # Чем меньше значение (кроме comfort_percent, uniformity_score и balance_score), тем лучше
        
        # 1. Удобные комбинации % (чем больше, тем лучше)
        comfort_sorted = sorted(layout_data, key=lambda x: x['comfort_percent'], reverse=True)
        for i, layout in enumerate(comfort_sorted):
            layout['comfort_place'] = i + 1
        
        # 2. Штраф на пальцы (чем меньше, тем лучше)
        penalty_sorted = sorted(layout_data, key=lambda x: x['finger_penalty'])
        for i, layout in enumerate(penalty_sorted):
            layout['penalty_place'] = i + 1
        
        # 3. Равномерность нагрузки на пальцы (чем больше uniformity_score, тем лучше)
        uniformity_sorted = sorted(layout_data, key=lambda x: x['uniformity_score'], reverse=True)
        for i, layout in enumerate(uniformity_sorted):
            layout['uniformity_place'] = i + 1
        
        # 4. Баланс рук (чем ближе к 100%, тем лучше)
        balance_sorted = sorted(layout_data, key=lambda x: x['balance_score'], reverse=True)
        for i, layout in enumerate(balance_sorted):
            layout['balance_place'] = i + 1
        
        # Рассчитываем итоговый рейтинг (сумма мест)
        for layout in layout_data:
            layout['total_place'] = (
                layout['comfort_place'] + 
                layout['penalty_place'] + 
                layout['uniformity_place'] + 
                layout['balance_place']
            )
        
        # Сортируем по итоговому рейтингу (чем меньше сумма мест, тем лучше)
        sorted_layouts = sorted(layout_data, key=lambda x: x['total_place'])
        
        # Выводим таблицу сравнения
        print(f"\n{'Раскладка':<25} {'Удобные %':<12} {'Штраф':<12} {'Равномер.':<10} {'Баланс':<10} {'Места/Итог':<25}")
        print("-" * 120)
        
        for i, layout in enumerate(sorted_layouts):
            name = layout['name']
            comfort_str = f"{layout['comfort_percent']:.1f}%"
            penalty_str = f"{layout['finger_penalty']:.0f}"
            
            # Форматируем равномерность нагрузки
            uniformity_str = f"{layout['uniformity_score']:.1f}%"
            
            balance_str = f"{layout['balance_score']:.1f}%"
            
            # Места по категориям
            places_str = f"{layout['comfort_place']}+{layout['penalty_place']}+{layout['uniformity_place']}+{layout['balance_place']}={layout['total_place']}"
            
            # Итоговое место
            final_place = i + 1
            rating_str = f"#{final_place} ({places_str})"
            
            print(f"{name:<25} {comfort_str:<12} {penalty_str:<12} {uniformity_str:<10} {balance_str:<10} {rating_str:<25}")
        
        # Выводим детальные рейтинги по критериям
        print("\n" + "="*120)
        print("ДЕТАЛЬНЫЙ РЕЙТИНГ ПО КРИТЕРИЯМ")
        print("="*120)
        
        categories = [
            ('Удобные комбинации %', 'comfort_percent', True),
            ('Штраф на пальцы', 'finger_penalty', False),
            ('Равномерность нагрузки', 'uniformity_score', True),
            ('Баланс рук', 'balance_score', True)
        ]
        
        for category_name, field_name, reverse in categories:
            print(f"\n{category_name}:")
            
            if reverse:
                sorted_by_cat = sorted(layout_data, key=lambda x: x[field_name], reverse=True)
            else:
                sorted_by_cat = sorted(layout_data, key=lambda x: x[field_name])
            
            for i, layout in enumerate(sorted_by_cat):
                value = layout[field_name]
                
                if 'percent' in field_name or 'score' in field_name or 'uniformity' in field_name:
                    value_str = f"{value:.1f}%"
                elif 'penalty' in field_name:
                    value_str = f"{value:.0f}"
                else:
                    value_str = str(value)
                
                print(f"  {i+1}. {layout['name']:<25} - {value_str}")
        
        # Дополнительно: выводим распределение нагрузки по пальцам
        print("\n" + "="*120)
        print("РАСПРЕДЕЛЕНИЕ НАГРУЗКИ ПО ПАЛЬЦАМ")
        print("="*120)
        
        finger_names = ['Л.мизин', 'Л.безым', 'Л.средн', 'Л.указ', 
                       'П.указ', 'П.средн', 'П.безым', 'П.мизин']
        
        for layout in sorted_layouts[:5]:  # Только топ-5
            print(f"\n{layout['name']}:")
            finger_values = layout['finger_values']
            total = sum(finger_values)
            
            if total > 0:
                for i, (finger_name, value) in enumerate(zip(finger_names, finger_values)):
                    percent = (value / total) * 100
                    bar_length = int(percent / 5)  # 1 символ = 5%
                    bar = "█" * bar_length
                    print(f"  {finger_name}: {value:>6} ({percent:5.1f}%) {bar}")
    
    def create_test_files(self):
        """Создает тестовые файлы если они отсутствуют"""
        # Многоязычный тестовый текст
        test_text = """Привет! Hello! Это тестовый текст для анализа клавиатурных раскладок.
        Программа сравнивает эргономику разных раскладок на основе комбинаций символов.
        
        Русский текст: ЙЦУКЕН, Скоропись, фонетические раскладки.
        English text: QWERTY, Dvorak, Colemak, Workman layouts.
        
        Клавиатурная эргономика важна для быстрого и комфортного набора текста.
        Keyboard ergonomics is important for fast and comfortable typing.
        
        Тестируем различные комбинации: привет, hello, программа, algorithm,
        разработка, development, тестирование, testing, анализ, analysis."""
        
        with open('test_text.txt', 'w', encoding='utf-8') as f:
            f.write(test_text)
        
        print("Тестовый файл создан")