from typing import Union

from cache import Cache
from commands import Command, CommandSet, CommandGet, CommandDelete

from protocol import SEPARATOR, SEPARATOR_BINARY

_NOT_EXECUTED = 'NOT_EXECUTED'
_SUCCESS = 'SUCCESS'
_FAILURE = 'COMMAND_FAILED'
_NOT_FOUND = 'NOT_FOUND'


# Executes the provided command on the cache
def execute_command(command: Command, cache: Cache) -> Union[str, bytes]:
    args = command.args
    result: Union[str, bytes] = _NOT_EXECUTED
    if isinstance(command, CommandSet):
        if cache.set_item(
            args[0],
            command.get_bytes_attachment(),
            int(args[1])
        ):
            result = _SUCCESS
        else:
            result = _FAILURE
    elif isinstance(command, CommandGet):
        item = cache.get_item(args[0])
        if item is None:
            result = _NOT_FOUND
        else:
            result = str(len(item)).encode() + SEPARATOR_BINARY + item
    elif isinstance(command, CommandDelete):
        if cache.delete_item(args[0]):
            result = _SUCCESS
        else:
            result = _FAILURE

    if isinstance(result, str):
        result += SEPARATOR
    else:
        result += SEPARATOR_BINARY
    return result
