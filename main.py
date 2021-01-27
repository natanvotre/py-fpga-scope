from time import sleep
import matplotlib.pyplot as plt
import numpy as np

from src.quartus_api import InSystemController

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
    plt.plot(np.fft.fft(data, n=len(data)*10))
    plt.show()
    sleep(1)

if __name__ == '__main__':
    main()