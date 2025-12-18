import re
from typing import Set, Dict
from collections import defaultdict


def file_to_words_set(filename: str, min_length: int = 2) -> Set[str]:
    '''
    Загружает содержимое файла и возвращает множество уникальных слов
    Игнорирует односимвольные слова
    '''
    words_set = set()
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            text = file.read()
        
        # Простая токенизация - разбиваем на слова по всем не-буквенным символам
        words = re.findall(r'[а-яёА-ЯЁa-zA-Z]+', text)
        
        for word in words:
            if len(word) >= min_length:
                words_set.add(word.lower())
    
    except FileNotFoundError:
        print(f"Файл {filename} не найден")
        return set()
    
    return words_set


def detect_language_ratio(text: str) -> Dict[str, float]:
    '''
    Определяет языковое соотношение текста
    Возвращает словарь {'russian': 0.75, 'english': 0.25}
    '''
    # Простые регулярные выражения для определения языка
    ru_pattern = re.compile(r'[а-яёА-ЯЁ]')
    en_pattern = re.compile(r'[a-zA-Z]')
    
    # Подсчитываем символы каждого языка
    ru_chars = len(ru_pattern.findall(text))
    en_chars = len(en_pattern.findall(text))
    total_chars = ru_chars + en_chars
    
    if total_chars == 0:
        return {'russian': 0, 'english': 0}
    
    return {
        'russian': ru_chars / total_chars,
        'english': en_chars / total_chars
    }