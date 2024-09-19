from monitor import *

class LoggingMonitor(Monitor):

    def __init__(self, period=10):
        super(LoggingMonitor, self).__init__("LoggingMonitor", period)
        # Put any iniitialization code here
        # BEGIN STUDENT CODE
        # END STUDENT CODE

    def perceive(self):
        # BEGIN STUDENT CODE
        # END STUDENT CODE
        pass

    def monitor(self):
        if (not self.filename):
            self.filename = f"/home/robotanist/15_482/Mon_HW/log{int(self.time)}.txt"
        with open(self.filename, 'a') as f:
            f.write(f"{clock_time(self.time)}")
            for key in self.sensordata:
                f.write(f", {key}: {self.sensordata[key]}")
            for key in self.actuator_state:
                f.write(f", {key}: {self.actuator_state[key]}")
            f.write("\n")

