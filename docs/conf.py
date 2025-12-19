project = 'Keyboard Layout Analyzer v2.0'
copyright = '2024, Your Name or Organization'
author = 'Your Name'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.autosummary',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'ru'
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Добавляем поддержку emoji
html_show_sourcelink = False
html_theme_options = {
    'display_version': True,
    'style_external_links': True,
}