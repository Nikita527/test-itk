from datetime import datetime


class CurrentTimeMeta(type):
    """Мета класс добавляющий в класс текущее время."""

    def __new__(cls, name, bases, attrs):
        """Добавляет в класс текущее время."""
        attrs["created_at"] = datetime.now()
        return type.__new__(cls, name, bases, attrs)
