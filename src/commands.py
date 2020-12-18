from typing import List
from enum import Enum


class CommandId(Enum):
    SET = 'set'
    GET = 'get'
    DELETE = 'del'


class Command:
    def __init__(self, args: List[str]):
        self.args = args
        self.bytes_attachment: bytes = b''

    def get_id(self) -> str:
        raise NotImplementedError

    def get_arguments(self) -> List[str]:
        return self.args

    def get_bytes_attachment(self) -> bytes:
        return self.bytes_attachment

    def set_bytes_attachment(self, attachment: bytes) -> None:
        self.bytes_attachment = attachment


class CommandSet(Command):
    def get_id(self) -> str:
        return CommandId.SET.value


class CommandGet(Command):
    def get_id(self) -> str:
        return CommandId.GET.value


class CommandDelete(Command):
    def get_id(self) -> str:
        return CommandId.DELETE.value
