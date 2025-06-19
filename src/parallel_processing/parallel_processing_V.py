import time
import multiprocessing


from base import generate_data, process_number
from save_file import save_data_to_json


def worker(input_queue, output_queue):
    while True:
        number = input_queue.get()
        if number is None:
            break
        result = process_number(number)
        output_queue.put(result)


if __name__ == "__main__":
    n = int(input("Введите число для генерации: "))
    data = generate_data(n)

    num_workers = multiprocessing.cpu_count()
    input_queue = multiprocessing.Queue(maxsize=2 * num_workers)
    output_queue = multiprocessing.Queue()

    processes = []
    start = time.time()
    for _ in range(num_workers):
        p = multiprocessing.Process(target=worker, args=(input_queue, output_queue))
        p.start()
        processes.append(p)

    for number in data:
        input_queue.put(number)

    for _ in range(num_workers):
        input_queue.put(None)

    results = []
    for _ in range(n):
        results.append(output_queue.get())

    for p in processes:
        p.join()
    elapsed = time.time() - start

    print(f"Время выполнения (multiprocessing.Process + Queue): {elapsed:.2f} сек")
    save_data_to_json("result_parallel_processing_C.json", results)
