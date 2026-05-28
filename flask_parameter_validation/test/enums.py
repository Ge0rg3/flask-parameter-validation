from enum import Enum


class Fruits(str, Enum):
    """
    Possible fruits
    """

    APPLE = "apple"  # An apple a day keeps the doctor away, so they say
    ORANGE = "orange"  # Oranges contain vitamin C, which might also keep the doctor away


class Binary(int, Enum):
    """
    Possible binary values
    """

    ZERO = 0  # Logic level low
    ONE = 1  # Logic level high
