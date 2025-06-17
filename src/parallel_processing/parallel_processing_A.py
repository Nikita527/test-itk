import time
from concurrent.futures import ThreadPoolExecutor

from base import generate_data, process_number
from save_file import save_data_to_json


if "__main__" == __name__:
    n = int(input("Введите число для генерации: "))
    data = generate_data(n)

    start = time.time()
    with ThreadPoolExecutor() as executor:
        result = list(executor.map(process_number, data))
    elapsed = time.time() - start

    print(f"Время выполнения (ThreadPoolExecutor): {elapsed:.2f} сек")
    save_data_to_json("result_parallel_processing_A.json", result)
