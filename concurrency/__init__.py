import traceback
from concurrent import futures
from queue import Queue
from typing import Callable

from scrape.constants import TIMEOUT


def run(
    data_queue: Queue,
    predicate: Callable,
    handle_result: Callable,
    workers_done: Callable,
    timeout: int = TIMEOUT * 2,
    max_workers: int = 10,
):
    """Creates a thread pool to run predicate against data

    Args:
        data_queue (queue.Queue): A queue for data items
        predicate (typing.Callable): The function to call against a data item
        handle_result (typing.Callable): handle_result(data_item, result) is called on Future completion
        timeout (int, optional): Predicate timeout. Defaults to 10.
        max_workers (int, optional): Maximum threads. Defaults to 5.
    """

    if data_queue.empty():
        print("data_queue must have at least one item")
        return

    with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:

        # queue first data_item
        data_item = data_queue.get()
        workers = {executor.submit(predicate, data_item): data_item}

        while workers:

            # return first worker that is done [done[...], notdone[]]
            done, _ = futures.wait(
                workers, timeout=timeout, return_when=futures.FIRST_COMPLETED
            )

            if done and len(done):
                done_future = list(done)[0]
            else:
                continue

            # collect done result, remove from workers
            data_item = workers[done_future]

            try:
                result = done_future.result()
            except Exception as exc:
                print(f"{data_item} generated an exception")
                print(traceback.format_exc())
            else:
                if data_item != "DONE":
                    # print(f"{data_item} returned {result}")
                    handle_result(data_item, result)
                else:
                    print(result)

            del workers[done_future]

            # schedule all data_items currently in queue
            while not data_queue.empty():
                data_item = data_queue.get()
                workers[executor.submit(predicate, data_item)] = data_item

    workers_done()
