from moviepy import VideoClip, VideoFileClip, concatenate_videoclips
import random
from collections.abc import Sequence


class LoopedCollection(Sequence):
    def __init__(self, items: list):
        self.items = items
        self._index: int | None = None

    def get_random(self):
        return random.choice(self.items)

    def get_all(self):
        return self.items

    def append(self, item):
        self.items.append(item)

    def append_list(self, items: list):
        for c in items:
            self.append(c)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index):
        return self.items[index]

    def __iter__(self):
        return iter(self.items)

    def m_iter_item_index(self):
        if self._index == None:
            self._index = 0
            return self._index

        self._index += 1

        if self._index >= len(self.items):
            self._index = 0

        return self._index

    def get_next_chunk(self, chunk_size: int):
        res = []

        for _ in range(chunk_size):
            res.append(self.items[self.m_iter_item_index()])

        return res

    def length(self):
        return len(self.items)
