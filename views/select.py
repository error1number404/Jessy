import random

from discord.ui import View


class SelectView(View):
    def __init__(self, *args):
        super().__init__(timeout=None)
        self.custom_id = f'select_view.{random.randint(0, 9999999)}'
        [self.add_item(item) for item in args]

    def __iter__(self):
        class iterator(object):
            def __init__(self, obj):
                self.obj = obj
                self.keys = obj.keys()
                self.custom_id = self.keys[0]
                self.index = 0

            def __iter__(self):
                return self

            def __next__(self):
                if self.index == len(self.keys) - 1:
                    raise StopIteration
                self.index += 1
                for_return = self.obj[self.custom_id]
                self.custom_id = self.keys[self.index]
                return for_return

        return iterator(self)

    def __getitem__(self, key):
        result = [x for x in self.children if x.custom_id.split('.')[0] == key]
        return result[0] if result else None

    def keys(self):
        return [x.custom_id for x in self.children]

    async def end(self):
        [await x.end() for x in self.children]
        del self
