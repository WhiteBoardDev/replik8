from dataclasses import dataclass

@dataclass(frozen=True)
class InvalidUserInputError:
    message: str