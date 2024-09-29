from monitor import *
from lib.terrabot_utils import clock_time, time_since_midnight

class LoggingMonitor(Monitor):

    def __init__(self, period=10):
        super(LoggingMonitor, self).__init__("LoggingMonitor", period)
        # Put any iniitialization code here
        # BEGIN STUDENT CODE
        self.filename = None
        # END STUDENT CODE

    def perceive(self):

        # {'unix_time': 946708525.0, 'midnight_time': 5725.0, 'light': 0.0, 
        # 'temp': 20.0, 'humid': 89.0, 'weight': 774.6421813964844, 'smoist': 549.0, 
        # 'level': 135.0, 'light_raw': (0, 0), 'temp_raw': (20, 20), 
        # 'humid_raw': (89, 89), 'weight_raw': (348.5889892578125, 426.0531921386719), 
        # 'smoist_raw': (549, 549), 'level_raw': 135.0}
        # BEGIN STUDENT CODE
        self.mtime = self.sensordata["midnight_time"]
        self.time = self.sensordata["unix_time"]
        # END STUDENT CODE
        pass

    def monitor(self):
        if (not self.filename):
            self.filename = f"log{int(self.time)}.txt"
        with open(self.filename, 'a') as f:
            f.write(f"{clock_time(self.time)}")
            f.write("\n")
            for key in self.sensordata:
                f.write(f", {key}: {self.sensordata[key]}")
            f.write("\n")
            for key in self.actuator_state:
                f.write(f", {key}: {self.actuator_state[key]}")
            f.write("\n\n")