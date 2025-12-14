import matplotlib.pyplot as plt
from analysis.layout_evaluator import LayoutEvaluator


def main():
    """Основная функция программы"""
    evaluator = LayoutEvaluator()
    
    while True:
        print("\n" + "="*60)
        print("ПРОДВИНУТЫЙ АНАЛИЗАТОР КЛАВИАТУРНЫХ РАСКЛАДОК")
        print("="*60)
        print("1. Показать все доступные раскладки")
        print("2. Загрузить кастомную раскладку из файла")
        print("3. Анализировать комбинации символов (все раскладки)")
        print("4. Анализировать конкретный текстовый файл")
        print("5. Показать результаты последнего анализа")
        print("6. Выход")
        
        choice = input("\nВыберите действие (1-6): ").strip()
        
        if choice == '1':
            evaluator.show_all_layouts()
            
        elif choice == '2':
            layout_file = input("Введите имя файла раскладки (JSON): ").strip()
            if layout_file:
                evaluator.load_custom_layout(layout_file)
            
        elif choice == '3':
            evaluator.analyze_combinations_all_layouts()
            
        elif choice == '4':
            text_file = input("Введите имя файла с текстом: ").strip()
            if not text_file:
                text_file = 'test_text.txt'
                
                # Создаем тестовый файл если его нет
                try:
                    with open(text_file, 'r', encoding='utf-8'):
                        pass
                except FileNotFoundError:
                    evaluator.create_test_files()
            
            evaluator.analyze_combinations_all_layouts(text_file)
            
        elif choice == '5':
            if evaluator.all_layouts_stats:
                print("\nРезультаты последнего анализа комбинаций:")
                evaluator.print_combinations_comparison(evaluator.all_layouts_stats)
            else:
                print("Анализ еще не проводился. Сначала выполните анализ комбинаций.")
            
        elif choice == '6':
            print("Выход из программы.")
            break
            
        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    # Устанавливаем русские шрифты для графиков
    try:
        plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False
    except:
        pass
    
    main()