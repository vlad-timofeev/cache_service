import asyncio
from typing import Union


SEPARATOR = '\r\n'
SEPARATOR_BINARY = b'\r\n'
NOT_FOUND = 'NOT_FOUND'
SUCCESS = 'SUCCESS'


async def send_message(
        message: Union[str, bytes], writer: asyncio.StreamWriter) -> None:
    writer.write(
        (message.encode() if isinstance(message, str) else message) +
        SEPARATOR_BINARY)
    await writer.drain()


async def receive_message(
        reader: asyncio.StreamReader, size: int = None) -> bytes:
    if size is None:
        return await reader.readuntil(SEPARATOR_BINARY)
    return await reader.readexactly(size + len(SEPARATOR_BINARY))


def decode_and_trim(message: bytes) -> str:
    return message.decode().strip()
