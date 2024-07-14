from enum import Enum


class Fruits(str, Enum):
    APPLE = "apple"
    ORANGE = "orange"


class Binary(int, Enum):
    ZERO = 0
    ONE = 1
