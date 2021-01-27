from dataclasses import dataclass
from enum import Enum
from .tcl_base import TclBase
from typing import List


class DataType(Enum):
    Signed = 0
    Unsigned = 1
    HexaDecimal = 2
    Binary = 3


def transform_to(data: str, data_type:DataType):
    if not isinstance(data_type, DataType):
        raise TypeError

    if data_type == DataType.Binary:
        return data

    if data_type == DataType.HexaDecimal:
        return '%0*X' % ((len(data) + 3) // 4, int(data, 2))

    unsigned_data = int(data, 2)
    if data_type == DataType.Unsigned:
        return unsigned_data

    if data_type == DataType.Signed:
        print(unsigned_data)
        return unsigned_data if data[0] == '0' \
            else unsigned_data - 2**len(data)

    raise ValueError

def transform_from(data, data_type:DataType, width:int) -> str:
    if not isinstance(data_type, DataType):
        raise TypeError

    if data_type == DataType.Binary:
        return data

    if data_type == DataType.HexaDecimal:
        return bin(int(data, 16))[2:].zfill(width)


    unsigned_bin = bin(data)[2:].zfill(width)
    if data_type == DataType.Unsigned:
        return unsigned_bin

    if data_type == DataType.Signed:
        return unsigned_bin if data>=2**(width-1) \
            else bin(int(data+2**(width-1), 10))[2:].zfill(width)

    raise ValueError


def parse_bitstream(bitstream:str, data_type:DataType, width:int) -> list:
    total_length = len(bitstream)
    return [
        transform_to(bitstream[i:i+width], data_type)
        for i in reversed(range(0, total_length, width))
    ]

def dump_bitstream(data:list, data_type:DataType, width:int):
    return ''.join([
            transform_from(d, data_type, width)
            for d in reversed(data)
    ])


class BaseTclObj:
    __tcl: TclBase = None

    @property
    def tcl(self) -> TclBase:
        return self.__tcl

    @tcl.setter
    def tcl(self, value):
        self.__tcl = value


@dataclass
class SourceProbe(BaseTclObj):
    instance: int
    source_len: int
    probe_len: int
    name: str

    data_type: DataType = DataType.Signed

    source = 0
    probe = 0

    def get_probe(self):
        result = self.tcl.get_probe(self.instance)
        self.probe = transform_to(result, self.data_type)
        return self.probe

    def set_source(self, value, data_type=None):
        data_type = data_type or self.data_type

        value = transform_from(value, data_type, self.source_len)
        self.tcl.set_source(self.instance, value)

        self.source = transform_to(value, self.data_type)
        return self.source

    @staticmethod
    def map(str_list: List[str], tcl):
        obj_list = []
        for data_str in str_list:
            data_list = data_str.split(' ')
            obj = SourceProbe(
                instance=int(data_list[0]),
                source_len=int(data_list[1]),
                probe_len=int(data_list[2]),
                name=data_list[3]
            )
            obj.tcl = tcl
            obj_list.append(obj)

        return obj_list


@dataclass
class SystemMemory(BaseTclObj):
    instance: int
    length: int
    width: int
    mode: str
    type_mem: str
    name: str

    data_type: DataType = DataType.Signed

    data = []

    def read(self):
        result = self.tcl.read_memory_data(self.instance, self.length)
        self.data = parse_bitstream(result, self.data_type, self.width)
        return self.data

    def write(self, data:list, start_addr=0, data_type=None):
        data_type = data_type or self.data_type

        data_str = dump_bitstream(data, data_type, self.width)
        length = len(data_str)
        words = length//self.width

        self.tcl.write_memory_data(data, self.instance, words, start_addr)
        self.data = parse_bitstream(data_str, self.data_type, self.width)

    @staticmethod
    def map(str_list: List[str], tcl):
        obj_list = []
        for data_str in str_list:
            data_list = data_str.split(' ')
            obj = SystemMemory(
                instance=int(data_list[0]),
                length=int(data_list[1]),
                width=int(data_list[2]),
                mode=data_list[3],
                type_mem=data_list[4],
                name=data_list[5],
            )
            obj.tcl = tcl
            obj_list.append(obj)

        return obj_list
