from contextlib import contextmanager
from time import sleep
from typing import List

from .tcl_base import TclBase
from .types import DataType, SourceProbe, SystemMemory


class InSystemController(TclBase):

    def list_available_source_probes(self, hardware=None, device=None) -> List[SourceProbe]:
        result = super().list_available_source_probes(hardware, device)
        return SourceProbe.map(result, self)

    def list_available_memories(self, hardware=None, device=None) -> List[SystemMemory]:
        result = super().list_available_memories(hardware, device)
        return SystemMemory.map(result, self)

    @contextmanager
    def in_system(self):
        try:
            self.start_source_probe()
            self.start_system_memory()
            yield self
        finally:
            self.end_source_probe()
            self.end_system_memory()

    def get_frame(self, memory:SystemMemory, in_system:SourceProbe, delay=0.1, attempts=10):
        if in_system.source == 1:
            raise Exception("Source should be zero in the beginning!")

        in_system.data_type = DataType.Unsigned
        in_system.set_source(1)
        for _ in range(attempts):
            probe = in_system.get_probe()
            if probe == 1:
                break
            sleep(delay)
        else:
            raise Exception("Exceeded the number of attempts")

        frame = memory.read()
        in_system.set_source(0)

        return frame
