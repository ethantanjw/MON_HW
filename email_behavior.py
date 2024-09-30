from behavior import *
from transitions import Machine
import smtplib
from email.message import EmailMessage
import os

'''
The behavior should send an email that includes the team name and TerraBot
number, the date and time, the current sensor and actuator readings, and
the most recent image taken
'''
class Email(Behavior):
    def __init__(self):
        super(Email, self).__init__("EmailBehavior")
        # Your code here
	# Initialize the FSM and add transitions
        # BEGIN STUDENT CODE
        self.initial = 'Halt'
        self.states = [self.initial]
        self.states.append('Init')
        self.states.append('Done')
        self.fsm = Machine(self, states = self.states, initial = self.initial, ignore_invalid_triggers=True)
        self.fsm.add_transition('enable', '*', 'Init', after=self.send_action)
        self.fsm.add_transition('doStep', 'Init', 'Done')
        self.fsm.add_transition('disable', '*', 'Halt')
        # END STUDENT CODE

    # Add the condition and action functions
    #  Remember: if statements only in the condition functions;
    #            modify state information only in the action functions
    # BEGIN STUDENT CODE
    def init(self, sender, password):
        port = 587
        host = "smtp.office365.com"
        timeout = 2.5 # Seconds
        server = smtplib.SMTP(host, port, timeout=timeout) 
        server.ehlo()
        server.starttls()
        server.login(sender, password)
        return server

    """
    ****************************** PARAMETERS ***********************************
    * from_address[string]: the outlook account assigned to your group
    * password[string]: the password associated with the assigned outlook account
    * to_address[string]: email addresses separated by ', ' (COMMA + SPACE)
    * subject[string]: the subject of the email
    * text[string]: the content of the email (sensor readings, actuator values,
    #               explanations, etc.)
    * images[list of jpgs]: the image to be included
    *****************************************************************************
    """
    def send(self, from_address, password, to_address, subject, text, images=[]):

        try:
            server = self.init(from_address, password)
        except Exception as e:
            print("Failed to send: %s" %e)
            return False

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = from_address
        msg['To'] = to_address
        msg.set_content(text)
        for image in images:
            msg.add_attachment(image, maintype='image', subtype='jpeg')
        success = True
        try:
            server.sendmail(from_address, to_address.split(','), msg.as_string())
        except Exception as e:
            print("Failed to send: %s" %e)
            success = False

        server.close()
        return success


    def send_action(self):
        send_str = "Team 6 TerraBot Daily Info \n \n"
        for item in self.sensor_list:
            send_str += item + "\n"
        
        files = os.listdir(".")
        jpg_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg'))]
        max_val = 0
        for jf in jpg_files:
            raw_jf = jf.split('.')[0]
            deci = jf.split('.')[1]
            max_val = max(max_val, int(raw_jf))
        images_list = []
        filename = str(max_val) + '.' + deci + ".jpg"
        
        with open(filename, 'rb') as img_file:
            image_data = img_file.read()
        
        images_list.append(image_data)
        self.send("TerraBot0@outlook.com", "Simmons482", "kehaoc@andrew.cmu.edu, junweiet@andrew.cmu.edu, jaeheek@andrew.cmu.edu, alextiax@andrew.cmu.edu, rsimmons@andrew.cmu.edu", "TerraBot6 Email", send_str, images_list)
    # END STUDENT CODE


    def enable(self): self.trigger('enable')
    def disable(self): self.trigger('disable')
    
    def perceive(self):
        self.time = self.sensordata['unix_time']
        # Add any sensor data variables you need for the behavior
        # BEGIN STUDENT CODE
        self.sensor_list = []

        for key, val in self.sensordata.items():
            self.sensor_list.append(str(key) + " " + str(val))
        # END STUDENT CODE

    def act(self):
        self.trigger("doStep")

