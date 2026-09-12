"""Template package initialization."""
from . import layout

_LONG_READING = ("/reading/articles/", "Long Reading")
if _LONG_READING not in layout.NAV_ITEMS:
    try:
        reading_index = next(i for i, item in enumerate(layout.NAV_ITEMS) if item[0] == "/reading/")
    except StopIteration:
        layout.NAV_ITEMS.append(_LONG_READING)
    else:
        layout.NAV_ITEMS.insert(reading_index + 1, _LONG_READING)
