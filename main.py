from typing import Hashable


_MISSING = object()


class LRUCache:
	def __init__(self, max_size: int):
		if not isinstance(max_size, int):
			raise TypeError('max_size should be positive integer')
		if max_size <= 0:
			raise ValueError('max_size should be positive integer')

		self._max_size = max_size
		self._dict = {}

	__slots__ = '_max_size', '_dict'

	@property
	def max_size(self) -> int:
		return self._max_size

	@property
	def full(self) -> bool:
		return len(self._dict) >= self._max_size

	def get(self, key: Hashable, default_value=_MISSING):
		if key in self._dict:
			# Put key in front of queue
			value = self._dict.pop(key)
			self._dict[key] = value
		elif default_value is _MISSING:
			raise KeyError(f"Key {key} wasn't found")
		else:
			value = default_value

		return value

	def put(self, key: Hashable, value):
		if self.full:
			lru_key = next(iter(self._dict))
			self._dict.pop(lru_key)
		self._dict[key] = value


def main():
	cache = LRUCache(2)
	cache.put(1, 2)                       # key 1 added
	cache.put(10, 20)                     # key 10 added
	print(1, cache.get(1))                          # key 1 refreshed, key 10 is LRU now
	cache.put(100, 200)                   # key 100 added (LRU key 10 removed)
	print(10, cache.get(10, None))  # key 10 not found
	print(1, cache.get(1))                          # key 1 found


if __name__ == "__main__":
	main()
