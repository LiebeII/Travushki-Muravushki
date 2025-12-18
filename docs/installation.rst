Установка
==========

Требования
-----------
- Python 3.8 или выше
- Установленные библиотеки: matplotlib, numpy

Шаги установки
---------------

1. Клонируйте репозиторий:

   .. code-block:: bash

      git clone https://github.com/ваш-username/keyboard-layout-analyzer.git
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
   │   ├── text_processor.py       # Обработка текста
   │   ├── combo_analyzer.py       # Анализ комбинаций
   │   └── layout_evaluator.py     # Оценка раскладок
   ├── layouts/                     # Данные раскладок
   │   ├── layout_data.py          # Класс LayoutData
   │   └── layout_maps.py          # Карты раскладок
   ├── visualization/              # Визуализация
   │   ├── charts.py              # Графики и диаграммы
   │   └── stats_formatter.py     # Форматирование статистики
   └── utils/                      # Вспомогательные функции
       └── helpers.py