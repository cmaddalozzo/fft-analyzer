from abc import ABC, abstractmethod
from typing import Optional, Callable

from .utils import round_up_to_even


class AudioStream(ABC):
    rate: int

    def __init__(
        self,
        on_data: Callable,
        device: Optional[int] = None,
        rate: Optional[int] = None,
        updates_per_second: int = 100,
    ):
        self.device = device if device else self.detect_default_device()
        self.rate = rate if rate else self.detect_rate(self.device)
        self.updates_per_second = updates_per_second
        self.on_data = on_data

        self.frames_per_buffer = round_up_to_even(self.rate / updates_per_second)

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def detect_default_device(self) -> int:
        pass

    @abstractmethod
    def detect_rate(self, device: int) -> int:
        pass
