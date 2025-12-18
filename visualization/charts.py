import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any
import matplotlib
from visualization.stats_formatter import format_number

# Устанавливаем шрифт Nerd Font
matplotlib.rcParams['font.family'] = 'DejaVu Sans Mono'
matplotlib.rcParams['axes.unicode_minus'] = False


def visualize_finger_statistics(layouts_stats: Dict[str, Any], source_file: str):
    """Визуализация статистики нагрузки на пальцы"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle(f'Статистика нагрузки на пальцы\n(Источник: {source_file})', fontsize=16, fontweight='bold')
    
    layout_names = list(layouts_stats.keys())
    
    # 1. Нагрузка на пальцы (русские названия) - БЕЗ БОЛЬШИХ ПАЛЬЦЕВ
    ax1 = axes[0, 0]
    
    # Русские названия пальцев (без больших пальцев)
    finger_names_ru = {
        'left_pinky': 'Лев. мизинец',
        'left_ring': 'Лев. безымянный',
        'left_middle': 'Лев. средний',
        'left_index': 'Лев. указательный',
        'right_index': 'Прав. указательный',
        'right_middle': 'Прав. средний',
        'right_ring': 'Прав. безымянный',
        'right_pinky': 'Прав. мизинец'
    }
    
    # Порядок пальцев (без больших пальцев)
    finger_order = ['left_pinky', 'left_ring', 'left_middle', 'left_index',
                    'right_index', 'right_middle', 'right_ring', 'right_pinky']
    
    x = np.arange(len(finger_order))
    width = 0.8 / len(layout_names)
    
    for i, layout_name in enumerate(layout_names):
        stats = layouts_stats[layout_name]
        finger_load = stats['finger_load']
        
        values = [finger_load.get(finger, 0) for finger in finger_order]
        
        # Преобразуем значения для отображения
        display_values = [v / 1000 if v > 1000 else v for v in values]
        
        ax1.bar(x + i * width - width * (len(layout_names) - 1) / 2, 
                display_values, width, label=layout_name)
    
    ax1.set_xlabel('Пальцы')
    ax1.set_ylabel('Нагрузка (тыс. нажатий)')
    ax1.set_title('Нагрузка на пальцы по раскладкам (без больших пальцев)')
    ax1.set_xticks(x)
    ax1.set_xticklabels([finger_names_ru.get(f, f) for f in finger_order], rotation=45)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Штраф на пальцы по раскладкам
    ax2 = axes[0, 1]
    
    # Используем 'finger_penalty' вместо 'dynamic_penalty'
    penalties = [layouts_stats[name]['finger_penalty'] for name in layout_names]
    
    # Сортируем для лучшего отображения
    sorted_indices = np.argsort(penalties)
    sorted_names = [layout_names[i] for i in sorted_indices]
    sorted_penalties = [penalties[i] for i in sorted_indices]
    
    colors = ['#2E86AB' if i == 0 else '#A23B72' if i == len(sorted_penalties)-1 else '#F18F01' 
              for i in range(len(sorted_penalties))]
    
    bars = ax2.bar(range(len(sorted_names)), sorted_penalties, color=colors)
    ax2.set_xlabel('Раскладка')
    ax2.set_ylabel('Штраф на пальцы')
    ax2.set_title('Штраф на пальцы (расстояние от домашнего ряда)\n(меньше = лучше)')
    ax2.set_xticks(range(len(sorted_names)))
    ax2.set_xticklabels(sorted_names, rotation=45)
    ax2.grid(True, alpha=0.3)
    
    # Добавляем значения на столбцы
    for bar, penalty in zip(bars, sorted_penalties):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + max(sorted_penalties)*0.01,
                f'{penalty:.0f}', ha='center', va='bottom')
    
    # 3. Баланс между руками
    ax3 = axes[1, 0]
    
    left_percents = [layouts_stats[name]['hand_balance']['left_percent'] for name in layout_names]
    right_percents = [layouts_stats[name]['hand_balance']['right_percent'] for name in layout_names]
    
    x = np.arange(len(layout_names))
    width = 0.35
    
    bars1 = ax3.bar(x - width/2, left_percents, width, label='Левая рука', color='#2E86AB')
    bars2 = ax3.bar(x + width/2, right_percents, width, label='Правая рука', color='#A23B72')
    
    # Добавляем линию идеального баланса (50%)
    ax3.axhline(y=50, color='green', linestyle='--', alpha=0.5, label='Идеальный баланс')
    
    # Закрашиваем область хорошего баланса (45-55%)
    ax3.axhspan(45, 55, alpha=0.1, color='green')
    
    ax3.set_xlabel('Раскладка')
    ax3.set_ylabel('Процент использования (%)')
    ax3.set_title('Баланс между руками')
    ax3.set_xticks(x)
    ax3.set_xticklabels(layout_names, rotation=45)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Добавляем маркер для хорошего баланса
    for i, (left, right) in enumerate(zip(left_percents, right_percents)):
        if 45 <= left <= 55 and 45 <= right <= 55:
            ax3.text(i, max(left, right) + 2, '✓', ha='center', va='bottom', fontweight='bold', color='green')
    
    # 4. Сравнение удобных/неудобных комбинаций
    ax4 = axes[1, 1]
    
    comfort_counts = [layouts_stats[name]['total_comfort'] for name in layout_names]
    partial_counts = [layouts_stats[name]['total_partial'] for name in layout_names]
    uncomfortable_counts = [layouts_stats[name]['total_uncomfortable'] for name in layout_names]
    
    x = np.arange(len(layout_names))
    width = 0.25
    
    bars1 = ax4.bar(x - width, comfort_counts, width, label='Удобные', color='#2E86AB')
    bars2 = ax4.bar(x, partial_counts, width, label='Частично удобные', color='#F18F01')
    bars3 = ax4.bar(x + width, uncomfortable_counts, width, label='Неудобные', color='#A23B72')
    
    ax4.set_xlabel('Раскладка')
    ax4.set_ylabel('Количество комбинаций')
    ax4.set_title('Распределение комбинаций по удобству')
    ax4.set_xticks(x)
    ax4.set_xticklabels(layout_names, rotation=45)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def visualize_combo_distribution(layouts_stats: Dict[str, Any], source_file: str):
    """Визуализация распределения комбинаций"""
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle(f'Распределение комбинаций по раскладкам\n(Источник: {source_file})', fontsize=16, fontweight='bold')
    
    layout_names = list(layouts_stats.keys())
    
    # 1. Процентное соотношение комбинаций
    ax1 = axes[0]
    
    # Собираем данные
    comfort_percents = []
    partial_percents = []
    uncomfortable_percents = []
    
    for layout_name in layout_names:
        stats = layouts_stats[layout_name]
        total = stats['total_comfort'] + stats['total_partial'] + stats['total_uncomfortable']
        
        if total > 0:
            comfort_percents.append(stats['total_comfort'] / total * 100)
            partial_percents.append(stats['total_partial'] / total * 100)
            uncomfortable_percents.append(stats['total_uncomfortable'] / total * 100)
        else:
            comfort_percents.append(0)
            partial_percents.append(0)
            uncomfortable_percents.append(0)
    
    x = np.arange(len(layout_names))
    width = 0.8
    
    # Создаем stacked bar chart
    bars1 = ax1.bar(x, comfort_percents, width, label='Удобные', color='#2E86AB')
    bars2 = ax1.bar(x, partial_percents, width, bottom=comfort_percents, label='Частично удобные', color='#F18F01')
    bars3 = ax1.bar(x, uncomfortable_percents, width, 
                    bottom=[c+p for c,p in zip(comfort_percents, partial_percents)], 
                    label='Неудобные', color='#A23B72')
    
    ax1.set_xlabel('Раскладка')
    ax1.set_ylabel('Процент (%)')
    ax1.set_title('Процентное соотношение комбинаций по удобству')
    ax1.set_xticks(x)
    ax1.set_xticklabels(layout_names, rotation=45)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # 2. Сравнение всех раскладок (удобные, частично удобные, неудобные) - вертикальная гистограмма
    ax2 = axes[1]
    
    # Группируем данные для сравнения
    categories = ['Удобные', 'Частично удобные', 'Неудобные']
    category_data = {
        'Удобные': comfort_percents,
        'Частично удобные': partial_percents,
        'Неудобные': uncomfortable_percents
    }
    
    x = np.arange(len(layout_names))
    width = 0.25
    offsets = [-width, 0, width]
    
    colors = ['#2E86AB', '#F18F01', '#A23B72']
    
    for i, (category, color) in enumerate(zip(categories, colors)):
        values = category_data[category]
        bars = ax2.bar(x + offsets[i], values, width, label=category, color=color, alpha=0.8)
        
        # Добавляем значения на столбцы
        for bar, value in zip(bars, values):
            height = bar.get_height()
            if height > 5:  # Добавляем текст только для достаточно высоких столбцов
                ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{value:.1f}%', ha='center', va='bottom', fontsize=9)
    
    ax2.set_xlabel('Раскладка')
    ax2.set_ylabel('Процент (%)')
    ax2.set_title('Сравнение раскладок по типам комбинаций')
    ax2.set_xticks(x)
    ax2.set_xticklabels(layout_names, rotation=45)
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Добавляем общую линию для 100%
    ax2.axhline(y=100, color='gray', linestyle=':', alpha=0.5)
    
    plt.tight_layout()
    plt.show()