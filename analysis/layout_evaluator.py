import json
import matplotlib.pyplot as plt
from typing import Dict, List, Any
import numpy as np
from collections import defaultdict
import re

from visualization.stats_formatter import format_number
from visualization.charts import visualize_finger_statistics, visualize_combo_distribution
from analysis.text_processor import file_to_words_set, detect_language_ratio
from analysis.combo_analyzer import combos_counter, conditional_combos_counter, combos_dict_to_combos_count_dict, scancode_from_char, key_from_value
from layouts.layout_data import LayoutData


class LayoutEvaluator:
    def __init__(self):
        # Загрузка предустановленных раскладок
        self.layouts = self.load_default_layouts()
        self.current_layout = None
        self.data = LayoutData()
        self.max_combos_length = 4
        
        # Статистика для всех раскладок
        self.all_layouts_stats = {}
        
        # Языки раскладок
        self.layout_languages = {
            'ЙЦУКЕН': 'russian',
            'Скоропись': 'russian',
            'Фонетическая (яВерт)': 'russian',
            'Вызов': 'russian',
            'QWERTY': 'english',
            'Dvorak': 'english',
            'Colemak': 'english',
            'Workman': 'english'
        }
    
    def load_default_layouts(self) -> Dict[str, Any]:
        """Загружает предустановленные раскладки"""
        default_layouts = {}
        
        # ЙЦУКЕН (стандартная русская)
        default_layouts['ЙЦУКЕН'] = {
            "name": "ЙЦУКЕН",
            "language": "russian",
            "layout": [
                ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "="],
                ["й", "ц", "у", "к", "е", "н", "г", "ш", "щ", "з", "х", "ъ"],
                ["ф", "ы", "в", "а", "п", "р", "о", "л", "д", "ж", "э"],
                ["я", "ч", "с", "м", "и", "т", "ь", "б", "ю", "."]
            ]
        }
        
        # Скоропись (русская эргономичная)
        default_layouts['Скоропись'] = {
            "name": "Скоропись",
            "language": "russian",
            "layout": [
                ["ц", "у", "а", "о", "в", "п", "р", "л", "д", "ж", "э"],
                ["й", "к", "е", "н", "г", "ш", "з", "х", "ъ", "ф", "ы"],
                ["я", "ч", "с", "м", "и", "т", "ь", "б", "ю", "ё"]
            ]
        }
        
        # Фонетическая (яВерт)
        default_layouts['Фонетическая (яВерт)'] = {
            "name": "Фонетическая (яВерт)",
            "language": "russian",
            "layout": [
                ["я", "в", "е", "р", "т", "ы", "у", "и", "о", "п"],
                ["а", "с", "д", "ф", "г", "х", "й", "к", "л"],
                ["з", "ь", "ц", "ж", "б", "н", "м", "ш", "щ", "ч"]
            ]
        }
        
        # Вызов (альтернативная русская)
        default_layouts['Вызов'] = {
            "name": "Вызов",
            "language": "russian",
            "layout": [
                ["б", "х", "т", "ч", "щ", "ш", "г", "а", "у", "э"],
                ["в", "н", "д", "р", "й", "ж", "с", "о", "и", "я"],
                ["к", "п", "м", "л", "ц", "ф", "з", "ъ", "ы", "ю"],
                ["ь", "е", " ", " ", " ", " ", "↑", "↑", "ё"]
            ]
        }
        
        # QWERTY (английская)
        default_layouts['QWERTY'] = {
            "name": "QWERTY",
            "language": "english",
            "layout": [
                ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "="],
                ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]", "\\"],
                ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'"],
                ["z", "x", "c", "v", "b", "n", "m", ",", ".", "/"]
            ]
        }
        
        # Dvorak (эргономичная английская)
        default_layouts['Dvorak'] = {
            "name": "Dvorak",
            "language": "english",
            "layout": [
                ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "[", "]"],
                ["'", ",", ".", "p", "y", "f", "g", "c", "r", "l", "/", "=", "\\"],
                ["a", "o", "e", "u", "i", "d", "h", "t", "n", "s", "-"],
                [";", "q", "j", "k", "x", "b", "m", "w", "v", "z"]
            ]
        }
        
        # Colemak (эргономичная английская)
        default_layouts['Colemak'] = {
            "name": "Colemak",
            "language": "english",
            "layout": [
                ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "="],
                ["q", "w", "f", "p", "g", "j", "l", "u", "y", ";", "[", "]", "\\"],
                ["a", "r", "s", "t", "d", "h", "n", "e", "i", "o", "'"],
                ["z", "x", "c", "v", "b", "k", "m", ",", ".", "/"]
            ]
        }
        
        # Workman (эргономичная английская)
        default_layouts['Workman'] = {
            "name": "Workman",
            "language": "english",
            "layout": [
                ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "="],
                ["q", "d", "r", "w", "b", "j", "f", "u", "p", ";", "[", "]", "\\"],
                ["a", "s", "h", "t", "g", "y", "n", "e", "o", "i", "'"],
                ["z", "x", "m", "c", "v", "k", "l", ",", ".", "/"]
            ]
        }
        
        print(f"Загружено {len(default_layouts)} предустановленных раскладок")
        return default_layouts
    
    def show_all_layouts(self):
        """Показывает все доступные раскладки"""
        print("\n" + "="*60)
        print("ДОСТУПНЫЕ РАСКЛАДКИ")
        print("="*60)
        
        for name, layout in self.layouts.items():
            language = self.layout_languages.get(name, 'неизвестен')
            print(f"\n{name} ({language}):")
            for row_idx, row in enumerate(layout.get('layout', [])):
                print(f"  Ряд {row_idx + 1}: {' '.join(row)}")
    
    def load_custom_layout(self, layout_file: str):
        """Загружает кастомную раскладку из JSON файла"""
        try:
            with open(layout_file, 'r', encoding='utf-8') as f:
                layout_data = json.load(f)
            
            layout_name = layout_data.get('name', layout_file)
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
        """Создает карту раскладки из данных"""
        layout_map = {}
        
        # Собираем все символы из раскладки
        if 'layout' in layout_data:
            scancodes = [
                '02', '03', '04', '05', '06', '07', '08', '09', '0A', '0B', '0C',
                '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '1A',
                '1E', '1F', '20', '21', '22', '23', '24', '25', '26', '27', '28',
                '2C', '2D', '2E', '2F', '30', '31', '32', '33', '34', '35', '36',
                '39'
            ]
            
            scancode_idx = 0
            
            for row in layout_data['layout']:
                for char in row:
                    if char.strip() and len(char) == 1:
                        if scancode_idx < len(scancodes):
                            scancode = scancodes[scancode_idx]
                            scancode_idx += 1
                            
                            # Для букв добавляем оба регистра
                            if char.isalpha():
                                layout_map[char.lower()] = {'scancode': scancode, 'modifiers': []}
                                layout_map[char.upper()] = {'scancode': scancode, 'modifiers': ['shift']}
                            else:
                                layout_map[char] = {'scancode': scancode, 'modifiers': []}
        
        # Добавляем пробел
        layout_map[' '] = {'scancode': '39', 'modifiers': []}
        
        return layout_map
    
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
            
            # Анализируем комбинации
            one_hand_combos, comfort_combos, partial_combos, comfort_scores = conditional_combos_counter(
                combos, layout_map, self.data, self.max_combos_length
            )
            
            # Преобразуем в формат для статистики
            one_hand_count, comfort_count, partial_count = combos_dict_to_combos_count_dict(
                one_hand_combos, comfort_combos, partial_combos
            )
            
            # Анализ двухсимвольных комбинаций
            two_char_analysis = self.data.analyze_two_char_combinations(
                combos.get(2, {}), layout_map
            )
            
            # Статистика по пальцам
            finger_load = self.data.calculate_finger_load(text, layout_map)
            total_penalty = self.data.calculate_finger_penalties_total(text, layout_map)
            hand_penalties = self.data.calculate_hand_penalty_distribution(text, layout_map)
            
            total_one_hand = sum(one_hand_count.values())
            total_comfort = sum(comfort_count.values())
            total_partial = sum(partial_count.values())
            
            layouts_stats[layout_name] = {
                'one_hand': one_hand_count,
                'comfort_count': comfort_count,
                'partial_count': partial_count,
                'total_one_hand': total_one_hand,
                'total_comfort': total_comfort,
                'total_partial': total_partial,
                'two_char_analysis': two_char_analysis,
                'finger_load': finger_load,
                'total_penalty': total_penalty,
                'hand_penalties': hand_penalties,
                'avg_comfort_score': np.mean([score for length_scores in comfort_scores.values() for score in length_scores.values()]) if comfort_scores else 0
            }
            
            if total_one_hand > 0:
                comfort_percent = total_comfort / total_one_hand * 100
                partial_percent = total_partial / total_one_hand * 100
                uncomfortable_percent = 100 - comfort_percent - partial_percent
            else:
                comfort_percent = partial_percent = uncomfortable_percent = 0
            
            print(f"  Всего одноручных комбинаций: {format_number(total_one_hand)}")
            print(f"  Удобные: {format_number(total_comfort)}")
            print(f"  Частично удобные: {format_number(total_partial)}")
            print(f"  Распределение: {comfort_percent:.1f}% удобных, {partial_percent:.1f}% частично удобных, {uncomfortable_percent:.1f}% неудобных")
            print(f"  Общий штраф на пальцы: {total_penalty:.1f}")
            print(f"  Распределение штрафов: {hand_penalties.get('left_percent', 0):.1f}% левая рука, {hand_penalties.get('right_percent', 0):.1f}% правая рука")
            print(f"  Двухсимвольные комбинации: {format_number(two_char_analysis['one_hand_total'])} одноручных, из них {format_number(two_char_analysis['comfortable_one_hand'])} удобных")
        
        # Сохраняем статистику
        self.all_layouts_stats = layouts_stats
        
        # Выводим сравнение
        self.print_combinations_comparison(layouts_stats)
        
        # Визуализация
        if layouts_stats:
            visualize_finger_statistics(layouts_stats, source_file)
            visualize_combo_distribution(layouts_stats, source_file)
    
    def print_combinations_comparison(self, layouts_stats: Dict[str, Any]):
        """Выводит сравнение результатов анализа комбинаций с рейтингами"""
        print("\n" + "="*100)
        print("СРАВНЕНИЕ РАСКЛАДОК ПО КОМБИНАЦИЯМ СИМВОЛОВ")
        print("="*100)
        
        # Собираем все критерии для рейтингов
        criteria_data = {
            'Удобные комбинации %': [],
            'Общий штраф': [],
            'Нагрузка на указательные': [],
            'Баланс рук': []
        }
        
        layout_data = []
        for layout_name, stats in layouts_stats.items():
            total_one_hand = stats['total_one_hand']
            total_comfort = stats['total_comfort']
            total_penalty = stats['total_penalty']
            
            if total_one_hand > 0:
                comfort_percent = total_comfort / total_one_hand * 100
            else:
                comfort_percent = 0
            
            # Нагрузка на указательные пальцы
            index_load = (stats['finger_load'].get('left_index', 0) + 
                         stats['finger_load'].get('right_index', 0))
            
            # Баланс рук
            hand_penalties = stats['hand_penalties']
            left_percent = hand_penalties.get('left_percent', 50)
            right_percent = hand_penalties.get('right_percent', 50)
            balance_score = 100 - abs(left_percent - right_percent)
            
            layout_data.append({
                'name': layout_name,
                'comfort_percent': comfort_percent,
                'total_penalty': total_penalty,
                'index_load': index_load,
                'balance_score': balance_score
            })
            
            criteria_data['Удобные комбинации %'].append(comfort_percent)
            criteria_data['Общий штраф'].append(-total_penalty)  # отрицательный - меньше лучше
            criteria_data['Нагрузка на указательные'].append(-index_load)  # отрицательный - меньше лучше
            criteria_data['Баланс рук'].append(balance_score)
        
        # Вычисляем рейтинги по каждому критерию
        ratings = {}
        for criterion, values in criteria_data.items():
            # Сортируем по значениям (больше лучше)
            sorted_indices = np.argsort(values)[::-1]
            for rank, idx in enumerate(sorted_indices):
                if layout_data[idx]['name'] not in ratings:
                    ratings[layout_data[idx]['name']] = {}
                ratings[layout_data[idx]['name']][criterion] = rank + 1
        
        # Выводим таблицу сравнения
        print(f"\n{'Раскладка':<25} {'Удобные %':<12} {'Штраф':<10} {'Указ.нагр.':<12} {'Баланс':<10} {'Рейтинг':<25}")
        print("-" * 100)
        
        for layout in layout_data:
            name = layout['name']
            comfort_str = f"{layout['comfort_percent']:.1f}%"
            penalty_str = f"{layout['total_penalty']:.1f}"
            index_str = format_number(layout['index_load'])
            balance_str = f"{layout['balance_score']:.1f}%"
            
            # Средний рейтинг
            avg_rating = np.mean(list(ratings[name].values()))
            rating_str = f"#{int(avg_rating)} средний"
            
            print(f"{name:<25} {comfort_str:<12} {penalty_str:<10} {index_str:<12} {balance_str:<10} {rating_str:<25}")
        
        # Выводим рейтинги по критериям
        print("\n" + "="*100)
        print("РЕЙТИНГ ПО КРИТЕРИЯМ")
        print("="*100)
        
        for criterion in criteria_data.keys():
            print(f"\n{criterion}:")
            # Сортируем раскладки по этому критерию
            if 'Удобные' in criterion:
                sorted_layouts = sorted(layout_data, key=lambda x: x['comfort_percent'], reverse=True)
            elif 'Штраф' in criterion:
                sorted_layouts = sorted(layout_data, key=lambda x: x['total_penalty'])
            elif 'Указ' in criterion:
                sorted_layouts = sorted(layout_data, key=lambda x: x['index_load'])
            else:  # Баланс
                sorted_layouts = sorted(layout_data, key=lambda x: x['balance_score'], reverse=True)
            
            for i, layout in enumerate(sorted_layouts[:5]):  # топ-5
                if 'Удобные' in criterion:
                    value = layout['comfort_percent']
                    value_str = f"{value:.1f}%"
                elif 'Штраф' in criterion:
                    value = layout['total_penalty']
                    value_str = f"{value:.1f}"
                elif 'Указ' in criterion:
                    value = layout['index_load']
                    value_str = format_number(int(value))
                else:  # Баланс
                    value = layout['balance_score']
                    value_str = f"{value:.1f}%"
                
                print(f"  {i+1}. {layout['name']:<20} - {value_str}")
        
        # Выводим преимущества и недостатки В СРАВНЕНИИ С ДРУГИМИ
        print("\n" + "="*100)
        print("ПРЕИМУЩЕСТВА И НЕДОСТАТКИ (В СРАВНЕНИИ С ДРУГИМИ РАСКЛАДКАМИ)")
        print("="*100)
        
        # Вычисляем средние значения для сравнения
        avg_comfort = np.mean([d['comfort_percent'] for d in layout_data])
        avg_penalty = np.mean([d['total_penalty'] for d in layout_data])
        avg_balance = np.mean([d['balance_score'] for d in layout_data])
        avg_index_load = np.mean([d['index_load'] for d in layout_data])
        
        # Вычисляем стандартные отклонения
        std_comfort = np.std([d['comfort_percent'] for d in layout_data])
        std_penalty = np.std([d['total_penalty'] for d in layout_data])
        std_balance = np.std([d['balance_score'] for d in layout_data])
        std_index_load = np.std([d['index_load'] for d in layout_data])
        
        for layout in layout_data:
            print(f"\n{layout['name']}:")
            
            advantages = []
            disadvantages = []
            
            # Сравниваем с средним значением +- стандартное отклонение
            if layout['comfort_percent'] > avg_comfort + std_comfort/2:
                advantages.append(f"Высокий процент удобных комбинаций ({layout['comfort_percent']:.1f}% vs среднее {avg_comfort:.1f}%)")
            elif layout['comfort_percent'] < avg_comfort - std_comfort/2:
                disadvantages.append(f"Низкий процент удобных комбинаций ({layout['comfort_percent']:.1f}% vs среднее {avg_comfort:.1f}%)")
            
            if layout['total_penalty'] < avg_penalty - std_penalty/2:
                advantages.append(f"Низкий общий штраф ({layout['total_penalty']:.1f} vs среднее {avg_penalty:.1f})")
            elif layout['total_penalty'] > avg_penalty + std_penalty/2:
                disadvantages.append(f"Высокий общий штраф ({layout['total_penalty']:.1f} vs среднее {avg_penalty:.1f})")
            
            if layout['balance_score'] > avg_balance + std_balance/2:
                advantages.append(f"Отличный баланс между руками ({layout['balance_score']:.1f}% vs среднее {avg_balance:.1f}%)")
            elif layout['balance_score'] < avg_balance - std_balance/2:
                disadvantages.append(f"Плохой баланс между руками ({layout['balance_score']:.1f}% vs среднее {avg_balance:.1f}%)")
            
            if layout['index_load'] < avg_index_load - std_index_load/2:
                advantages.append(f"Низкая нагрузка на указательные пальцы ({format_number(layout['index_load'])} vs среднее {format_number(int(avg_index_load))})")
            elif layout['index_load'] > avg_index_load + std_index_load/2:
                disadvantages.append(f"Высокая нагрузка на указательные пальцы ({format_number(layout['index_load'])} vs среднее {format_number(int(avg_index_load))})")
            
            if advantages:
                print("  Преимущества:")
                for adv in advantages:
                    print(f"    ✓ {adv}")
            
            if disadvantages:
                print("  Недостатки:")
                for dis in disadvantages:
                    print(f"    ✗ {dis}")
            
            if not advantages and not disadvantages:
                print("  Средние показатели по всем критериям (близки к среднему по всем раскладкам)")
    
    def create_test_files(self):
        """Создает тестовые файлы если они отсутствуют"""
        # Многоязычный тестовый текст
        test_text = """Привет! Hello! Это тестовый текст для анализа клавиатурных раскладок.
        Программа сравнивает эргономику разных раскладок на основе комбинаций символов.
        
        Русский текст: ЙЦУКЕН, Вызов, Скоропись, фонетические раскладки.
        English text: QWERTY, Dvorak, Colemak, Workman layouts.
        
        Клавиатурная эргономика важна для быстрого и комфортного набора текста.
        Keyboard ergonomics is important for fast and comfortable typing.
        
        Тестируем различные комбинации: привет, hello, программа, algorithm,
        разработка, development, тестирование, testing, анализ, analysis.
        
        Специальные символы: ! @ # $ % ^ & * ( ) _ + { } [ ] | \\ : ; " ' < > ? , . /"""
        
        with open('test_text.txt', 'w', encoding='utf-8') as f:
            f.write(test_text)
        
        print("Тестовый файл создан")