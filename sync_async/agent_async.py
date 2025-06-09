import time

def task(name):
    print(f"{name} started")
    time.sleep(2)  # Blocking delay
    print(f"{name} finished")

def main():
    task("Task 1")
    task("Task 2")
    task("Task 3")

main()

import asyncio

async def task(name):
    print(f"{name} started")
    await asyncio.sleep(2)  # Non-blocking delay
    print(f"{name} finished")

async def main():
    await asyncio.gather(
        task("Task 1"),
        task("Task 2"),
        task("Task 3")
    )

asyncio.run(main())
