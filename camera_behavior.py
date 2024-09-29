from behavior import *
from transitions import Machine
import sys, os.path as op
import os
from terrabot_utils import clock_time
import time

'''
The behavior should adjust the lights to a reasonable level (say 400-600),
wait a bit for the light to stabilize, and then request an image.
It should check to be sure the image has been recorded and, if so, process
the image; if not, try again for up to 3 times before giving up
'''

class TakeImage(Behavior):
    def __init__(self):
        super(TakeImage, self).__init__("TakeImageBehavior")

        # if os.path.exists(f"/home/robotanist/Desktop/TerraBot/agents/Mon_HW"):
        #     print("success")
        # Your code here
    # Initialize the FSM and add transitions
        # BEGIN STUDENT CODE
        self.initial = 'Halt'
        self.states = [self.initial]
        self.states.append('init')
        self.states.append('taking_images')
        self.states.append('not_taking_images')

        self.fsm = Machine(self, states=self.states, initial=self.initial, ignore_invalid_triggers=True)

        self.image_count = 0
        self.led = 0
        self.days = 0

        self.last_time = 24*60*60 # Start with the prior day
        self.fsm.add_transition('enable', 'Halt', 'init', after=['set_initial', 'adjust_light'])
        self.fsm.add_transition('doStep', 'init', 'taking_images', conditions=['correct_light_level'], after=['capture_image'])
        self.fsm.add_transition('doStep', 'init', 'not_taking_images', conditions=['not_correct_light_level'], after=['adjust_light'])        
        self.fsm.add_transition('doStep', 'not_taking_images', 'taking_images', conditions=['correct_light_level', 'not_enough_images'], after=['capture_image'])
        self.fsm.add_transition('doStep', 'taking_images', 'not_taking_images', conditions=['not_correct_light_level', 'enough_images'], after=['adjust_light'])
        
        self.fsm.add_transition('disable', '*', 'Halt')
        # END STUDENT CODE

    # Add the condition and action functions
    #  Remember: if statements only in the condition functions;
    #            modify state information only in the action functions
    # BEGIN STUDENT CODE
    def correct_light_level(self):
        return self.light >= 400 and self.light <= 600

    def not_correct_light_level(self):
        return not (self.light >= 400 and self.light <= 600)

    def adjust_light(self):
        if self.light < 400:
            self.setLED(self.led + 100)
        elif self.light >= 600:
            self.setLED(self.led - 100)

    def enough_images(self):
        return self.image_count == 3

    def not_enough_images(self):
        return self.image_count < 3

    def new_day(self):
        return self.mtime > 75599

    def set_initial(self):
        self.led = 0
        self.setLED(self.led)

    def handle_new_day(self):
        if self.new_day():
            self.image_count = 0
            self.days += 1
    
    def capture_image(self):
        print("Taking a picture, storing in %s" %f"/home/robotanist/Desktop/TerraBot/agents/Mon_HW/image_{self.time}.jpg")
        self.image_count += 1
        self.actuators.doActions((self.name, self.sensors.getTime(), {"camera": f"/home/robotanist/Desktop/TerraBot/agents/Mon_HW/{self.time}.jpg"}))
        rospy.sleep(10)


    def setLED(self, level):
        self.led = max(0, min(255, level))
        self.actuators.doActions((self.name, self.sensors.getTime(),
                                  {"led": self.led}))

    # END STUDENT CODE

    def perceive(self):
        self.time = self.sensordata['unix_time']
        # Add any sensor data variables you need for the behavior
        # BEGIN STUDENT CODE
        self.mtime = self.sensordata["midnight_time"]
        self.time = self.sensordata["unix_time"]
        self.light = self.sensordata["light"]

        if self.mtime > 75540:
            self.image_count = 0
            self.days += 1

        # END STUDENT CODE

    def act(self):
        self.trigger("doStep")