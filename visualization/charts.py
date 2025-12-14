import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Any
from .stats_formatter import format_number


def visualize_finger_statistics(layouts_stats: Dict[str, Dict[str, Any]], text_file: str = None):
    '''
    Визуализация статистики по пальцам
    '''
    if not layouts_stats:
        print("Нет данных для визуализации")
        return
    
    layouts = list(layouts_stats.keys())
    
    # 1. ПЕРВАЯ ФИГУРА: Нагрузка на пальцы и штрафы
    fig1 = plt.figure(figsize=(16, 8))
    
    if text_file:
        fig1.suptitle(f'Статистика для файла: {text_file}', fontsize=16, fontweight='bold')
    
    # 1.1. Нагрузка на пальцы
    ax1 = plt.subplot(1, 2, 1)
    finger_names = ['left_pinky', 'left_ring', 'left_middle', 'left_index',
                   'right_index', 'right_middle', 'right_ring', 'right_pinky']
    
    finger_loads = {finger: [] for finger in finger_names}
    
    for layout in layouts:
        stats = layouts_stats[layout]
        for finger in finger_names:
            finger_loads[finger].append(stats['finger_load'].get(finger, 0))
    
    x = np.arange(len(layouts))
    width = 0.1
    colors = plt.cm.tab10(np.linspace(0, 1, len(finger_names)))
    
    # Находим максимальное значение для нормализации текста
    max_values = []
    for i in range(len(layouts)):
        max_val = max(finger_loads[finger][i] for finger in finger_names)
        max_values.append(max_val)
    
    for i, finger in enumerate(finger_names):
        bars = ax1.bar(x + i*width - (len(finger_names)-1)*width/2, finger_loads[finger], width, 
                      color=colors[i], label=finger.replace('_', ' ').title())
        
        # Добавляем значения на столбцы
        for bar_idx, bar in enumerate(bars):
            val = finger_loads[finger][bar_idx]
            if val > 0:
                ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max_values[bar_idx]*0.01,
                        format_number(val), ha='center', va='bottom', fontsize=7, rotation=90)
    
    ax1.set_xlabel('Раскладки', fontsize=12)
    ax1.set_ylabel('Количество кликов', fontsize=12)
    ax1.set_title('Нагрузка на пальцы', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(layouts, rotation=45, ha='right')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # 1.2. Общий штраф на пальцы
    ax2 = plt.subplot(1, 2, 2)
    total_penalties = [layouts_stats[layout]['total_penalty'] for layout in layouts]
    
    bars = ax2.bar(range(len(layouts)), total_penalties, color=plt.cm.Set3(np.linspace(0, 1, len(layouts))))
    ax2.set_xlabel('Раскладки', fontsize=12)
    ax2.set_ylabel('Общий штраф', fontsize=12)
    ax2.set_title('Общий штраф на пальцы', fontsize=14, fontweight='bold')
    ax2.set_xticks(range(len(layouts)))
    ax2.set_xticklabels(layouts, rotation=45, ha='right')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Добавляем значения на столбцы
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + max(total_penalties)*0.01,
                f'{height:.1f}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.show()
    
    # 2. ВТОРАЯ ФИГУРА: Распределение штрафов между руками
    num_layouts = len(layouts)
    cols = min(4, num_layouts)
    rows = (num_layouts + cols - 1) // cols
    
    fig2 = plt.figure(figsize=(cols * 4, rows * 3.5))
    
    if text_file:
        fig2.suptitle(f'Распределение штрафов между руками: {text_file}', 
                     fontsize=16, fontweight='bold', y=0.98)
    
    for idx, layout in enumerate(layouts):
        row = idx // cols
        col = idx % cols
        ax = fig2.add_subplot(rows, cols, idx + 1)
        
        stats = layouts_stats[layout]['hand_penalties']
        left_percent = stats.get('left_percent', 0)
        right_percent = stats.get('right_percent', 0)
        
        if left_percent + right_percent > 0:
            sizes = [left_percent, right_percent]
            labels = ['Левая', 'Правая']
            colors_pie = ['lightblue', 'lightcoral']
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors_pie,
                                              autopct='%1.1f%%', startangle=90,
                                              textprops={'fontsize': 10})
            
            ax.set_title(f'{layout}\nЛевая: {left_percent:.1f}% | Правая: {right_percent:.1f}%', 
                        fontsize=12, fontweight='bold', pad=20)
            ax.axis('equal')
        else:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', fontsize=12)
            ax.set_title(f'{layout}', fontsize=12, fontweight='bold')
            ax.axis('off')
    
    plt.tight_layout()
    plt.show()
    
    # 3. ТРЕТЬЯ ФИГУРА: Одноручные комбинации
    cols_combos = min(4, num_layouts)
    rows_combos = (num_layouts + cols_combos - 1) // cols_combos
    
    fig3 = plt.figure(figsize=(cols_combos * 4, rows_combos * 3.5))
    
    if text_file:
        fig3.suptitle(f'Одноручные комбинации: {text_file}', 
                     fontsize=16, fontweight='bold', y=0.98)
    
    for idx, layout in enumerate(layouts):
        row = idx // cols_combos
        col = idx % cols_combos
        ax = fig3.add_subplot(rows_combos, cols_combos, idx + 1)
        
        stats = layouts_stats[layout]['two_char_analysis']
        total = stats['one_hand_total']
        comfortable = stats['comfortable_one_hand']
        uncomfortable = total - comfortable
        
        if total > 0:
            sizes = [comfortable, uncomfortable]
            labels = ['Удобные', 'Неудобные']
            colors_pie = ['green', 'lightcoral']
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors_pie,
                                              autopct='%1.1f%%', startangle=90,
                                              textprops={'fontsize': 10})
            
            ax.set_title(f'{layout}\nВсего: {format_number(total)}', 
                        fontsize=12, fontweight='bold', pad=20)
            ax.axis('equal')
            
            # Добавляем абсолютные значения в центр
            center_text = f'Удобные:\n{format_number(comfortable)}\nНеудобные:\n{format_number(uncomfortable)}'
            ax.text(0, 0, center_text, ha='center', va='center', fontsize=9, fontweight='bold')
        else:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', fontsize=12)
            ax.set_title(f'{layout}', fontsize=12, fontweight='bold')
            ax.axis('off')
    
    plt.tight_layout()
    plt.show()


