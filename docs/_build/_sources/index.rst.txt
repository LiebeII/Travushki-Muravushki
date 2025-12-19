Документация Keyboard Layout Analyzer v2.0
============================================

.. toctree::
   :maxdepth: 3
   :caption: Содержание:

   overview
   quick_start
   layouts
   evaluation_criteria
   usage
   json_format
   visualization
   api_reference
   development

Обзор
-----
**Keyboard Layout Analyzer v2.0** — это продвинутая программа для комплексного анализа и сравнения клавиатурных раскладок с точки зрения эргономики, удобства набора и распределения нагрузки на пальцы.

Основные нововведения в версии 2.0:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
✅ **Многоязычный анализ:** Автоматическое определение языка текста  
✅ **Поддержка нескольких слоев:** Учет Alt-слоя с выбором оптимального варианта  
✅ **Расширенная система рейтинга:** 4 критерия оценки с весами  
✅ **Улучшенная визуализация:** Интерактивные графики Matplotlib  
✅ **Гибкая архитектура:** Легкое добавление новых раскладок и критериев  

Быстрый старт
-------------
.. code-block:: bash

   git clone https://github.com/your-username/keyboard-layout-analyzer.git
   cd keyboard-layout-analyzer
   pip install matplotlib numpy
   python main.py

Иконки статуса
~~~~~~~~~~~~~~
.. image:: https://img.shields.io/badge/Python-3.8+-blue.svg
   :target: https://python.org
   :alt: Python 3.8+

.. image:: https://img.shields.io/badge/Version-2.0-green.svg
   :target: #
   :alt: Version 2.0