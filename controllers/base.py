
from abc import ABC, abstractmethod


class TrafficController(ABC):
    """Common interface for all traffic controllers."""

    @abstractmethod
    def get_signal(self, current_time, queues=None):
        pass
