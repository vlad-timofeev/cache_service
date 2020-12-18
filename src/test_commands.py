import asyncio
import unittest
from unittest import IsolatedAsyncioTestCase

from config import PORT, HOST
from test_utils import send_message, receive_message, decode_and_trim,\
    NOT_FOUND, SUCCESS


class CommandsTest(IsolatedAsyncioTestCase):

    """
    Simple CRUD test
    """
    async def test_crud(self) -> None:
        reader, writer = await asyncio.open_connection(HOST, PORT)

        # key is not set initially
        await send_message('get score', writer)
        response = await receive_message(reader)
        self.assertEqual(decode_and_trim(response), NOT_FOUND)

        # insert key
        value = '42'
        await send_message(f'set score 0 {len(value)}', writer)
        await receive_message(reader)
        await send_message(value, writer)
        response = await receive_message(reader)
        self.assertEqual(decode_and_trim(response), SUCCESS)
        await send_message('get score', writer)
        response = await receive_message(reader)
        self.assertEqual(decode_and_trim(response), str(len(value)))
        response = await receive_message(reader, len(value))
        self.assertEqual(decode_and_trim(response), value)

        # update key
        value = '999'
        await send_message(f'set score 0 {len(value)}', writer)
        await receive_message(reader)
        await send_message(value, writer)
        response = await receive_message(reader)
        self.assertEqual(decode_and_trim(response), SUCCESS)
        await send_message('get score', writer)
        response = await receive_message(reader)
        self.assertEqual(decode_and_trim(response), str(len(value)))
        response = await receive_message(reader)
        self.assertEqual(decode_and_trim(response), value)

        # delete key
        await send_message('del score', writer)
        await receive_message(reader)
        await send_message('get score', writer)
        response = await receive_message(reader)
        self.assertEqual(decode_and_trim(response), NOT_FOUND)

        writer.close()
        await writer.wait_closed()


if __name__ == '__main__':
    unittest.main()
