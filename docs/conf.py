# Configuration file for the Sphinx documentation builder.
project = 'Анализатор клавиатурных раскладок'
copyright = '2024, Ваше имя или организация'
author = 'Ваше имя'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'ru'
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']