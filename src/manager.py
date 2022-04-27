from collections import OrderedDict
from src.utils import *
import src.lang as lang


class Manager:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.tasks = OrderedDict()

    def submit(self, coro):
        @functools.wraps(coro)
        def wrapper(api, *args):
            async def create_task():
                task = self.loop.create_task(coro(api, *args), name=f"{type(api).__name__}({api.coin}).{coro.__name__}")
                self.tasks[task] = api
                return task

            return create_task()

        return wrapper

    async def cancel(self, idx: int):
        if idx - 1 in range(len(self.tasks)):
            task, api = list(self.tasks.items())[idx - 1]
            task.cancel()
            while not task.done():
                await asyncio.sleep(0.01)
            self.tasks.pop(task)
            print(f"{task.get_name()}{lang.cancelled}.")

    async def stop(self):
        while self.tasks:
            keys = list(self.tasks.keys())
            for task in keys:
                if task.done():
                    self.tasks.pop(task)
                else:
                    task.cancel()
            await asyncio.sleep(0.01)

    async def clear(self):
        keys = list(self.tasks.keys())
        for task in keys:
            if task.done():
                self.tasks.pop(task)

    def show(self):
        for i, task in enumerate(self.tasks.keys()):
            print(f'{i + 1}   {task.get_name()}')
        print('b   Back')

    async def join(self):
        await asyncio.gather(*self.tasks.keys())

    async def menu(self):
        while True:
            print(lang.manager_menu)
            command = await ainput(self.loop)
            if command == '1':
                while True:
                    self.show()
                    command = await ainput(self.loop)
                    if command == 'b':
                        break
                    idx = int(command)
                    if idx - 1 in range(len(self.tasks)):
                        await self.sub_menu(idx)
            elif command == '2':
                await self.clear()
            elif command == '3':
                await self.stop()
            elif command == 'b':
                return
            else:
                continue

    async def sub_menu(self, idx: int):
        task, api = list(self.tasks.items())[idx - 1]
        print(idx, self.task_info(task), api)
        while True:
            print(lang.manager_sub_menu)
            command = await ainput(self.loop)
            if command == '1':
                await self.cancel(idx)
                return
            elif command == '2':
                try:
                    raise NotImplemented('Modify attribute')
                except Exception as exc:
                    print(exc)
            elif command == 'b':
                return
            else:
                continue

    def task_info(self, task):
        return task.get_name()
