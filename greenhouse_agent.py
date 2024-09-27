import rospy, ros_hardware, layers
import sys, os, select, time
from terrabot_utils import time_since_midnight

import greenhouse_behaviors as gb
import ping_behavior as ping
import camera_behavior

def init_ros(sim, name):
    if sim: rospy.set_param('use_sim_time', True)
    rospy.init_node(name, anonymous = True)
    # Wait for clock to start up correctly
    while rospy.get_time() == 0: rospy.sleep(0.1)

def check_for_input():
    if sys.stdin in select.select([sys.stdin],[],[],0)[0]:
        input = sys.stdin.readline()
        if input[0] == 'q':
            quit()
        else:
            print("Usage: q (quit)")

# Often the agent starts running before sensor data is received
# This waits for some data to have been received, assuming the real
# sensor values are not zero
def wait_for_sensors(sensors):
    while sensors.weight == 0 or sensors.moisture == 0:
        #print("Wait")
        rospy.sleep(.25)

class BehavioralGreenhouseAgent:

    def __init__(self, sim):
        init_ros(sim, 'greenhouseagent_behavioral')

        # Initialize ROSSensors, ROSActuators, and behaviors,
        #  save each of them as instance variables, and pass them all
        #  to instantiate a BehavioralLayer
        self.sensors = ros_hardware.ROSSensors()
        # BEGIN STUDENT CODE
        self.actuators = ros_hardware.ROSActuators()
        
        #instantiate behaviors
        self.behaviors = [gb.Light(),
				gb.RaiseTemp(),
        			gb.LowerTemp(),
        			gb.LowerHumid(),
        			gb.RaiseSMoist(),
        			gb.LowerSMoist(),
        			ping.Ping(),
                    camer_behavior.TakeImage()]
        			
        #instantiate BehavioralLayer w/ ROSensors, ROSActuators, list of behaviors
        self.behavioral = layers.BehavioralLayer(self.sensors, self.actuators, self.behaviors)
        # END STUDENT CODE

    def main(self):
        wait_for_sensors(self.sensors)
        self.behavioral.startAll()
        while not rospy.core.is_shutdown():
            # Run a step of the behavioral architecture
            self.behavioral.doStep()
            rospy.sleep(1)
            check_for_input()

class LayeredGreenhouseAgent:

    def __init__(self,sim,schedulefile):
        init_ros(sim, 'greenhouseagent_layered')

        # Initialize the architecture:
        # As with the behavioral agent, initialize ROSSensors, ROSActuators,
        #  and all behaviors, save each of them as instance variables, and
        #  pass them all to instantiate a BehavioralLayer.
        # In addition, create executive and planning layers, and set the
        #  connections between the layers, using the appropriate functions
        #  defined in the executive and planning classes.  In particular,
        #  connect the behavioral and planning layers to the executive, and
        #  the executive to the planning layer.
        # Don't forget to have the planning layer invoke getNewSchedule
        self.sensors = ros_hardware.ROSSensors()
        # BEGIN STUDENT CODE
        self.actuators = ros_hardware.ROSActuators()
        
        #instantiate behaviors
        self.behaviors = [gb.Light(),
				gb.RaiseTemp(),
        			gb.LowerTemp(),
        			gb.LowerHumid(),
        			gb.RaiseSMoist(),
        			gb.LowerSMoist(),
        			ping.Ping(),
                    camera_behavior.TakeImage()]
        			
        #instantiate BehavioralLayer w/ ROSensors, ROSActuators, list of behaviors
        self.behavioral = layers.BehavioralLayer(self.sensors, self.actuators, self.behaviors)
        
        #instatiate PlanningLayer & ExecutiveLayer
        self.planning = layers.PlanningLayer(schedulefile)
        self.executive = layers.ExecutiveLayer()
        
        #set connections between layers
        #setBehavioralLayer & setPlanningLayer for the executive
        self.executive.setBehavioralLayer(self.behavioral)
        self.executive.setPlanningLayer(self.planning)
        #setExecutive for planning layer
        self.planning.setExecutive(self.executive)
        
        #invoke getNewSchedule
        self.planning.getNewSchedule()
        # END STUDENT CODE

    def main(self):
        wait_for_sensors(self.sensors)
        while not rospy.core.is_shutdown():
            t = time_since_midnight(rospy.get_time())
            # Run a step of each layer of the architecture
            # BEGIN STUDENT CODE
            self.planning.doStep(t)
            self.executive.doStep(t)
            self.behavioral.doStep()
            # END STUDENT CODE
            rospy.sleep(1)
            check_for_input()

if __name__ == '__main__':
    sim = False
    if "-m" in sys.argv and "sim" in sys.argv:
        sim = True
    if "-B" in sys.argv:
        print("Starting Behavioral Agent")
        agent = BehavioralGreenhouseAgent(sim)
        agent.main()
    elif "-L" in sys.argv:
        print("Starting Layered Agent")
        agent = LayeredGreenhouseAgent(sim,"greenhouse_schedule.txt")
        agent.main()
