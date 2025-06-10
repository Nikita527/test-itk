from current_time_meta_class import CurrentTimeMeta


class TestClass(metaclass=CurrentTimeMeta):
    """Тестовый класс."""

    def __init__(self):
        self.value = 42


assert hasattr(TestClass, "created_at")
print(TestClass.created_at)
