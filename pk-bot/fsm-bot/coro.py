import asyncio
from threading import Thread


loop = asyncio.new_event_loop()
running = True


def evaluate(future):
    global running
    stop = future.result()
    if stop:
        print("press enter to exit...")
        running = False


def side_thread(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


thread = Thread(target=side_thread, args=(loop,), daemon=True)
thread.start()


async def display(text):
    # await asyncio.sleep(5)
    print("echo:", text)
    return text == "exit"


while running:
  text = input("enter text: ")
  future = asyncio.run_coroutine_threadsafe(display(text), loop)
  future.add_done_callback(evaluate)


print("exiting")