def visualize_combo_distribution(layouts_stats: Dict[str, Dict[str, Any]], text_file: str = None):
    '''
    Визуализация распределения комбинаций
    '''
    if not layouts_stats:
        print("Нет данных для визуализации")
        return
    
    layouts = list(layouts_stats.keys())
    
    # 1. ПЕРВАЯ ФИГУРА: Распределение по длинам комбинаций
    fig1 = plt.figure(figsize=(14, 8))
    
    if text_file:
        fig1.suptitle(f'Распределение комбинаций по длинам: {text_file}', 
                     fontsize=16, fontweight='bold')
    
    ax1 = fig1.add_subplot(1, 1, 1)
    
    categories = ['Одноручные', 'Удобные', 'Частично удобные']
    colors = ['lightblue', 'lightgreen', 'lightcoral']
    
    for length in [2, 3, 4]:
        one_hand_values = []
        comfortable_values = []
        partially_values = []
        
        for layout in layouts:
            stats = layouts_stats[layout]
            one_hand_values.append(stats['one_hand'].get(length, 0))
            comfortable_values.append(stats['comfort_count'].get(length, 0))
            partially_values.append(stats['partial_count'].get(length, 0))
        
        x = np.arange(len(layouts))
        width = 0.25
        
        if length == 2:
            offset = -width
            label_suffix = ' (2 символа)'
        elif length == 3:
            offset = 0
            label_suffix = ' (3 символа)'
        else:
            offset = width
            label_suffix = ' (4 символа)'
        
        bars1 = ax1.bar(x + offset, one_hand_values, width, label=f'Одноручные{label_suffix}', 
                       color=colors[0], alpha=0.7)
        bars2 = ax1.bar(x + offset, comfortable_values, width, label=f'Удобные{label_suffix}', 
                       color=colors[1], alpha=0.7, bottom=one_hand_values)
        bars3 = ax1.bar(x + offset, partially_values, width, label=f'Частично{label_suffix}', 
                       color=colors[2], alpha=0.7, bottom=np.array(one_hand_values) + np.array(comfortable_values))
        
        # Добавляем значения на столбцы
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax1.text(bar.get_x() + bar.get_width()/2., bar.get_y() + height/2,
                            format_number(height), ha='center', va='center', fontsize=7)
    
    ax1.set_xlabel('Раскладки', fontsize=12)
    ax1.set_ylabel('Количество комбинаций', fontsize=12)
    ax1.set_title('Распределение комбинаций по длинам', fontsize=14, fontweight='bold')
    ax1.set_xticks(np.arange(len(layouts)))
    ax1.set_xticklabels(layouts, rotation=45, ha='right')
    
    # Создаем легенду только для уникальных меток
    handles, labels = ax1.get_legend_handles_labels()
    unique_labels = []
    unique_handles = []
    for handle, label in zip(handles, labels):
        if label not in unique_labels:
            unique_labels.append(label)
            unique_handles.append(handle)
    
    ax1.legend(unique_handles, unique_labels, bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    ax1.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.show()
    
    # 2. ВТОРАЯ ФИГУРА: Процентное соотношение комбинаций
    num_layouts = len(layouts)
    cols = min(4, num_layouts)
    rows = (num_layouts + cols - 1) // cols
    
    fig2 = plt.figure(figsize=(cols * 4, rows * 3.5))
    
    if text_file:
        fig2.suptitle(f'Процентное соотношение комбинаций: {text_file}', 
                     fontsize=16, fontweight='bold', y=0.98)
    
    for idx, layout in enumerate(layouts):
        row = idx // cols
        col = idx % cols
        ax = fig2.add_subplot(rows, cols, idx + 1)
        
        stats = layouts_stats[layout]
        total_one_hand = stats['total_one_hand']
        total_comfort = stats['total_comfort']
        total_partial = stats['total_partial']
        
        if total_one_hand > 0:
            comfortable_percent = total_comfort / total_one_hand * 100
            partially_percent = total_partial / total_one_hand * 100
            uncomfortable_percent = 100 - comfortable_percent - partially_percent
            
            sizes = [comfortable_percent, partially_percent, uncomfortable_percent]
            labels = ['Удобные', 'Частично', 'Неудобные']
            colors_pie = ['green', 'yellowgreen', 'lightcoral']
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors_pie,
                                             autopct='%1.1f%%', startangle=90, pctdistance=0.85,
                                             textprops={'fontsize': 9})
            
            ax.set_title(f'{layout}\nВсего: {format_number(total_one_hand)}', 
                        fontsize=12, fontweight='bold', pad=20)
            ax.axis('equal')
        else:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', fontsize=12)
            ax.set_title(f'{layout}', fontsize=12, fontweight='bold')
            ax.axis('off')
    
    plt.tight_layout()
    plt.show()