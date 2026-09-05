from re import I
from typing import Self
from io import StringIO

class Bencoder():

    def __init__(self):
        self.message = StringIO()

    def withString(self, item: str) -> Self:
        self.message.write(f"{len(item)}:{item}")
        return self
    
    def withInt(self, item: int) -> Self:
        base10 = str(item)
        self.message.write(f"i{base10}e")
        return self

    def withDict(self, items: dict[str, str | int | dict]) -> Self:
        self.message.write('d')
        for key in sorted(items.keys()):
            self.withString(key)
            val = items.get(key)
            if isinstance(val, str):
                self.withString(val)
            if isinstance(val, int):
                self.withInt(val)
            if isinstance(val, dict):
                self.withDict(val)
            if isinstance(val, list):
                self.withList(val)
        self.message.write("e")
        return self
    
    def withList(self, items: list[str | int | dict]) -> Self:
        self.message.write("l")
        for item in items:
            if isinstance(item, str):
                self.withString(item)
            if isinstance(item, int):
                self.withInt(item)
            if isinstance(item, dict):
                self.withDict(item)
        self.message.write("e")
        return self


    def asBytes(self) -> bytes:
        return self.message.getvalue().encode('utf-8')
