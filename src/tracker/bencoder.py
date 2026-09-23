from dataclasses import dataclass
from re import I
from typing import Self, Iterator
from io import StringIO

class Bencoder():

    def __init__(self):
        self.message = bytearray()

    def withString(self, item: bytes) -> Self:
        self.message.extend(f"{len(item)}:".encode())
        self.message.extend(item)
        return self
    
    def withInt(self, item: int) -> Self:
        base10 = str(item)
        self.message.extend(f"i{base10}e".encode())
        return self

    def withDict(self, items: dict[str, str | int | dict | list]) -> Self:
        self.message.extend('d'.encode())
        for key in sorted(items.keys()):
            self.withString(key.encode())
            val = items.get(key)
            if isinstance(val, bytes):
                self.withString(val)
            elif isinstance(val, int):
                self.withInt(val)
            elif isinstance(val, dict):
                self.withDict(val)
            elif isinstance(val, list):
                self.withList(val)
            else:
                raise Exception('unable to encode value of dict due to unsupported type')
        self.message.extend("e".encode())
        return self
    
    def withList(self, items: list[str | int | dict]) -> Self:
        self.message.extend("l".encode())
        for item in items:
            if isinstance(item, bytes):
                self.withString(item)
            elif isinstance(item, int):
                self.withInt(item)
            elif isinstance(item, dict):
                self.withDict(item)
            else:
                raise Exception('unable to encode value of list due to unsupported type')
        self.message.extend("e".encode())
        return self


    def asBytes(self) -> bytes:
        return bytes(self.message)

def _parse_int(message: Iterator[int]) -> int:
    int_buffer = StringIO()
    for byte in message:
        char = chr(byte)
        if char.isdigit():
            int_buffer.write(char)
        elif char == 'e':
            break
        else:
            raise Exception('malformed bencoded int')
    return int(int_buffer.getvalue())

def _parse_str(prev_char: str, message: Iterator[int]) -> bytes:
    assert len(prev_char) == 1
    int_buffer = StringIO()
    int_buffer.write(prev_char)
    for byte in message:
        char = chr(byte)
        if char.isdigit():
            int_buffer.write(char)
        elif char == ':':
            break
        else:
            raise Exception('malformed bencoded string')
    str_len = int(int_buffer.getvalue())
    val_buff = bytearray(str_len)
    chars_written = 0
    for char in message:
        val_buff[chars_written] = char
        chars_written += 1
        if chars_written >= str_len:
            break
    return bytes(val_buff)

def _parse_list(message: Iterator[int]) -> list:
    result = list()
    for current_byte in message:
        current_char = chr(current_byte)
        if current_char.isdigit():
            result.append(_parse_str(current_char, message))
        elif current_char == 'i':
            result.append(_parse_int(message))
        elif current_char == 'l':
            result.append(_parse_list(message))
        elif current_char == 'd':
            result.append(_parse_dict(message))
        elif current_char == 'e':
            return result
        else:
            raise Exception("unable to parse bencoded list")
    raise Exception("unable to parse bencoded list")

def _parse_dict(message: Iterator[int]) -> dict:
    result = dict()
    current_dict_key: int | str | None = None
    for current_byte in message:
        current_char = chr(current_byte)
        if current_char.isdigit():
            str_val = _parse_str(current_char, message) 
            if current_dict_key is None:
                current_dict_key = str_val.decode('utf-8')
            else:
                result[current_dict_key] = str_val
                current_dict_key = None
        elif current_char == 'i':
            val = _parse_int(message)
            if current_dict_key is None:
                current_dict_key = val
            else:
                result[current_dict_key] = val
                current_dict_key = None
        elif current_char == 'l':
            assert current_dict_key is not None
            result[current_dict_key] = _parse_list(message)
            current_dict_key = None
        elif current_char == 'd':
            assert current_dict_key is not None
            result[current_dict_key] = _parse_dict(message)
            current_dict_key = None
        elif current_char == 'e':
            return result
        else:
            raise Exception('unable to parse dict from message')
    raise Exception('unable to parse dict from message')

def parse_bencoded_message(input: bytes) -> dict | list | int | bytes:
    message_iter = iter(input)
    for byte in message_iter:
        char = chr(byte)
        if char == 'd': 
            return _parse_dict(message_iter)
        elif char == 'i':
            return _parse_int(message_iter)
        elif char.isdigit():
            return _parse_str(char, message_iter)
        elif char == 'l':
            return _parse_list(message_iter)
        else:
            raise Exception("unable to parse bencoded message")
    raise Exception("unable to parse bencoded message")