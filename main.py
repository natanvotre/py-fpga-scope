import matplotlib.pyplot as plt
import numpy as np
from time import sleep
from numpy import ndarray

from src.quartus_api import InSystemController

from PyQt5.QtWidgets import QApplication, QLabel

def calc_fft(data: ndarray, N=None, is_complex=False):
    if N is None:
        N = int(len(data)/2)*2

    windowed_data = data * np.hanning(len(data))
    result = 20*np.log10(
        np.abs(
            np.fft.fft(windowed_data, N)
        ) / N
    )
    if is_complex:
        data = np.zeros(N)
        data[:int(N/2)] = result[int(N/2):]
        data[int(N/2):] = result[:int(N/2)]
        return data

    return result[:int(N/2)]


def show_fft(data: ndarray, fs=48e3, N=None, is_complex=False, show=True, name=None):
    if N is None:
        N = int(len(data)/2)*2
    if is_complex:
        f = np.linspace(-fs/2, fs/2, N)
    else:
        f = np.linspace(0, fs/2, int(N/2))
    fft = calc_fft(data, N, is_complex)
    plt.clf()
    plt.plot(f, fft)
    if show:
        plt.show()
    else:
        plt.savefig(name)


def main():
    base = InSystemController()
    print(f'Current Hardware: {base.hardware}')
    print(f'Current Device: {base.device}')

    probes = base.list_available_source_probes()
    print(f'Available probes: {probes}')
    mems = base.list_available_memories()
    print(f'Available memories: {mems}')

    probe = probes[0]
    mem = mems[0]

    base.start_source_probe()
    probe.get_probe()
    probe.set_source(1)
    print(probe.source, probe.probe)

    base.start_system_memory()
    data = mem.read()
    base.end_system_memory()
    print(data)
    print(data[-1])
    print(hex(data[-1]))
    plt.plot(data)
    plt.show()
    show_fft(data, fs=1e6, N=10000)


if __name__ == '__main__':
    main()