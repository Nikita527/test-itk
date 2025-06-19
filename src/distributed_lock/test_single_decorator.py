import datetime
import multiprocessing
import time

from distributed_lock import single


def process_transaction(n):
    @single(max_processing_time=datetime.timedelta(minutes=2))
    def inner():
        print(f"Process {n}: Start processing")
        time.sleep(2)
        print(f"Process {n}: Done")

    try:
        inner()
    except RuntimeError as e:
        print(f"Process {n}: {e}")


if __name__ == "__main__":
    process = [
        multiprocessing.Process(target=process_transaction, args=(i,))
        for i in range(3)
    ]
    for p in process:
        p.start()
    for p in process:
        p.join()
