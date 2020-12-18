import time
from typing import Optional, Dict, List, Tuple, Set
from collections import OrderedDict
import heapq
from dataclasses import dataclass

from config import MAX_NUMBER_OF_ITEMS


_UNEXPIRING_ITEM_TIMESTAMP = 0


@dataclass
class CachedValue:
    value: bytes
    # timestamp in nanoseconds, guaranteed to be unique for each item
    expiration: int


class Cache:
    """
    The cache
    1. Uses LRU eviction strategy.
    2. Supports TTL for items.
    """

    def __init__(self) -> None:
        # Items are stored in a hash table
        self._cache: Dict[str, CachedValue] = OrderedDict()
        # In this queue item keys that expire earlier go first
        self._expiration_queue: List[Tuple[int, str]] = []
        # Keep a set of all existing timestamps of the expiration queue above
        self._expiration_times: Set[int] = set()

    def set_item(self, key: str, value: bytes, ttl: int = 0) -> bool:
        self._evict_expired_items()

        # Calculate expiration timestamp and store item in the cache
        expiration = self._get_unique_expiration_ts(ttl) if ttl > 0\
            else _UNEXPIRING_ITEM_TIMESTAMP
        cached_value = CachedValue(value, expiration)
        self._cache[key] = cached_value

        if expiration != _UNEXPIRING_ITEM_TIMESTAMP:
            # Make the item be tracked by the expiration queue
            heapq.heappush(self._expiration_queue, (expiration, key))
            self._expiration_times.add(expiration)

        # Ensure the number of items is within the specified limit
        self._evict_extra_items()

        return key in self._cache

    def get_item(self, key: str) -> Optional[bytes]:
        self._evict_expired_items()

        cached_value = self._cache.get(key)
        if cached_value is not None:
            # Mark this item as recently accessed (for LRU strategy)
            self._cache.move_to_end(key)
        return cached_value.value if cached_value is not None else None

    def delete_item(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def _evict_extra_items(self) -> None:
        # Evict items if allowed limit for the number of items is exceeded.
        while len(self._cache) > MAX_NUMBER_OF_ITEMS:
            # with the help of OrderedDict, it's not a problem to
            # quickly get the least recently used item
            oldest = next(iter(self._cache))
            self.delete_item(oldest)

    # this method ensures there are no expired items in the cache
    def _evict_expired_items(self) -> None:
        now = time.time_ns()
        queue = self._expiration_queue
        while len(queue) > 0:
            expiration, key = queue[0]
            if expiration > now:
                # all remaning items in the queue are not expiring
                break

            should_delete = True
            cached_value = self._cache.get(key)
            if cached_value is None:
                # this item has been already deleted - that's okay, skipping
                should_delete = False
            elif cached_value.expiration != expiration:
                # this item has been replaced with a different one, skipping
                should_delete = False
            if should_delete:
                self.delete_item(key)
            # remove this item from the expiration queue
            heapq.heappop(queue)
            self._expiration_times.remove(expiration)

    # Returns unique expiration timestamp in nanoseconds
    # Based on the provided "ttl" in seconds
    def _get_unique_expiration_ts(self, ttl: int) -> int:
        expiration = int(time.time_ns() + ttl * 1e9)
        while expiration in self._expiration_times:
            # with nanosecond precision, collisions are unlikely, yet possible
            expiration += 1
        return expiration
