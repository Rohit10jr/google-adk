import time

def task(name):
    print(f"{name} started")
    time.sleep(2)  # Blocking delay
    print(f"{name} finished")

def main():
    print("--- synchronous example ---")
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
    print("--- asynchronus example ---")
    await asyncio.gather(
        task("Task 1"),
        task("Task 2"),
        task("Task 3")
    )
    print("--- complete ---")

        
coro1 = task("Task 1")
coro2 = task("Task 2")
coro3 = task("Task 3")
print(coro1, coro2, coro3)
asyncio.run(main())
# dont work
# asyncio.run(asyncio.gather(
#     task("Task 1"),
#     task("Task 2"),
#     task("Task 3")
# ))
# asyncio.run(coro1, coro2, coro3)
