class SingletonMeta(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonWithMeta(metaclass=SingletonMeta):
    pass


class SingletonWithNew:

    _instances = None

    def __new__(cls, *args, **kwargs):
        if cls._instances is None:
            cls._instances = super().__new__(cls, *args, **kwargs)
        return cls._instances

    def __init__(self):
        self.value = 42


class _SingletonModule:
    pass


instance = _SingletonModule()
