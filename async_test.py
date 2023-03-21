import asyncio
import aioconsole
from contextvars import ContextVar

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


async def command_writer():
    while True:
        command = await aioconsole.ainput('Enter command: ')
        commands_list = commandContext.get()
        commands_list.append(command)
        commandContext.set(commands_list)


async def run_tasks():
    tasks = [
        command_writer(),
        command_reader()
    ]

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(run_tasks())
