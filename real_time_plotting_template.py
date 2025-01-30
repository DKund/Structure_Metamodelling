import sys
import time
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow
from pyqtgraph.Qt import QtCore
from collections import deque
from PyQt5.QtGui import QFont

pg.setConfigOptions(useOpenGL=True)
pg.setConfigOptions(antialias=True)
pg.setConfigOption('background', 'k')
pg.setConfigOption('foreground', '#82e0aa')

class RealTimePlot(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Displacement Time Plot')
        self.resize(1000, 600)

        self.plot_layout = pg.GraphicsLayoutWidget()
        self.setCentralWidget(self.plot_layout)
        
        self.plot_displacement = self.plot_layout.addPlot(row=0, col=0)
        self.plot_load         = self.plot_layout.addPlot(row=1, col=0)

        # ------------------------------------------------------------------------------
        # CONFIGURE DISPLACEMENT VS TIME PLOT:
        # ------------------------------------------------------------------------------
        self.plot_displacement.setLabel ('left', 'Displacement', units='mm', **{
            'font-size': '10pt',
            'font-family': 'Square',
            'color': '#82e0aa'
        })
        self.plot_displacement.setLabel ('bottom', 'Time', units='s', **{
            'font-size': '10pt',
            'font-family': 'Square',
            'color': '#82e0aa'
        })
        self.plot_displacement.showGrid(x=True, y=True, alpha=0.25)
        self.plot_displacement.setTitle('Displacement Vs Time', size='12pt')

        # ------------------------------------------------------------------------------
        # CONFIGURE LOAD VS TIME PLOT:
        # ------------------------------------------------------------------------------
        self.plot_load.setLabel ('left', 'Load', units='kN', **{
            'font-size': '10pt',
            'font-family': 'Square',
            'color': '#82e0aa'
        })
        self.plot_load.setLabel ('bottom', 'Time', units='s', **{
            'font-size': '10pt',
            'font-family': 'Square',
            'color': '#82e0aa'
        })
        self.plot_load.showGrid(x=True, y=True, alpha=0.25)
        self.plot_load.setTitle('Load Vs Time', size='12pt')

        # ------------------------------------------------------------------------------
        # CONFIGURE PLOT TICKS AXES:
        # ------------------------------------------------------------------------------
        plot_list = [self.plot_displacement,
                     self.plot_load]
        axis_font = QFont()
        axis_font.setBold(True)
        for p_item in plot_list:
            p_item.getAxis('left').setStyle(tickFont = axis_font)
            p_item.getAxis('bottom').setStyle(tickFont = axis_font)
        
        # ------------------------------------------------------------------------------
        # PLOT DISPLACEMENT VS TIME AND LOAD VS TIME CURVE:
        # ------------------------------------------------------------------------------
        self.plot_displacement.addLegend(**{
            'font-size': '10pt',
            'font-family': 'Square',
            'color': '#82e0aa'
        })
        self.plot_load.addLegend(**{
            'font-size': '10pt',
            'font-family': 'Square',
            'color': '#82e0aa'
        })
        self.curve_displacement = self.plot_displacement.plot([], [],
                                           pen=pg.mkPen(('#e74c3c'),
                                                        width = 2),
                                           name = 'Sensor Displacement(mm)')
        self.curve_load = self.plot_load.plot([], [],
                                           pen=pg.mkPen(('#f39c12'),
                                                        width = 2),
                                           name = 'Sensor Load(kN)')

        self.time_data = deque(maxlen = 500)
        self.displacement_data = deque(maxlen = 500)
        self.load_data = deque(maxlen = 500)

        self.start_time = time.time()

        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        displacement = np.random.randn()
        load = np.random.randn()
        current_time = time.time() - self.start_time

        self.time_data.append(current_time)
        self.displacement_data.append(displacement)
        self.load_data.append(load)

        self.curve_displacement.setData(self.time_data, self.displacement_data)
        self.curve_load.setData(self.time_data, self.load_data)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RealTimePlot()
    window.show()
    sys.exit(app.exec_())
