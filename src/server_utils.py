from typing import Union
from asyncio import StreamReader, StreamWriter


from commands import CommandSet
from protocol import SEPARATOR, SEPARATOR_BINARY


class MalformedMessageException(Exception):
    pass


async def send_message(
        message: Union[str, bytes], writer: StreamWriter) -> None:
    data = message.encode() if isinstance(message, str) else message
    writer.write(data)
    await writer.drain()


def build_error_message(message: str, fatal: bool) -> str:
    fatal_substr = ' (fatal)' if fatal else ''
    return f'Protocol error{fatal_substr}: {message}{SEPARATOR}'


async def close_connection(writer: StreamWriter) -> None:
    writer.close()
    await writer.wait_closed()
    addr: str = writer.get_extra_info('peername')
    print(f'Closed the client socket {addr}')


async def process_set_command(
        command: CommandSet, reader: StreamReader, writer: StreamWriter
) -> None:
    size = int(command.get_arguments()[2])
    await send_message(
        f'Send {size} bytes, terminated with \\r\\n.{SEPARATOR}', writer)
    data = await reader.readexactly(size + len(SEPARATOR_BINARY))
    log_received_message(data, writer)
    _validate_message(data)
    data_without_separator = data[:len(data) - len(SEPARATOR_BINARY)]
    command.bytes_attachment = data_without_separator


def log_received_message(message: bytes, writer: StreamWriter) -> None:
    addr: str = writer.get_extra_info('peername')
    print(f'Received message from {addr}')
    print(message)


def _validate_message(message: bytes) -> None:
    if not message.endswith(SEPARATOR_BINARY):
        raise MalformedMessageException()
