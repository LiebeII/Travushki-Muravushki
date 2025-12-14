import re
from typing import Set, Dict
from collections import defaultdict


def file_to_words_set(filename: str, min_length: int = 2) -> Set[str]:
    '''
    Получает название файла и возвращает множество уникальных слов
    Отбрасывает односимвольные слова
    '''
    words_set = set()
    letters = (
        'аАбБвВгГдДеЕёЁжЖзЗиИйЙкКлЛмМнНоОп'
        'ПрРсСтТуУфФхХцЦчЧшШщЩъЪыЫьЬэЭюЮяЯ'
        'aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ'
    )

    word_temp = ''

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                for char in line:
                    if char in letters:
                        word_temp += char
                    elif word_temp != '':
                        if len(word_temp) >= min_length:
                            words_set.add(word_temp.lower())
                        word_temp = ''
                
                # Добавление последнего слова, если оно есть
                if word_temp != '':
                    if len(word_temp) >= min_length:
                        words_set.add(word_temp.lower())
                    word_temp = ''
    
    except FileNotFoundError:
        print(f"Файл {filename} не найден")
        return set()
    
    return words_set


def detect_language_ratio(text: str) -> Dict[str, float]:
    '''
    Определяет процентное соотношение языков в тексте
    Возвращает словарь {'russian': 0.75, 'english': 0.25}
    '''
    # Регулярные выражения для определения языков
    ru_pattern = re.compile(r'[а-яА-ЯёЁ]')
    en_pattern = re.compile(r'[a-zA-Z]')
    
    # Считаем символы каждого языка
    ru_chars = len(ru_pattern.findall(text))
    en_chars = len(en_pattern.findall(text))
    total_chars = ru_chars + en_chars
    
    if total_chars == 0:
        return {'russian': 0, 'english': 0}
    
    return {
        'russian': ru_chars / total_chars,
        'english': en_chars / total_chars
    }