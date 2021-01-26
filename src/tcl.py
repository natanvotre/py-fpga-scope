import sys
import re
from select import POLLIN, poll
from subprocess import PIPE, Popen
from signal import SIGINT
from time import sleep
from pathlib import Path
from dataclasses import dataclass
from typing import List


class TclBase:

    def __init__(self, bin_path=None, hardware=None, device=None) -> None:
        self.tcl = None
        self.stp_command = 'quartus_stp'
        if bin_path is not None:
            self.stp_command = str(Path(bin_path) / self.stp_command)

        self.initialize_tcl()
        self.set_hardware(hardware)
        self.set_device(device)

    def log(self, msg):
        """ primitive log """
        print(f'Tcl: {msg}')

    def brackets_find(self, data):
        return re.findall(r'\{(.*?)\}', data)

    def initialize_tcl(self):
        self.tcl = Popen(
            f'{self.stp_command} -s',
            shell=True,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
        )
        checks = 0
        while checks < 3:
            output = self.read_tcl(timeout=2)
            if output.find('Info: *******') >= 0:
                print('found')
                checks += 1
        self.write_command('')

    def read_tcl(self, default=None, timeout=1, *args, **kwargs):
        result = default
        try:
            result = self.tcl.stdout.readline().decode('utf8')
            if 'ERROR:' in result:
                raise Exception(result)
        except Exception as e:
            print(e)
            raise e

        return result

    def write_command(self, cmd:str, has_output=True):
        self.tcl.stdin.write(f'{cmd}\n'.encode('utf8'))
        self.tcl.stdin.flush()

        if has_output:
            data = self.read_tcl().replace('tcl> ', '')
            print(data)
            return data

        return None

    def find_hardwares(self):
        result = self.write_command('get_hardware_names')\
            .replace('[','\[')\
            .replace(']','\]')
        return self.brackets_find(result)

    def find_devices(self, hardware=None):
        if hardware is None:
            hardware = self.hardware

        result = self.write_command(f'get_device_names -hardware_name "{hardware}"')
        return self.brackets_find(result)

    def set_hardware(self, name=None):
        if name is None:
            self.hardware = self.find_hardwares()[0]
        else:
            self.hardware = name

    def set_device(self, name=None):
        if name is None:
            self.device = self.find_devices()[0]
        else:
            self.device = name

    def start_source_probe(self, hardware=None, device=None):
        hardware = hardware or self.hardware
        device = device or self.device

        self.write_command(
            'start_insystem_source_probe '
            f'-hardware_name "{hardware}" -device_name "{device}"',
            has_output=False
        )

    def end_source_probe(self):
        self.write_command('end_insystem_source_probe', has_output=False)

    def list_available_source_probes(self, hardware=None, device=None):
        hardware = hardware or self.hardware
        device = device or self.device

        result = self.write_command(
            'get_insystem_source_probe_instance_info '
            f'-hardware_name "{hardware}" -device_name "{device}"'
        )
        return self.brackets_find(result)

    def get_probe(self, id:int):
        return self.write_command(
            f'puts [read_probe_data -instance_index {id}]'
        )

    def set_source(self, id:int, value:str):
        self.write_command(
            f'write_source_data -instance_index {id} -value "{value}"',
            has_output=False
        )

    def start_system_memory(self, hardware=None, device=None):
        hardware = hardware or self.hardware
        device = device or self.device

        self.write_command(
            'begin_memory_edit '
            f'-hardware_name "{hardware}" -device_name "{device}"',
            has_output=False,
        )

    def end_system_memory(self):
        self.write_command('end_memory_edit', has_output=False)

    def list_available_memories(self, hardware=None, device=None):
        hardware = hardware or self.hardware
        device = device or self.device

        result = self.write_command(
            'get_editable_mem_instances '
            f'-hardware_name "{hardware}" -device_name "{device}"'
        )
        return self.brackets_find(result)

    def get_memory_data(self, id, words, start_addr=0):
        return self.write_command(
            f'puts [read_content_from_memory -instance_index {id}'
            f' -start_address {start_addr} -word_count {words} -content_in_hex]'
        )



@dataclass
class SourceProbe:
    instance: int
    source_len: int
    probe_len: int
    name: str

    source=0
    probe=0
    tcl:TclBase=None
    def update(tcl, source: int):
        # TODO
        pass

    def read(self, tcl:TclBase=None):
        tcl = tcl or self.tcl
        return tcl.get_probe(self.instance)

    @staticmethod
    def map(str_list: List[str]):
        return [
            SourceProbe(*data_str.split(' '))
            for data_str in str_list
        ]

@dataclass
class SystemMemory:
    instance: int
    length: int
    width: int
    mode: str
    type_mem: str
    name: str

    source=0
    probe=0
    tcl:TclBase=None
    def update(tcl, source: int):
        # TODO
        pass

    def read(self, tcl:TclBase=None):
        # TODO
        pass
        # tcl = tcl or self.tcl
        # return tcl.get_probe(self.instance)

    @staticmethod
    def map(str_list: List[str]):
        return [
            SystemMemory(*data_str.split(' '))
            for data_str in str_list
        ]


class InSystemController(TclBase):

    def list_available_source_probes(self, hardware=None, device=None):
        result = super().list_available_source_probes(hardware, device)
        return SourceProbe.map(result)

    def list_available_memories(self, hardware=None, device=None):
        result = super().list_available_memories(hardware, device)
        return SystemMemory.map(result)

    def start(self):
        self.start_source_probe()
        self.start_system_memory()


if __name__ == "__main__":
    base = InSystemController()
    print(base.hardware)
    print(base.device)
    probes = base.list_available_source_probes()
    print(probes)
    base.start_source_probe()
    print(base.get_probe(probes[0].instance))
    mems = base.list_available_memories()
    base.end_source_probe()
    base.start_system_memory()
    print(mems)
    print(base.get_memory_data(mems[0].instance, mems[0].length))
    base.end_system_memory()
    sleep(1)
