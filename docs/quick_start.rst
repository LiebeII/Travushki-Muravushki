Быстрый старт
==============

Требования
----------
- **Python 3.8** или выше
- **Библиотеки:** matplotlib, numpy

Установка
---------

1. Клонируйте репозиторий:

   .. code-block:: bash

      git clone https://github.com/your-username/keyboard-layout-analyzer.git
      cd keyboard-layout-analyzer

2. Установите зависимости:

   .. code-block:: bash

      pip install matplotlib numpy

3. Запустите программу:

   .. code-block:: bash

      python main.py

Структура проекта
-----------------
::

   keyboard-analyzer/
   ├── main.py                      # Главный файл программы
   ├── analysis/                    # Модули анализа
   │   ├── text_processor.py       # Обработка текста, определение языка
   │   ├── combo_analyzer.py       # Анализ комбинаций символов
   │   ├── layout_evaluator.py     # Основной класс оценки раскладок
   │   └── finger_penalty_calculator.py # Расчет штрафов по расстоянию
   ├── layouts/                     # Данные раскладок
   │   ├── layout_data.py          # Класс LayoutData с картами раскладок
   │   └── layout_maps.py          # Дополнительные карты раскладок
   ├── visualization/              # Визуализация результатов
   │   ├── charts.py              # Графики и диаграммы Matplotlib
   │   └── stats_formatter.py     # Форматирование чисел (K, M)
   ├── ready_made_layouts/        # Пользовательские раскладки (JSON)
   │   ├── altk.json             # Пример раскладки с Alt-слоем
   │   └── ...                   # Другие пользовательские раскладки
   └── README.md                  # Документация

Первые шаги
-----------
1. При первом запуске вы увидите главное меню
2. Выберите "1. Показать все раскладки" для просмотра доступных вариантов
3. Выберите "3. Анализ комбинаций символов для всех раскладок" для тестового анализа
4. Просмотрите результаты в консоли и сгенерированные графики