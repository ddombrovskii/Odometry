import asyncio
import time

# import aioconsole
from contextvars import ContextVar

from Utilities import LoopTimer

commandContext = ContextVar('command', default=[])


async def command_reader():
    while True:
        await asyncio.sleep(3)
        commands_list = commandContext.get()
        if len(commands_list) > 0:
            # do something ...
            print("read command:", commands_list[0])
            print("sleep 2 sec")
            commands_list.pop(0)
            commandContext.set(commands_list)


async def command_writer():
    while True:
        # command = await aioconsole.ainput('Enter command: ')
        commands_list = commandContext.get()
        # commands_list.append(command)
        commandContext.set(commands_list)


async def run_tasks():
    tasks = [
        command_writer(),
        command_reader()
    ]
    await asyncio.gather(*tasks)


#if __name__ == '__main__':
#     asyncio.run(run_tasks())

if __name__ == "__main__":
    lt = LoopTimer(0.1)
    print(lt)
    t = 0.0
    while not lt.is_loop:
        t0 = time.perf_counter()
        with lt:
            for i in range(10000):
                pass
        t += time.perf_counter() - t0

    print(lt)

    print(f"elapsed {t}")
