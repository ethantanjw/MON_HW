import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

file_path = 'sim_log_1day.txt'

sensor_data = []
actuator_data = []

with open(file_path, 'r') as file:
    current_record = {}
    for line in file:
        if line.startswith('01-'):
            if current_record:  
                sensor_data.append(current_record)
            current_record = {}

        if 'unix_time' in line:
            current_record['unix_time'] = float(line.split('unix_time: ')[1].split(',')[0])
        if 'midnight_time' in line:
            current_record['midnight_time'] = float(line.split('midnight_time: ')[1].split(',')[0])
        if 'light' in line:
            current_record['light'] = float(line.split('light: ')[1].split(',')[0])
        if 'temp' in line:
            current_record['temp'] = float(line.split('temp: ')[1].split(',')[0])
        if 'humid' in line:
            current_record['humid'] = float(line.split('humid: ')[1].split(',')[0])
        if 'weight' in line:
            current_record['weight'] = float(line.split('weight: ')[1].split(',')[0])
        if 'smoist' in line:
            current_record['smoist'] = float(line.split('smoist: ')[1].split(',')[0])
        if 'level' in line:
            current_record['level'] = float(line.split('level: ')[1].split(',')[0])

        if 'fan' in line or 'wpump' in line or 'led' in line:
            actuator_record = {
                'unix_time': current_record.get('unix_time', np.nan),
                'fan': line.split('fan: ')[1].split(',')[0].strip() == 'True',
                'wpump': line.split('wpump: ')[1].split(',')[0].strip() == 'True',
                'led': int(line.split('led: ')[1].strip())
            }
            actuator_data.append(actuator_record)

sensor_df = pd.DataFrame(sensor_data)
actuator_df = pd.DataFrame(actuator_data)

sensor_df['unix_time'] = pd.to_numeric(sensor_df['unix_time'])
actuator_df['unix_time'] = pd.to_numeric(actuator_df['unix_time'])

sensor_df['datetime'] = pd.to_datetime(sensor_df['unix_time'], unit='s')
actuator_df['datetime'] = pd.to_datetime(actuator_df['unix_time'], unit='s')

def create_plot(y_data, y_label, title):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(sensor_df['datetime'], y_data, label=title, color='blue', linewidth=1.5)
    ax.set_title(title)
    ax.set_xlabel('Time')
    ax.set_ylabel(y_label)

    def get_marker_y_values(df, y_data_column):
        marker_y_values = []
        for idx, row in df.iterrows():
            closest_idx = sensor_df['datetime'].sub(row['datetime']).abs().idxmin()
            marker_y_values.append(y_data.iloc[closest_idx])
        return marker_y_values

    fan_on = (actuator_df['fan'].shift() == False) & (actuator_df['fan'] == True)
    fan_off = (actuator_df['fan'].shift() == True) & (actuator_df['fan'] == False)

    fan_on_y = get_marker_y_values(actuator_df[fan_on], y_data)
    fan_off_y = get_marker_y_values(actuator_df[fan_off], y_data)
    ax.plot(actuator_df.loc[fan_on, 'datetime'], fan_on_y, 
            'ro', label='Fan State Change (On)', markersize=4, alpha=0.8, fillstyle='full')
    ax.plot(actuator_df.loc[fan_off, 'datetime'], fan_off_y, 
            'ro', label='Fan State Change (Off)', markersize=4, alpha=0.8, fillstyle='none')

    wpump_on = (actuator_df['wpump'].shift() == False) & (actuator_df['wpump'] == True)
    wpump_off = (actuator_df['wpump'].shift() == True) & (actuator_df['wpump'] == False)

    wpump_on_y = get_marker_y_values(actuator_df[wpump_on], y_data)
    wpump_off_y = get_marker_y_values(actuator_df[wpump_off], y_data)
    ax.plot(actuator_df.loc[wpump_on, 'datetime'], wpump_on_y, 
            'gs', label='Water Pump State Change (On)', markersize=6, alpha=0.8, fillstyle='full')
    ax.plot(actuator_df.loc[wpump_off, 'datetime'], wpump_off_y, 
            'gs', label='Water Pump State Change (Off)', markersize=6, alpha=0.8, fillstyle='none')

    led_on = (actuator_df['led'].shift() == 0) & (actuator_df['led'] > 0)
    led_off = (actuator_df['led'].shift() > 0) & (actuator_df['led'] == 0)

    led_on_y = get_marker_y_values(actuator_df[led_on], y_data)
    led_off_y = get_marker_y_values(actuator_df[led_off], y_data)
    ax.plot(actuator_df.loc[led_on, 'datetime'], led_on_y, 
            'm^', label='LED State Change (On)', markersize=6, alpha=0.8, fillstyle='full')
    ax.plot(actuator_df.loc[led_off, 'datetime'], led_off_y, 
            'm^', label='LED State Change (Off)', markersize=6, alpha=0.8, fillstyle='none')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
    fig.autofmt_xdate()
    
    handles, labels = ax.get_legend_handles_labels()
    unique_labels = dict(zip(labels, handles))
    ax.legend(unique_labels.values(), unique_labels.keys())

    plt.show()

create_plot(sensor_df['light'], 'Light Intensity', 'Light')
create_plot(sensor_df['temp'], 'Temperature (°C)', 'Temperature')
create_plot(sensor_df['humid'], 'Humidity (%)', 'Humidity')
create_plot(sensor_df['smoist'], 'Soil Moisture', 'Soil Moisture')
create_plot(sensor_df['weight'], 'Weight (g)', 'Weight')
create_plot(sensor_df['level'], 'Water Level', 'Water Level')
