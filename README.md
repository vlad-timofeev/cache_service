# Caching service

## Overview

This is a simple caching service with similarities to Memcached. It it able store custom objects by key. Supported commands are: `set`, `get`, and `del`. It is a concurrent, single-threaded program written in Python. The program does not depend on any third-party libraries, it uses only the standard library. Upon running it acts as a server that accepts TCP connections.

The cache supports setting a limit to the number of items stored based on LRU strategy. It also features TTL support for added/replaced items. Item keys are strings, and item values are stored as bytes - can be any type of data.

## Configuration and launch

Ensure that you have python installed and its version is >= 3.8. For example run `python --version` or `python3 --version` to check. For the rest of this README it's assumed that the Python executable is called `python3`.

Navigate to the root directory of the project and copy the sample configuration:

```
$ cp src/config.example.py src/config.py
```

Optionally open the newly created file and adjust the configuration.

Run the server, below is the sample output:

```
$ python3 src/main.py
Serving on ('127.0.0.1', 8888)
```

Now it's possible to connect with a client e.g. Telnet. There will be a sample session log in the *Testing* section below.

## API

Each incoming and outcoming message must be terminated by `\r\n`. When setting/getting an item, it is necessary to provide/obtain its size value. The size doesn't include the above-mentioned terminator. Knowing the size allows reliably write/read the full content of the stored object.

### set

Store a new item or replace the existing one.

```
set [KEY] [TTL] [SIZE]
```

* `KEY` - item key to store by.
* `TTL` - expiration in seconds, `0` for non-expiring.
* `SIZE` - size of the item value in bytes.

As the follow up message send the item value to store.

### get

Get the stored item.

```
get [KEY]
```

* `KEY` - item key to retrieve by.

If the item deleted, never stored, or expired – the response is `NOT_FOUND`.

Otherwise there will be two messages returned:

1. Size of the stored value.
2. The value itself.

### del

Delete the stored item.

```
del [KEY]
```

* `KEY` - item key to delete by.

## Testing

Ensure the server is running before testing. Restart it to clear the cache if necessary.
### Manual testing

Below is a sample testing session in Telnet.

```
$ telnet 127.0.0.1 8888
Trying 127.0.0.1...
Connected to 127.0.0.1.
Escape character is '^]'.
get score
NOT_FOUND
set score 0 2
Send 2 bytes, terminated with \r\n.
42
SUCCESS
get score
2
42
set score 0 3
Send 3 bytes, terminated with \r\n.
999
SUCCESS
get score
3
999
del score
SUCCESS
get score
NOT_FOUND
```

### Auto-tests

There are several auto-tests included. Every file in the project with name starting with `test` is for testing purposes, and doesn't affect the cache functionality.

It's possible to run a test like this:

```
$ python3 src/test_commands.py
```

Bundled tests:

* `src/test_commands.py` - basic CRUD test.
* `src/test_stress.py` - inserts and then deleted many items.
* `src/test_binary.py` - stores binary file, than retrieves it and compares with the original.
