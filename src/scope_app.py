# # from https://doc.qt.io/qt-5/qtcharts-temperaturerecords-example.html
from PyQt5.QtChart import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import numpy as np
import matplotlib.pyplot as plt

from quartus_api.insystem_controller import InSystemController


def calc_fft(data: np.ndarray, N=None, is_complex=False):
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


def show_fft(data: np.ndarray, fs=48e3, N=None, is_complex=False, show=True, name=None):
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

class ScopeApp(QApplication):
    def __init__(self) -> None:
        super().__init__([])
        self.system_controller = InSystemController()
        self.memory = self.system_controller.list_available_memories()[0]
        self.in_system = self.system_controller.list_available_source_probes()[0]

    def build_chart(self, title="", x_label="", y_label="", x_range=None, show_range=0.1, frequency=2):
        self.series = QLineSeries()
        for i in range(10000):
            self.series.append(i*1e6/2/10000, 0)

        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTitle(title)
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setAnimationDuration(1000)
        self.chart.setTheme(QChart.ChartThemeLight)

        self.chart.createDefaultAxes()
        self.chart.axisY(self.series).setTitleText(y_label)
        self.chart.axisX(self.series).setTitleText(x_label)
        self.series.setName("data1")
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)

        self.chartView = QChartView(self.chart)
        self.chartView.setRenderHint(QPainter.Antialiasing)

        self.window = QMainWindow()
        self.window.setCentralWidget(self.chartView)
        self.window.resize(600, 300)
        self.window.show()
        self.range = x_range
        self.data = None

        timer = QTimer(self.window, interval=1/frequency*1000, timeout=self.update)
        timer.start()

    def update(self):
        self.series.clear()

        with self.system_controller.in_system() as s:
            data = s.get_frame(self.memory, self.in_system)
        data = calc_fft(data, N=10000)
        self.data = data
        if self.range is not None:
            range_list = np.linspace(self.range[0], self.range[1], len(data))
        else:
            range_list = np.linspace(0, len(data)-1, len(data))

        for i, d in zip(range_list, data):
            self.series.append(i, d)

        data_range = np.max(data) - np.min(data)
        m_min = np.min(data) - data_range*0.1
        m_max = np.max(data) + data_range*0.1
        self.chart.axisY(self.series).setRange(m_min, m_max)
        if self.range is not None:
            self.chart.axisX(self.series).setRange(*self.range)


a = ScopeApp()
a.build_chart(x_range=(0, 1e6/2))
a.exec_()
