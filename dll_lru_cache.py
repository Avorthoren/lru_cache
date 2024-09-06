from typing import Hashable, Optional, Self

_MISSING = object()


class _DLListNode[T]:
	"""Double-linked list node."""
	def __init__(self, data: T = None, prv: Optional[Self] = None, nxt: Optional[Self] = None):
		self.data: T = data
		self._prv: Optional[Self] = prv
		self._nxt: Optional[Self] = nxt

	__slots__ = '_prv', '_nxt', 'data'

	def __repr__(self) -> str:
		return self.data

	@property
	def prv(self) -> Optional[Self]:
		return self._prv

	@property
	def nxt(self) -> Optional[Self]:
		return self._nxt

	def eject(self) -> Self:
		"""Eject node out of linked list, sew list back together:
		prev <-> self <-> next
		prev <----------> next
		"""
		if self._prv is not None:
			self._prv._nxt = self._nxt
		if self._nxt is not None:
			self._nxt._prv = self._prv
		self._prv = self._nxt = None

		return self

	def insert_between(self, prv: Optional[Self] = None, nxt: Optional[Self] = None) -> Self:
		if prv is not None:
			prv._nxt = self
		if nxt is not None:
			nxt._prv = self
		self._prv, self._nxt = prv, nxt

		return self


class _DLList[T]:
	"""Double linked list."""
	def __init__(self):
		self._front: Optional[_DLListNode[T]] = None
		self._back: Optional[_DLListNode[T]] = None

	__slots__ = '_front', '_back'

	class IsEmptyError(Exception):
		pass

	def empty(self) -> bool:
		return self._back is None  # and self._front is None

	@property
	def front(self) -> Optional[_DLListNode]:
		return self._front

	@property
	def back(self) -> Optional[_DLListNode]:
		return self._back

	def push_front(self, node: _DLListNode):
		self._front = node.insert_between(None, self._front)
		if self._back is None:
			# if deque was empty, front and back are the same node
			self._back = node

	def push_back(self, node: _DLListNode):
		self._back = node.insert_between(self._back, None)
		if self._front is None:
			# if deque was empty, front and back are the same node
			self._front = node

	def eject(self, node: _DLListNode) -> _DLListNode:
		if self._front is node:
			self._front = node.nxt
		if self._back is node:
			self._back = node.prv

		return node.eject()

	def pop_front(self) -> _DLListNode:
		if self._front is None:  # and self._back is None
			raise self.IsEmptyError
		return self.eject(self._front)

	def pop_back(self) -> _DLListNode:
		if self._back is None:  # and self._front is None
			raise self.IsEmptyError
		return self.eject(self._back)

	def move_to_front(self, node: _DLListNode) -> _DLListNode:
		if node is not self._front:
			self.eject(node)
			self.push_front(node)
		return node

	def move_to_back(self, node: _DLListNode) -> _DLListNode:
		if node is not self._back:
			self.eject(node)
			self.push_back(node)
		return node


class _Item[T: Hashable, V]:
	"""Cache item."""
	def __init__(self, key: T, value: V):
		self._key = key
		self.value = value

	__slots__ = '_key', 'value'

	@property
	def key(self) -> T:
		return self._key


class LRUCache[T: Hashable, V]:
	def __init__(self, max_size: int = None):
		if not isinstance(max_size, int):
			raise TypeError('max_size should be positive integer')
		if max_size <= 0:
			raise ValueError('max_size should be positive integer')

		self._max_size: Optional[int] = max_size
		# values in _dict will be nodes of the _dllist.
		# data in nodes will be items which user wants to store in the cache.
		self._dict: dict[T, _DLListNode[_Item[T, V]]] = {}
		self._dllist: _DLList[_Item[T, V]] = _DLList()

	__slots__ = '_max_size', '_dict', '_dllist'

	@property
	def max_size(self) -> int:
		return self._max_size

	@property
	def full(self) -> bool:
		return self._max_size is not None and len(self._dict) >= self._max_size

	def get(self, key: T, default_value=_MISSING) -> V:
		node = self._dict.get(key, _MISSING)
		if node is not _MISSING:
			# key in cache
			self._dllist.move_to_front(node)
			return node.data.value
		if default_value is not _MISSING:
			return default_value

		raise KeyError(f"Key {key} wasn't found")

	def put(self, key: T, value: V):
		node = self._dict.get(key, _MISSING)
		if node is not _MISSING:
			# key present in cache
			self._dllist.move_to_front(node)
			node.data.value = value
			return

		# key is not in cache
		if self.full:
			lru_node = self._dllist.pop_back()
			del self._dict[lru_node.data.key]

		node = _DLListNode(_Item(key, value))
		self._dict[key] = node
		self._dllist.push_front(node)


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
