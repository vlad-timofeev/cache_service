import sys
from typing import Type
from types import TracebackType

from server import Server


def _handle_exception(
    exc_type: Type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType
) -> None:
    if issubclass(exc_type, KeyboardInterrupt):
        # The purpose of this code is to avoid printing
        # the whole stack trace on KeyboardInterrupt (Ctrl+C)
        # Just a concise message is sufficient
        print(' KeyboardInterrupt')
        return
    sys.excepthook(exc_type, exc_value, exc_traceback)


def _patch_uncaught_exception_hook() -> None:
    sys._excepthook = sys.excepthook
    sys.excepthook = _handle_exception


def main() -> int:
    server = Server()
    server.run()
    return 0


if __name__ == "__main__":
    _patch_uncaught_exception_hook()
    main()
