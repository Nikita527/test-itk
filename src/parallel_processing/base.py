import random


def generate_data(n: int):
    """Генерирует радомную последовательность чисел."""
    return [random.randint(1, 1000) for _ in range(n)]


def process_number(number: int):
    """Вычисляет факториал числа."""
    return 1 if number < 2 else number * process_number(number - 1)
