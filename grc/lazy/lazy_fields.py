from flask_babel import LazyString
from typing import Tuple, List, Any
from wtforms import RadioField, SelectMultipleField


class LazyRadioField(RadioField):
    def __init__(self, lazy_choices: List[Tuple[Any, LazyString]], choices=None, validators=None, **kwargs):
        super().__init__(validators=validators, choices=choices, **kwargs)
        self.lazy_choices = lazy_choices
        self.choices = choices if choices else self._stringify_lazy_choices()

    def _stringify_lazy_choices(self) -> List[Tuple[Any, str]]:
        return [(choice_id, str(choice_label)) for choice_id, choice_label in self.lazy_choices]


class LazyMultiSelectField(SelectMultipleField):
    def __init__(self, lazy_choices: List[Tuple[Any, LazyString]], choices=None, validators=None, **kwargs):
        super().__init__(validators=validators, choices=choices, **kwargs)
        self.lazy_choices = lazy_choices
        self.choices = choices if choices else self._stringify_lazy_choices()

    def _stringify_lazy_choices(self) -> List[Tuple[Any, str]]:
        return [(choice_id, str(choice_label)) for choice_id, choice_label in self.lazy_choices]
