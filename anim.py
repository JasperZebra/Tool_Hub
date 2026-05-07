from PySide6.QtCore import QObject, Signal, Property


class AnimFloat(QObject):
    changed = Signal(float)

    def __init__(self, value=0.0, parent=None):
        super().__init__(parent)
        self._value = value

    def get_value(self):
        return self._value

    def set_value(self, v):
        self._value = v
        self.changed.emit(v)

    value = Property(float, get_value, set_value)
