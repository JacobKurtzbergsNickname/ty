"""Services Module for FastHTML app"""

from .affirmation import (
    create_affirmation,
    get_affirmation,
    list_affirmations,
)

from .good_things import (
    create_good_thing,
    get_good_thing,
    list_good_things,
)

from .gratitude import (
    create_gratitude_item,
    get_gratitude_item,
    list_gratitude_items,
)

from .positive_quote import (
    create_positive_quote,
    get_positive_quote,
    list_positive_quotes,
)

__all__ = [
    "create_affirmation",
    "get_affirmation",
    "list_affirmations",
    "create_good_thing",
    "get_good_thing",
    "list_good_things",
    "create_gratitude_item",
    "get_gratitude_item",
    "list_gratitude_items",
    "create_positive_quote",
    "get_positive_quote",
    "list_positive_quotes",
]
