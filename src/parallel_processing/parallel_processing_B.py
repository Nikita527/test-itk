import multiprocessing
import time

from base import generate_data, process_number
from save_file import save_data_to_json


if "__main__" == __name__:
    n = int(input("Введите число для генерации: "))
    data = generate_data(n)

    start = time.time()
    with multiprocessing.Pool() as pool:
        result = pool.map(process_number, data)
    elapsed = time.time() - start

    print(f"Время выполнения (multiprocessing.Pool): {elapsed:.2f} сек")
    save_data_to_json("result_parallel_processing_B.json", result)
