"""Extract saved cell display text without appending phonetic metadata.

Does not load workbooks, unhide cells, evaluate formulas or decide scope.
The caller must apply visibility/exclusion rules first.
"""
from xml.etree.ElementTree import Element


def display_text(element: Element | None) -> str:
    if element is None:
        return ''
    local = element.tag.rsplit('}', 1)[-1]
    if local in {'rPh', 'phoneticPr'}:
        return ''
    if local == 't':
        return element.text or ''
    return ''.join(display_text(child) for child in element)
