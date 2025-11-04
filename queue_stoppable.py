#!/usr/bin/env python3
# asyncq.py

import asyncio
import itertools as it
import os
import random
import time


async def makeitem(size: int = 5) -> str:
    """
    Create a random string of a given size

    :param size: Size of the string
    :return: Random string
    """

    return "Elemtent: " + str(random.randint(0, size * 10))
    # return os.urandom(size).hex()


async def randsleep(caller=None) -> None:
    """
    Sleep for a random time between 0 and 10 seconds
    :param caller: Name of the caller
    :return: None
    """
    i = random.randint(0, 10)
    if caller:
        print(f"{caller} sleeping for {i} seconds.")
    await asyncio.sleep(i)


class Consumer:
    """
    Class for the consumer
    """

    def __init__(self, name):
        """
        Constructor
        :param name: Name of the consumer
        """
        self.stop = False
        self.name = name

    def stopping(self):
        """
        Stop the consumer
        :return: None
        """
        self.stop = True
        print(f"Consumer {self.name} stopped!")

    async def consume(self, q: asyncio.Queue) -> None:
        """
        Consume an element from the queue
        :param q: Queue
        :return: None
        """
        while self.stop is False:
            await randsleep(caller=f"Consumer {self.name}")
            i, t = await q.get()
            now = time.perf_counter()
            print(f"Consumer {self.name} got element <{i}>"
                  f" in {now - t:0.5f} seconds.")
            q.task_done()


async def produce(name: int, q: asyncio.Queue) -> None:
    """
    Produce an element and put it into the queue
    :param name: Name of the producer
    :param q: Queue to put the element into
    :return: None
    """
    n = random.randint(0, 10)
    for _ in it.repeat(None, n):  # Synchronous loop for each single producer
        await randsleep(caller=f"Producer {name}")
        i = await makeitem()
        t = time.perf_counter()
        await q.put((i, t))
        print(f"Producer {name} added <{i}> to queue.")


async def main(nprod: int, ncon: int):
    """
    Main asyncio function
    :param nprod: Number of producers
    :param ncon: Number of consumers
    :return: None
    """
    q = asyncio.Queue()
    cons = [Consumer(n) for n in range(ncon)]
    producers = [asyncio.create_task(produce(n, q)) for n in range(nprod)]
    [asyncio.create_task(cons[n].consume(q)) for n in range(len(cons))]

    await asyncio.gather(*producers)
    await q.join()  # Implicitly awaits consumers, too

    for c in cons:
        c.stopping()


if __name__ == "__main__":
    """
    Main function
    :return: None
    """
    import argparse

    random.seed(444)
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--nprod", type=int, default=3)
    parser.add_argument("-c", "--ncon", type=int, default=5)
    ns = parser.parse_args()
    start = time.perf_counter()
    asyncio.run(main(**ns.__dict__))
    elapsed = time.perf_counter() - start
    print(f"Program completed in {elapsed:0.5f} seconds.")
