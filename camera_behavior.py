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
        # Your code here
	# Initialize the FSM and add transitions
        # BEGIN STUDENT CODE
        # FSM States
        # Define the states for the FSM
        states = ['Idle', 'PrepareLight', 'WaitForLight', 'CaptureImage', 'VerifyImage']

        # Initialize the FSM
        self.fsm = Machine(model=self, states=states, initial='Idle')

        # Add transitions in the specified format
        self.fsm.add_transition('enable', 'Idle', 'PrepareLight', after='setInitialConditions')
        self.fsm.add_transition('doStep', 'PrepareLight', 'WaitForLight', conditions=['should_adjust_light'], after='adjust_light')
        self.fsm.add_transition('doStep', 'WaitForLight', 'CaptureImage', conditions=['light_ready'], after='capture_image')
        self.fsm.add_transition('doStep', 'CaptureImage', 'VerifyImage', after='verify_image')
        self.fsm.add_transition('doStep', 'VerifyImage', 'Idle', conditions=['image_verified'], after='reset_for_next_image')
        self.fsm.add_transition('doStep', 'VerifyImage', 'CaptureImage', conditions=['retry_needed'], after='retry_capture')

        self.fsm = Machine(model=self, states=states, initial='Idle')
        # END STUDENT CODE

    # Add the condition and action functions
    #  Remember: if statements only in the condition functions;
    #            modify state information only in the action functions
    # BEGIN STUDENT CODE
    def setInitialConditions(self):
        """Set initial variables and conditions when behavior is enabled."""
        self.image_counter = 0
        self.retry_count = 0
        self.max_images_per_day = 3
        self.light_level = 0  # This will be adjusted later
        print("Initial conditions set. Image counter reset to 0.")

    def adjust_light(self):
        """Adjust light to the desired level (400-600)."""
        self.light_level = 500  # Adjust light to a mid-range level
        print(f"Adjusting light level to {self.light_level} (between 400-600)...")
        time.sleep(2)  # Simulating light adjustment time

    def capture_image(self):
        """Capture the image and save it to the desired path."""
        path = op.join("/images", f"image_{self.image_counter}.jpg")
        print(f"Capturing image and saving to {path}...")
        self.image_path = path  # Store the path for verification later
        # Simulate image capture
        time.sleep(5)  # Simulate time it takes to capture and save the image

    def verify_image(self):
        """Verify if the image was successfully saved."""
        print(f"Verifying if the image exists at {self.image_path}...")
        if op.exists(self.image_path):
            print("Image verification successful!")
            self.retry_count = 0  # Reset retry count after successful capture
        else:
            print("Image verification failed!")
            self.retry_count += 1

    def retry_capture(self):
        """Retry capturing the image if verification fails."""
        print(f"Retrying image capture (Attempt {self.retry_count})...")

    def reset_for_next_image(self):
        """Reset necessary states for the next image capture."""
        self.image_counter += 1
        print(f"Image {self.image_counter} captured and verified. Ready for the next capture.")

    # Conditions
    def should_adjust_light(self):
        """Check if the light level needs to be adjusted."""
        # We assume here that light always needs adjusting for this example
        return True

    def light_ready(self):
        """Check if the light is ready for image capture."""
        # Simulate that the light is ready after a short wait time
        time.sleep(3)  # Simulating light stabilization wait time
        print("Light has stabilized and is ready.")
        return True

    def image_verified(self):
        """Check if the image has been successfully saved."""
        # Image verification passed if retry count is less than 3 and image exists
        return op.exists(self.image_path) and self.retry_count < 3

    def retry_needed(self):
        """Check if retry is needed based on verification failure."""
        return self.retry_count < 3 and not op.exists(self.image_path)

    def should_take_more_images(self):
        """Check if more images can be taken today (max 3 per day)."""
        return self.image_counter < self.max_images_per_day
    # END STUDENT CODE

    def perceive(self):
        self.time = self.sensordata['unix_time']
        # Add any sensor data variables you need for the behavior
        # BEGIN STUDENT CODE
        # Collect relevant sensor data here
        self.light_level = self.sensordata.get('light_level', 0)
        
        # Check if it's a new day and reset the image counter if necessary
        self.reset_image_counter_if_new_day()
        # END STUDENT CODE

    def act(self):
        self.trigger("doStep")
