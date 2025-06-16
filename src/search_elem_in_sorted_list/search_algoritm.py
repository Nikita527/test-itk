from typing import List


def search(arr: List[int], number: int) -> bool:
    """Поиск элемента в отсортированном списке."""
    left, right = 0, len(arr) - 1
    while left <= right:
        middle = (left + right) // 2
        if arr[middle] == number:
            return True
        elif arr[middle] < number:
            left = middle + 1
        else:
            right = middle - 1
    return False


if __name__ == "__main__":
    test_list = [1, 2, 3, 45, 356, 569, 600, 705, 923]
    n = int(input("Введите число: "))
    print(search(test_list, n))
