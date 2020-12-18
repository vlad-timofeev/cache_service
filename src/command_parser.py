from typing import Optional, Type, List

from commands import Command, CommandSet, CommandGet, CommandDelete,\
    CommandId
from config import MAX_MESSAGE_SIZE
from protocol import SEPARATOR


class InvalidCommandArgument(Exception):
    pass


class CommandDefinition:
    def __init__(self, class_: Type[Command], args_number: int, usage: str):
        self.class_ = class_
        self.args_number = args_number
        self.usage = usage


class CommandOrError:
    def __init__(
            self,
            command: Optional[Command] = None,
            error: Optional[str] = None
    ):
        self.command = command
        self.error = error


_COMMAND_DEFINITIONS = {
    CommandId.SET.value: CommandDefinition(CommandSet, 3, '[key] [ttl] [size]'),
    CommandId.GET.value: CommandDefinition(CommandGet, 1, '[key]'),
    CommandId.DELETE.value: CommandDefinition(CommandDelete, 1, '[key]'),
}


# Tries to parse a command from the given message,
# returns either the parsed command or an error
def parse_command(message: str) -> CommandOrError:
    args = message.split()
    command_id = args[0]
    command_args = args[1:]

    if command_id not in _COMMAND_DEFINITIONS:
        supported: str = ','.join([command.value for command in CommandId])
        return CommandOrError(
            error=f'Unknown command: {command_id}. ' +
            f'Supported commands are: {supported}.{SEPARATOR}')

    definition = _COMMAND_DEFINITIONS[command_id]
    if len(command_args) != definition.args_number:
        return CommandOrError(
            error=f'Usage: {command_id} {definition.usage}{SEPARATOR}')

    if command_id == CommandId.SET.value:
        try:
            _validate_set_command_args(command_args)
        except InvalidCommandArgument as e:
            return CommandOrError(error=f'Bad argument: {str(e)}{SEPARATOR}')

    return CommandOrError(command=definition.class_(command_args))


def _validate_set_command_args(args: List[str]) -> None:
    _, ttl, size = args
    _parse_int(ttl, 'ttl', 0, None)
    _parse_int(size, 'size', 0, MAX_MESSAGE_SIZE)


def _parse_int(
        value: str,
        name: str,
        lower_bound: Optional[int],
        upper_bound: Optional[int]) -> None:
    try:
        number = int(value)
        if lower_bound is not None and number < lower_bound:
            raise InvalidCommandArgument(f'"{name}" must be >= {lower_bound}')
        if upper_bound is not None and number > upper_bound:
            raise InvalidCommandArgument(f'"{name}" must be <= {upper_bound}')

    except ValueError:
        raise InvalidCommandArgument(f'"{name}" must be integer')
