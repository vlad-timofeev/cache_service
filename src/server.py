import asyncio
from asyncio import StreamReader, StreamWriter
from typing import Union

from config import PORT, HOST, MAX_MESSAGE_SIZE
from commands import CommandSet
from command_parser import parse_command
from command_executor import execute_command
from cache import Cache
from server_utils import send_message,\
    close_connection, process_set_command, MalformedMessageException,\
    build_error_message, SEPARATOR_BINARY, log_received_message


class Server:
    def __init__(self) -> None:
        self._cache = Cache()

    def run(self) -> None:
        asyncio.run(self._serve())

    async def _serve(self) -> None:
        server = await asyncio.start_server(
            self._accept_client,
            HOST,
            PORT,
            limit=(MAX_MESSAGE_SIZE + len(SEPARATOR_BINARY))
        )

        addr: str = server.sockets[0].getsockname()
        print(f'Serving on {addr}')

        async with server:
            await server.serve_forever()

    async def _accept_client(
            self, reader: StreamReader, writer: StreamWriter) -> None:
        addr: str = writer.get_extra_info('peername')
        print(f'Accepted client from {addr}')

        try:
            while True:
                data = await reader.readuntil(SEPARATOR_BINARY)

                log_received_message(data, writer)

                response: Union[str, bytes] = ''
                try:
                    message = data.decode()
                    if len(message.strip()) == 0:
                        # ignore empty messages
                        continue

                    command_or_error = parse_command(message)
                    if command_or_error.error:
                        response = command_or_error.error
                    else:
                        command = command_or_error.command
                        if isinstance(command, CommandSet):
                            await process_set_command(command, reader, writer)

                        response = execute_command(command, self._cache)
                except ValueError:
                    print(f'Failed to decode message from {addr}')
                    response = build_error_message(
                        'failed to decode message', fatal=False)
                await send_message(response, writer)

        except (MalformedMessageException, asyncio.LimitOverrunError):
            await send_message(
                build_error_message(
                    'unexpected message length or termination marker.',
                    fatal=True
                ),
                writer
            )

        except (asyncio.IncompleteReadError, ConnectionResetError):
            # client disconnected
            pass

        await close_connection(writer)
