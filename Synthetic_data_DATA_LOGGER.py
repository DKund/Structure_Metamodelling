import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

duration = int(input('ENTER THE DURATION(in seconds) FOR DATA LOGGING: ')) #500
sampling_rate = int(input('ENTER THE SAMPLING RATE(samples/second): ')) #50

load_list = []
deflection_list = []

def load_data(t):
    base_load = 10.0    # kN
    amplitude = 1.0     # kN
    frequency = 0.5     # Hz
    noise_level = 0.1   # Random Noise

    load_value = (base_load
                  + amplitude * np.sin(2.0 * np.pi * frequency * t)
                  + noise_level * np.random.randn())
    return load_value

def deflection_data(t):
    amplitude_main = 2.0      # mm main deflection amplitude
    frequency_main = 0.5      # Hz, matching the main load frequency
    amplitude_second = 0.5    # mm main deflection amplitude
    frequency_second = 2.0    # Hz, matching the main load frequency
    noise_level = 0.05        # Random Noise

    deflection_value = (amplitude_main * np.sin(2.0 * np.pi * frequency_main * t + (np.pi/4))
                        + amplitude_second * np.sin(2.0 * np.pi * frequency_second * t)
                        + noise_level * np.random.randn())
    return deflection_value

def main():
    time_val = 0
    increment = 1/50
    while (True):
        if (time_val) == 0:
            print(f'[INFO]: DATA LOGGING INITIATED')
        
        load_val = load_data(time_val)
        deflection_val = deflection_data(time_val)

        load_list.append(load_val)
        deflection_list.append(deflection_val)

        if (len(load_list) > 0) and (len(load_list)%5000 == 0):
            print(f'[INFO]: LOGGED {len(load_list)} DATA POINTS')

        if time_val >= duration:
            print(f'[INFO]: DATA LOGGING COMPLETED')
            break
        time_val = time_val + increment
    
    dataframe = pd.DataFrame({
        'Load(kN)'      : load_list,
        'Deflection(mm)': deflection_list  
    })
    dataframe.to_csv('data_logger(synthetic_data).csv',
                     index = False)
if __name__ == '__main__':
    main()