import asyncio
import unittest
from unittest import IsolatedAsyncioTestCase
from pathlib import Path
import filecmp

from config import PORT, HOST
from test_utils import send_message, receive_message, decode_and_trim,\
    NOT_FOUND, SUCCESS


_INPUT_FILE_NAME = 'src/assets/test_in.jpeg'
_OUTPUT_FILE_NAME = 'src/assets/test_out.jpeg'


class BinaryTest(IsolatedAsyncioTestCase):

    """
    Test binary file
    """
    async def test_binary_file(self) -> None:
        reader, writer = await asyncio.open_connection(HOST, PORT)

        data = Path(_INPUT_FILE_NAME).read_bytes()

        # key is not set initially
        await send_message('get my_file', writer)
        response = await receive_message(reader)
        self.assertEqual(decode_and_trim(response), NOT_FOUND)

        # insert my_file
        await send_message(f'set my_file 0 {len(data)}', writer)
        await receive_message(reader)
        await send_message(data, writer)
        response = await receive_message(reader)
        self.assertEqual(decode_and_trim(response), SUCCESS)

        # obtain my_file
        await send_message('get my_file', writer)
        response = await receive_message(reader)
        self.assertEqual(decode_and_trim(response), str(len(data)))
        response = await receive_message(reader, len(data))
        # trim trailing message separator
        received_file = response[:len(data)]
        Path(_OUTPUT_FILE_NAME).write_bytes(received_file)

        # compare files
        self.assertTrue(
            filecmp.cmp(
                _INPUT_FILE_NAME,
                _OUTPUT_FILE_NAME
            )
        )

        writer.close()
        await writer.wait_closed()


if __name__ == '__main__':
    unittest.main()
