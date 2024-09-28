import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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

        #actuators
        if 'fan' in line or 'wpump' in line or 'led' in line:
            actuator_record = {
                'unix_time': current_record.get('unix_time', np.nan),
                'fan': line.split('fan: ')[1].split(',')[0].strip() == 'True',
                'wpump': line.split('wpump: ')[1].split(',')[0].strip() == 'True',
                'led': int(line.split('led: ')[1].strip())
            }
            actuator_data.append(actuator_record)

if current_record:
    sensor_data.append(current_record)

df_sensors = pd.DataFrame(sensor_data)
df_actuators = pd.DataFrame(actuator_data)

df_sensors['datetime'] = pd.to_datetime(df_sensors['unix_time'], unit='s')
df_actuators['datetime'] = pd.to_datetime(df_actuators['unix_time'], unit='s')

fan_changes = df_actuators[df_actuators['fan'].shift() != df_actuators['fan']]
wpump_changes = df_actuators[df_actuators['wpump'].shift() != df_actuators['wpump']]
led_changes = df_actuators[df_actuators['led'].shift() != df_actuators['led']]

fig, axs = plt.subplots(3, 2, figsize=(15, 15))
fig.suptitle('Sensor Data and Actuator States Over Time')

#light
axs[0, 0].plot(df_sensors['datetime'], df_sensors['light'], label='Light', color='orange')
axs[0, 0].set_title('Light')
axs[0, 0].set_ylabel('Light Intensity')
for _, row in led_changes.iterrows():
    axs[0, 0].axvline(x=row['datetime'], color='purple', linestyle='--')

#temperature
axs[0, 1].plot(df_sensors['datetime'], df_sensors['temp'], label='Temperature', color='red')
axs[0, 1].set_title('Temperature')
axs[0, 1].set_ylabel('Temperature (°C)')
for _, row in fan_changes.iterrows():
    axs[0, 1].axvline(x=row['datetime'], color='pink', linestyle='--')

#humidity
axs[1, 0].plot(df_sensors['datetime'], df_sensors['humid'], label='Humidity', color='blue')
axs[1, 0].set_title('Humidity')
axs[1, 0].set_ylabel('Humidity (%)')
for _, row in fan_changes.iterrows():
    axs[1, 0].axvline(x=row['datetime'], color='pink', linestyle='--')

#soil moisture
axs[1, 1].plot(df_sensors['datetime'], df_sensors['smoist'], label='Soil Moisture', color='green')
axs[1, 1].set_title('Soil Moisture')
axs[1, 1].set_ylabel('Soil Moisture')
for _, row in wpump_changes.iterrows():
    axs[1, 1].axvline(x=row['datetime'], color='lightblue', linestyle='--')

#weight
axs[2, 0].plot(df_sensors['datetime'], df_sensors['weight'], label='Weight', color='purple')
axs[2, 0].set_title('Weight')
axs[2, 0].set_ylabel('Weight (g)')
for _, row in wpump_changes.iterrows():
    axs[2, 0].axvline(x=row['datetime'], color='lightblue', linestyle='--')

#water level
axs[2, 1].plot(df_sensors['datetime'], df_sensors['level'], label='Water Level', color='brown')
axs[2, 1].set_title('Water Level')
axs[2, 1].set_ylabel('Water Level')
for _, row in wpump_changes.iterrows():
    axs[2, 1].axvline(x=row['datetime'], color='lightblue', linestyle='--')

for ax in axs.flat:
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

handles = [
    plt.Line2D([], [], color='purple', linestyle='--', label='LED State Change'),
    plt.Line2D([], [], color='pink', linestyle='--', label='Fan State Change'),
    plt.Line2D([], [], color='lightblue', linestyle='--', label='Water Pump State Change')
]

fig.legend(handles=handles, loc='upper left', bbox_to_anchor=(0.02, 0.98))

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()
