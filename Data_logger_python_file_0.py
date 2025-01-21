# ------------------------------------------------------------------------------
# IMPORT NECESSARY PACKAGES.
# ------------------------------------------------------------------------------
import serial
import time
import csv
import sys
import random
import numpy as np
from math import inf
from collections import deque

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
from matplotlib.widgets import Button

# ------------------------------------------------------------------------------
# INITIALIZED EMPTY CONTAINERS.
# ------------------------------------------------------------------------------
duration = int(input('Enter the duration in seconds for data logging: '))
refinement = 1

start_time = []

time_val_list = deque(maxlen = 800)
load_val_list = deque(maxlen = 800)
deflection_val_list = deque(maxlen = 800)

# sub_deflection_list = []

# final_time_list = []
# final_load_list = []
# final_deflection_list = []

# ------------------------------------------------------------------------------
# INITIALIZED SERIAL PORTS.
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
# INITIALIZE PLOTS FOR VISUALIZING THE (SYNTHETIC)SENSOR DATA.
# ------------------------------------------------------------------------------
def load_deflection_val():
    load = np.random.normal(0, 100)
    deflection = np.random.normal(0, 10)
    elapsed_time = time.time() - start_time[0]
    
    deflection_val_list.append(deflection)
    load_val_list.append(load)
    time_val_list.append(elapsed_time)
    return

def synthetic_sensor_data():
    load_deflection_val()
    return
    # if len(sub_deflection_list) == refinement:
    #     sub_deflection_list.clear()
    #     load_deflection_val()
    # else:
    #     if len(sub_deflection_list) < refinement:
    #         if len(deflection_val_list) == 0:
    #             i = 1
    #             while True:
    #                 load_deflection_val()
    #                 if i%2 == 0:
    #                     break
    #                 i = i+1
    #         else:
    #             x2 = deflection_val_list[-1]
    #             l2 = load_val_list[-1]
    #             t2 = time_val_list[-1]

    #             x1 = deflection_val_list[-2]
    #             l1 = load_val_list[-2]
    #             t1 = time_val_list[-2]

    #             for i in range(0, refinement, 1):
    #                 sub_deflection_val = x1 + ((x2 - x1) / refinement) * (len(sub_deflection_list) - 1)
    #                 sub_deflection_list.append(sub_deflection_val)
    #                 final_deflection_list.append(sub_deflection_val)

    #                 sub_load_val = l1 + ((l2 - l1) / refinement) * (len(sub_deflection_list) - 1)
    #                 final_load_list.append(sub_load_val)

    #                 sub_time_val = t1 + ((t2 - t1) / refinement) * (len(sub_deflection_list) - 1)
    #                 final_time_list.append(sub_time_val)
    #                 return

sns.set_theme(style = 'darkgrid')
custom_style = {
    'grid.color': 'white',
    'grid.alpha': 0.5
}
sns.set_style(custom_style)
fig, ax = plt.subplots(2, 1, figsize=(10, 8), dpi=120)

(line_deflection1,) = ax[0].plot([], [], color='cornflowerblue', lw=4, alpha=0.2)
(line_deflection,) = ax[0].plot([], [], label='Deflection (mm)', color='royalblue', lw=.5, alpha=1)
ax[0].set_title("Real-time LOAD and DEFLECTION DATA", fontweight='bold')
ax[0].set_ylabel("DEFLECTION (mm)", fontweight='bold')
ax[0].legend(loc = 'upper left')
ax[0].grid(True)

(line_load1,)       = ax[1].plot([], [], color='palevioletred', lw=4, alpha=0.2)
(line_load,)        = ax[1].plot([], [], label='Load (KN)', color='crimson', lw=.5, alpha=1)
ax[1].set_xlabel("Time (s)", fontweight='bold')
ax[1].set_ylabel("LOAD (KN)", fontweight='bold')
ax[1].legend(loc = 'upper left')
ax[1].grid(True)

def init():
    line_deflection1.set_data([], [])
    line_deflection.set_data([], [])
    
    line_load1.set_data([], [])
    line_load.set_data([], [])
    
    return line_deflection, line_load

def update(frame):
    start_time.append(time.time())
    synthetic_sensor_data()
    
    line_deflection1.set_data(time_val_list, deflection_val_list)
    line_deflection.set_data(time_val_list, deflection_val_list)
    
    line_load1.set_data(time_val_list, load_val_list)
    line_load.set_data(time_val_list, load_val_list)
    
    # ax[0].set_autoscale_on(False)
    # ax[0].set_xlim(0, duration)
    # ax[0].set_ylim(-100, 100)

    # ax[1].set_autoscale_on(False)
    # ax[1].set_xlim(0, duration)
    # ax[1].set_ylim(-500, 500)

    ax[0].relim()
    ax[0].autoscale_view()

    ax[1].relim()
    ax[1].autoscale_view()

    try:
        output_filename = 'vibration_data_log.csv'      
        if len(time_val_list) == 1:
            print(f"[INFO] Logging data to {output_filename}...")
            with open(output_filename, mode='w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(["Timestamp (seconds)", 
                                        "Load (Newton)", 
                                        "Deflection (mm)"])
                csv_writer.writerow([f'{time_val_list[-1]:.3f}',
                                        f'{load_val_list[-1]:.3f}',
                                        f'{deflection_val_list[-1]:.3f}'])
        else:
            if (len(time_val_list)%refinement >= 0):
                with open(output_filename, mode='a', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow([f'{time_val_list[-1]:.3f}',
                                         f'{load_val_list[-1]:.3f}',
                                         f'{deflection_val_list[-1]:.3f}'])
                    return line_deflection, line_load

    except IOError as e:
        print(f"[ERROR] Could not write to file {output_filename}: {e}")
    
    except Exception as e:
        print(f"[ERROR] Unexpected error during file operations: {e}")

def main():

    # ------------------------------------------------------------------------------
    # PLOT INITIALIZATION (ANIMATION)
    # ------------------------------------------------------------------------------
    ani = animation.FuncAnimation(fig,
    update,
    init_func=init,
    interval = 1,
    frames = 60,
    blit=False)

    # ------------------------------------------------------------------------------
    # STOP PLOTTING (ANIMATION)
    # ------------------------------------------------------------------------------
    def stop_animation(event):
        if len(time_val_list) > 0:
            if (time_val_list[-1] > duration) and (len(time_val_list) > 0):
                ani.event_source.stop()
    ani._fig.canvas.mpl_connect('draw_event', stop_animation)
    plt.show()
    # load_port = 'COM3' #Port for Load Sensor
    # deflection_port = 'COM4' # Port for Deflection Sensor
    # baud_rate = 9600 # Baud rate for both sensors: Data transfer in bits/second
    # load_serial = initialize_serial(load_port, 
    #                                 baud_rate)
    # deflection_serial = initialize_serial(deflection_port, 
    #                                       baud_rate)
    # load_value = read_sensor_data(load_serial)
    # deflection_value = read_sensor_data(deflection_serial)

if __name__ == '__main__':
    main()