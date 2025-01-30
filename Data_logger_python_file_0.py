# ------------------------------------------------------------------------------
# PACKAGES:
# ------------------------------------------------------------------------------
import serial
import time
import csv
import sys
import numpy as np
import pandas as pd
from collections import deque

import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow
from pyqtgraph.Qt import QtCore
from PyQt5.QtGui import QFont


# ------------------------------------------------------------------------------
# INITIALIZATION INFO:
# ------------------------------------------------------------------------------
duration = int(input('Enter the duration in seconds for data logging: '))
sampling_rate = 50
delay_time = int(1000/sampling_rate)

pg.setConfigOptions(useOpenGL=True)
pg.setConfigOptions(antialias=True)
pg.setConfigOption('background', 'k')
pg.setConfigOption('foreground', '#82e0aa')


# ------------------------------------------------------------------------------
# INITIALIZED SERIAL PORTS:
# ------------------------------------------------------------------------------
def initialize_serial(port_name, 
                      baud_rate = 9600, 
                      timeout = 1):
    try:
        ser = serial.Serial(port=port_name, 
                            baudrate=baud_rate, 
                            timeout=timeout)
        print(f"[INFO] Connected to {port_name} at {baud_rate} baud.")
        return ser
    except serial.SerialException as e:
        print(f"[ERROR] Could not open serial port {port_name}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error while opening {port_name}: {e}")
        sys.exit(1)


# ------------------------------------------------------------------------------
# READ DATA FROM SENSORS.
# ------------------------------------------------------------------------------
def read_sensor_data(serial_connection):
    try:
        line = serial_connection.readline().decode('utf-8').strip()
        if not line:
            print("[WARNING] Empty line received from sensor.")
            return None
        data_value = float(line)
        return data_value
    except ValueError:
        print(f"[WARNING] Received non-numeric data: '{line}'")
        return None
    except serial.SerialException as e:
        print(f"[ERROR] Serial read error: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error during data read: {e}")
        return None


# ------------------------------------------------------------------------------
# (SYNTHETIC)SENSOR DATA: (NOISY + CLEAN).
# ------------------------------------------------------------------------------
data_frame_sensor_data = pd.read_csv('data_logger(synthetic_data).csv')

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
        self.plot_displacement.showGrid(x=True, y=True, alpha=0.4)
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
        self.plot_load.showGrid(x=True, y=True, alpha=0.4)
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
        self.timer.setInterval(delay_time)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()
        self.index_val = 0

    def update_plot(self):
        load_val       = data_frame_sensor_data.iloc[self.index_val, 0]
        displacement_val = data_frame_sensor_data.iloc[self.index_val, 1]
        current_time = time.time() - self.start_time
        
        self.time_data.append(current_time)
        self.displacement_data.append(displacement_val)
        self.load_data.append(load_val)

        self.curve_displacement.setData(self.time_data, self.displacement_data)
        self.curve_load.setData(self.time_data, self.load_data)
        self.index_val += 1

        if self.time_data[-1] >= duration:
            self.timer.stop()

        try:
            output_filename = 'vibration_data_log.csv'      
            if len(self.time_data) == 1:
                
                print(f"[INFO] Logging data to {output_filename}...")
                
                with open(output_filename, mode='w', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow(["Timestamp (seconds)", 
                                            "Load (Newton)", 
                                            "Deflection (mm)"])
                    csv_writer.writerow([f'{self.time_data[-1]:.3f}',
                                         f'{self.load_data[-1]:.3f}',
                                         f'{self.displacement_data[-1]:.3f}'])
            else:
                if (len(self.time_data) > 0):
                    with open(output_filename, mode='a', newline='') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow([f'{self.time_data[-1]:.3f}',
                                             f'{self.load_data[-1]:.3f}',
                                             f'{self.displacement_data[-1]:.3f}'])
                        
        except IOError as e:
            print(f"[ERROR] Could not write to file {output_filename}: {e}")

        except Exception as e:
            print(f"[ERROR] Unexpected error during file operations: {e}")

        finally:
            # if (len(self.time_data) > 0):
            if self.time_data[-1] >= duration:
                print(f'[INFO]: DATA LOGGING COMPLETED')


# ----------------------------------------------------------------------------------
# MAIN FUNCTION:
# ----------------------------------------------------------------------------------
def main():
    app = QApplication(sys.argv)
    window = RealTimePlot()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
