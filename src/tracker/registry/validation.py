from ast import In
import re

from tracker.InvalidUserInputError import InvalidUserInputError
from typing import Callable, Iterable


class FieldValidatorBuilder:
    def __init__(self, field_name: str) -> None:
        self.validation_chain: list[Callable[[str], None | InvalidUserInputError]] = []
        self.field_name = field_name

    def _length(self, min: int, max: int, value: str) -> None | InvalidUserInputError:
        if len(value) < min or len(value) > max:
            return InvalidUserInputError(
                f"{self.field_name} must be between {min} and {max} in length"
            )

    def length(self, min: int, max: int) -> FieldValidatorBuilder:
        def _length(value: str) -> None | InvalidUserInputError:
            if len(value) < min or len(value) > max:
                return InvalidUserInputError(
                    f"{self.field_name} must be between {min} and {max} in length"
                )

        self.validation_chain.append(_length)
        return self

    def matches_regex(self, pattern: str, error_msg: str) -> FieldValidatorBuilder:
        def _matches(value: str):
            if not re.match(pattern, value):
                return InvalidUserInputError(error_msg)

        self.validation_chain.append(_matches)
        return self

    def build(self) -> Callable[[str], None | InvalidUserInputError]:

        def validator(value: str) -> None | InvalidUserInputError:
            for validator in self.validation_chain:
                possible_invalid = validator(value)
                if possible_invalid is not None:
                    return possible_invalid

        return validator


def validate_chain(outcomes: Iterable[None | InvalidUserInputError]) -> None | InvalidUserInputError:
    possible_error = [x for x in outcomes if isinstance(x, InvalidUserInputError)]
    if len(possible_error) > 0:
        return possible_error[0]
    return None