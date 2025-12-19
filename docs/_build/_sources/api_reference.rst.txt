API Reference
==============

Основные классы
---------------

LayoutEvaluator
~~~~~~~~~~~~~~~
Основной класс для оценки раскладок.

.. automodule:: analysis.layout_evaluator
   :members:
   :undoc-members:
   :show-inheritance:

**Основные методы:**

.. py:method:: LayoutEvaluator.load_custom_layout(file_path)
   
   Загружает пользовательскую раскладку из JSON файла.
   
   :param file_path: Путь к JSON файлу
   :type file_path: str
   :return: True если успешно, False если ошибка
   :rtype: bool

.. py:method:: LayoutEvaluator.analyze_combinations_all_layouts(file_path=None)
   
   Анализирует комбинации символов для всех раскладок.
   
   :param file_path: Путь к файлу с текстом (опционально)
   :type file_path: str
   :return: Статистика анализа
   :rtype: dict

.. py:method:: LayoutEvaluator.print_combinations_comparison()
   
   Выводит сравнение раскладок в консоль.
   
   :return: None

.. py:method:: LayoutEvaluator.visualize_results()
   
   Генерирует графики визуализации.
   
   :return: None

LayoutData
~~~~~~~~~~
Класс для хранения данных раскладки.

.. automodule:: layouts.layout_data
   :members:
   :undoc-members:
   :show-inheritance:

**Атрибуты:**

.. py:attribute:: LayoutData.name
   
   Название раскладки.
   :type: str

.. py:attribute:: LayoutData.language
   
   Язык раскладки ('russian' или 'english').
   :type: str

.. py:attribute:: LayoutData.layout
   
   Матрица раскладки (4xN).
   :type: list

TextProcessor
~~~~~~~~~~~~~
Класс для обработки текста.

.. automodule:: analysis.text_processor
   :members:
   :undoc-members:
   :show-inheritance:

**Методы:**

.. py:method:: TextProcessor.detect_language(text)
   
   Определяет язык текста.
   
   :param text: Текст для анализа
   :type text: str
   :return: 'russian', 'english' или 'mixed'
   :rtype: str

.. py:method:: TextProcessor.extract_words(text)
   
   Извлекает слова из текста.
   
   :param text: Текст для обработки
   :type text: str
   :return: Список слов
   :rtype: list

ComboAnalyzer
~~~~~~~~~~~~~
Класс для анализа комбинаций символов.

.. automodule:: analysis.combo_analyzer
   :members:
   :undoc-members:
   :show-inheritance:

**Методы:**

.. py:method:: ComboAnalyzer.analyze_word(word, layout_data)
   
   Анализирует комбинации символов в слове.
   
   :param word: Слово для анализа
   :type word: str
   :param layout_data: Данные раскладки
   :type layout_data: LayoutData
   :return: Статистика по комбинациям
   :rtype: dict

Visualization
-------------

Charts
~~~~~~
Класс для создания графиков.

.. automodule:: visualization.charts
   :members:
   :undoc-members:
   :show-inheritance:

**Методы:**

.. py:method:: Charts.plot_finger_load(layouts_stats, title="Нагрузка на пальцы")
   
   Создает график нагрузки на пальцы.
   
   :param layouts_stats: Статистика по раскладкам
   :type layouts_stats: dict
   :param title: Заголовок графика
   :type title: str
   :return: Объект matplotlib Figure
   :rtype: matplotlib.figure.Figure

.. py:method:: Charts.plot_total_penalty(layouts_stats, title="Общий штраф по раскладкам")
   
   Создает график общего штрафа.
   
   :param layouts_stats: Статистика по раскладкам
   :type layouts_stats: dict
   :param title: Заголовок графика
   :type title: str
   :return: Объект matplotlib Figure
   :rtype