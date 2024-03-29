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
        workers_done(typing.Callable): Called when all workers are done
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

            # no worker is done
            if not done or not len(done):
                continue

            # get done worker
            done_future = list(done)[0]
            data_item = workers[done_future]

            # collect worker result
            try:
                result = done_future.result()
                handle_result(data_item, result)
            except Exception:
                print(f"{data_item} generated an exception")
                print(traceback.format_exc())

            # remove from workers
            del workers[done_future]

            # schedule all data_items currently in queue
            while not data_queue.empty():
                data_item = data_queue.get()
                workers[executor.submit(predicate, data_item)] = data_item

    workers_done()
