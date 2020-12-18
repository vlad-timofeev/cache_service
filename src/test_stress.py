import asyncio
import unittest
from unittest import IsolatedAsyncioTestCase
import random
import string

from config import PORT, HOST
from test_utils import send_message, receive_message, decode_and_trim,\
    SUCCESS


_NUMBER_OF_ITEMS_TO_INSERT = 1000
_VALUE_LENGTH = 1000


def random_string(length: int) -> str:
    return ''.join(random.choices(string.ascii_uppercase, k=length))


class StressTest(IsolatedAsyncioTestCase):

    """
    Inserts _NUMBER_OF_ITEMS_TO_INSERT random values and then deletes them all.
    Each item value is _VALUE_LENGTH chars long.
    """
    async def test_server(self) -> None:
        reader, writer = await asyncio.open_connection(HOST, PORT)

        index = 0
        insert = True

        print(f'Inserting {_NUMBER_OF_ITEMS_TO_INSERT} items...')

        while True:
            if index >= _NUMBER_OF_ITEMS_TO_INSERT:
                if insert:
                    # switch into deletion mode
                    index = 0
                    insert = False
                    print(f'Deleting {_NUMBER_OF_ITEMS_TO_INSERT} items...')
                else:
                    print('Done.')
                    break

            if insert:
                value = random_string(_VALUE_LENGTH)
                await send_message(f'set {index} 0 {len(value)}', writer)
                await receive_message(reader)
                await send_message(value, writer)
                response = await receive_message(reader)
                self.assertEqual(decode_and_trim(response), SUCCESS)
            else:
                await send_message(f'del {index}', writer)
                response = await receive_message(reader)
                self.assertEqual(decode_and_trim(response), SUCCESS)

            index += 1

        writer.close()
        await writer.wait_closed()


if __name__ == '__main__':
    unittest.main()
