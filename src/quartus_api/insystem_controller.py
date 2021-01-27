from typing import List

from .tcl_base import TclBase
from .types import SourceProbe, SystemMemory


class InSystemController(TclBase):

    def list_available_source_probes(self, hardware=None, device=None) -> List[SourceProbe]:
        result = super().list_available_source_probes(hardware, device)
        return SourceProbe.map(result, self)

    def list_available_memories(self, hardware=None, device=None) -> List[SystemMemory]:
        result = super().list_available_memories(hardware, device)
        return SystemMemory.map(result, self)

    def start(self):
        self.start_source_probe()
        self.start_system_memory()
