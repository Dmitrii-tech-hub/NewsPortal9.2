from django import template
import re

register = template.Library()

@register.filter(name='censor')
def censor(value):
    if not isinstance(value, str):
        raise ValueError("Filter 'censor' can only be applied to strings.")
    # Список нецензурных слов
    bad_words = ['редиска']  # Добавьте сюда слова, которые нужно цензурировать
    for word in bad_words:
        value = re.sub(rf'\b{re.escape(word)}\b', '*' * len(word), value, flags=re.IGNORECASE)
    return value

