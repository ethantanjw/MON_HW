from behavior import *
from limits import *
from transitions import Machine

#sensor data passed into greenhouse behaviors:
#  [time, lightlevel, temperature, humidity, soilmoisture, waterlevel]
#actuators are looking for a dictionary with any/all of these keywords:
#  {"led":val, "fan":True/False, "pump": True/False}


'''
The combined ambient and LED light level between 8am and 10pm should be 
in the optimal['light_level'] range;
Between 10pm and 8am, the LEDs should be off (set to 0).
'''
class Light(Behavior):

    def __init__(self):
        super(Light, self).__init__("LightBehavior")
        self.optimal_level = optimal['light_level']

        self.initial = 'Halt'
        self.states = [self.initial]
        # Add all your FSM state names to self.states
        # BEGIN STUDENT CODE
        self.states.extend(['init', 'light', 'dark'])
        # END STUDENT CODE

        self.fsm = Machine(self, states=self.states, initial=self.initial, ignore_invalid_triggers=True)

        # Add FSM transitions and actions
        # BEGIN STUDENT CODE
        self.fsm.add_transition('enable', 'Halt', 'init', after='setInitial')
        self.fsm.add_transition('doStep', 'init', 'light', conditions=['should_on'], after='adjust_light')
        self.fsm.add_transition('doStep', 'init', 'dark', conditions=['should_off'], after='setInitial')
        self.fsm.add_transition('doStep', 'light', 'dark', conditions=['should_off'], after='setInitial')
        self.fsm.add_transition('doStep', 'light', 'light', conditions=['should_adjust_light'], after='adjust_light')
        self.fsm.add_transition('doStep', 'dark', 'light', conditions=['should_on'], after='adjust_light')
        self.fsm.add_transition('disable', '*', 'Halt', after='setInitial')
        # END STUDENT CODE
        
    def enable(self):  
        self.trigger('enable')

    def disable(self): 
        self.trigger('disable')

    def setInitial(self):
        self.led = 0
        self.setLED(self.led)
        
    def perceive(self):
        self.mtime = self.sensordata["midnight_time"]
        self.time = self.sensordata["unix_time"]
        self.light = self.sensordata["light"]

    
    def act(self):
        self.trigger("doStep")
        
    # Add all your condition functions here
    # BEGIN STUDENT CODE
    def should_on(self):
        hour = (self.mtime // 3600) % 24
        return hour >= 8 and hour < 22
    
    def should_off(self):
        return not self.should_on()

    def should_adjust_light(self):
        return self.light < self.optimal_level[0] or self.light >= self.optimal_level[1]
    # END STUDENT CODE
        
    # Add all your before / after action functions here
    # BEGIN STUDENT CODE

    def adjust_light(self):
        if self.light < self.optimal_level[0]:
            self.setLED(self.led + 20)
        elif self.light >= self.optimal_level[1]:
            self.setLED(self.led - 20)

    # END STUDENT CODE

    def setLED(self, level):
        self.led = max(0, min(255, level))
        self.actuators.doActions((self.name, self.sensors.getTime(),
                                  {"led": self.led}))

    def set_optimal(self, optimal):
        self.optimal_level = [optimal-20, optimal+20]
                                  

"""
The temperature should be greater than the lower limit
"""
class RaiseTemp(Behavior):

    def __init__(self):
        super(RaiseTemp, self).__init__("RaiseTempBehavior")

        self.led = 0

        self.initial = 'Halt'
        self.states = [self.initial]
        # Add all your FSM state names to self.states
        # BEGIN STUDENT CODE
        self.states.extend(['init', 'heating'])
        # END STUDENT CODE

        self.fsm = Machine(self, states=self.states, initial=self.initial,
                           ignore_invalid_triggers=True)

        # Add FSM transitions and actions
        # BEGIN STUDENT CODE
        self.fsm.add_transition('enable', 'Halt', 'init', after='setInitial')
        self.fsm.add_transition('doStep', 'init', 'heating', conditions=['should_heat'], after='start_heating')
        self.fsm.add_transition('doStep', 'heating', 'init', conditions=['should_stop_heating'], after='stop_heating')
        self.fsm.add_transition('disable', '*', 'Halt', after='stop_heating')
        # END STUDENT CODE
        
    def enable(self):  self.trigger('enable')
    def disable(self): self.trigger('disable')

    def setInitial(self):
        self.setLED(0)
        
    def perceive(self):
        self.temp = self.sensordata["temp"]

    def act(self):
        # Use 'doStep' trigger for all other transitions
        self.trigger("doStep")

    # Add all your condition functions here
    # BEGIN STUDENT CODE
    def should_heat(self):
        return self.temp < limits['temperature'][0]

    def should_stop_heating(self):
        return self.temp >= optimal['temperature'][0]
    # END STUDENT CODE

    # Add all your before / after action functions here
    # BEGIN STUDENT CODE
    def start_heating(self):
        self.setLED(200)

    def stop_heating(self):
        self.setLED(0)
    # END STUDENT CODE
            
    def setLED(self, level):
        self.actuators.doActions((self.name, self.sensors.getTime(),
                                  {"led": level}))
        
"""
The temperature should be less than the upper limit
"""
class LowerTemp(Behavior):

    def __init__(self):
        super(LowerTemp, self).__init__("LowerTempBehavior")

        self.initial = 'Halt'
        self.states = [self.initial]
        # Add all your FSM state names to self.states
        # BEGIN STUDENT CODE
        self.states.extend(['init', 'cooling'])
        # END STUDENT CODE

        self.fsm = Machine(self, states=self.states, initial=self.initial,
                           ignore_invalid_triggers=True)

        # Add FSM transitions and actions
        # BEGIN STUDENT CODE
        self.fsm.add_transition('enable', 'Halt', 'init', after='setInitial')
        self.fsm.add_transition('doStep', 'init', 'cooling', conditions=['should_cool'], after='start_cooling')
        self.fsm.add_transition('doStep', 'cooling', 'init', conditions=['should_stop_cooling'], after='stop_cooling')
        self.fsm.add_transition('disable', '*', 'Halt', after='stop_cooling')
        # END STUDENT CODE
        
    def enable(self):  self.trigger('enable')
    def disable(self): self.trigger('disable')

    def setInitial(self):
        self.setFan(False)
        
    def perceive(self):
        self.temp = self.sensordata["temp"]

    def act(self):
        # Use 'doStep' trigger for all other transitions
        self.trigger("doStep")

    # Add all your condition functions here
    # BEGIN STUDENT CODE
    def should_cool(self):
        return self.temp >= limits['temperature'][1]

    def should_stop_cooling(self):
        return self.temp <= optimal['temperature'][1]
    # END STUDENT CODE
        
    # Add all your before / after action functions here
    # BEGIN STUDENT CODE
    def start_cooling(self):
        self.setFan(True)

    def stop_cooling(self):
        self.setFan(False)
    # END STUDENT CODE
            
    def setFan(self, act_state):
        self.actuators.doActions((self.name, self.sensors.getTime(),
                                  {"fan": act_state}))
    
"""
Humidity should be less than the limit
"""
class LowerHumid(Behavior):

    def __init__(self):
        super(LowerHumid, self).__init__("LowerHumidBehavior")

        self.initial = 'Halt'
        self.states = [self.initial]
        # Add all your FSM state names to self.states
        # BEGIN STUDENT CODE
        self.states.extend(['init', 'toohumid'])
        # END STUDENT CODE

        self.fsm = Machine(self, states=self.states, initial=self.initial,
                           ignore_invalid_triggers=True)

        # Add FSM transitions and actions
        # BEGIN STUDENT CODE
        self.fsm.add_transition('enable', 'Halt', 'init', after='setInitial')
        self.fsm.add_transition('doStep', 'init', 'toohumid', conditions=['should_lower_humidity'], after='start_fan')
        self.fsm.add_transition('doStep', 'toohumid', 'init', conditions=['is_humidity_optimal'], after='stop_fan')
        self.fsm.add_transition('disable', '*', 'Halt', after='stop_fan')
        # END STUDENT CODE
        
    def enable(self):  self.trigger('enable')
    def disable(self): self.trigger('disable')
        
    def setInitial(self):
        self.setFan(False)
        
    def perceive(self):
        self.humid = self.sensordata["humid"]

    def act(self):
        # Use 'doStep' trigger for all other transitions
        self.trigger("doStep")

    # Add all your condition functions here
    # BEGIN STUDENT CODE
    def should_lower_humidity(self):
        return self.humid >= limits["humidity"][1]

    def is_humidity_optimal(self):
        return self.humid <= optimal['humidity'][1]
    # END STUDENT CODE
        
    # Add all your before / after action functions here
    # BEGIN STUDENT CODE
    def start_fan(self):
        self.setFan(True)

    def stop_fan(self):
        self.setFan(False)
    # END STUDENT CODE

    def setFan(self, act_state):
        self.actuators.doActions((self.name, self.sensors.getTime(),
                                  {"fan": act_state}))
            
"""
Soil moisture should be greater than the lower limit
"""
class RaiseSMoist(Behavior):

    def __init__(self):
        super(RaiseSMoist, self).__init__("RaiseMoistBehavior")
        self.weight = 0
        self.weight_window = []
        self.smoist_window = []
        self.total_water = 0
        self.water_level = 0
        self.start_weight = 0
        self.last_time = 24*60*60 # Start with the prior day
        self.daily_limit = 100
        self.wet = limits["moisture"][1]

        self.initial = 'Halt'
        self.states = [self.initial]
        # Add all your FSM state names to self.states
        # BEGIN STUDENT CODE
        self.states.extend(['init', 'waiting', 'watering', 'measuring', 'done'])
        # END STUDENT CODE

        self.fsm = Machine(self, states=self.states, initial=self.initial,
                           ignore_invalid_triggers=True)

        # Add FSM transitions and actions
        # BEGIN STUDENT CODE
        self.fsm.add_transition('enable', 'Halt', 'init', after='setInitial')
        self.fsm.add_transition('doStep', 'init', 'waiting', conditions=['timer_up'], after='handle_new_day')
        self.fsm.add_transition('doStep', 'waiting', 'watering', conditions=['should_water'], after='start_watering')
        self.fsm.add_transition('doStep', 'watering', 'measuring', conditions=['timer_up'], after='stop_watering')
        self.fsm.add_transition('doStep', 'measuring', 'waiting', conditions=['timer_up'], after='calculate_water')
        self.fsm.add_transition('doStep', 'waiting', 'done', conditions=['watered_enough'], after='stop_pump')
        self.fsm.add_transition('disable', '*', 'Halt', after='stop_pump')
        self.fsm.add_transition('doStep', 'done', 'init', conditions=['new_day'], after='reset_total_water')
        # END STUDENT CODE
        
    def enable(self):  self.trigger('enable')
    def disable(self): self.trigger('disable')

    def setInitial(self):
        # pass ASK ETHAN ABOUT THIS
        self.setPump(False)
        self.setTimer(10)
        
    def sliding_window(self, window, item, length=4):
        if (len(window) == length): window = window[1:]
        window.append(item)
        return window, sum(window)/float(len(window))
    
    def perceive(self):
        self.time = self.sensordata["unix_time"]
        self.mtime = self.sensordata["midnight_time"]
        self.water_level = self.sensordata["level"]
        self.weight = self.sensordata["weight"]
        self.weight_window, self.weight_est = self.sliding_window(self.weight_window, self.weight)
        self.smoist = self.sensordata["smoist"]
        self.smoist_window, self.smoist_est = self.sliding_window(self.smoist_window, self.smoist)

    def act(self):
        # Use 'doStep' trigger for all other transitions
        self.trigger("doStep")

    # Add all your condition functions here
    # BEGIN STUDENT CODE    
    def timer_up(self):
        return self.time >= self.waittime

    def should_water(self):
        return self.total_water < self.daily_limit and self.water_level > 30 and self.smoist_est < self.wet
    
    def watered_enough(self):
        return self.total_water >= self.daily_limit or self.water_level < 30 or self.smoist_est >= self.wet
    
    def new_day(self):
        return self.last_time > self.mtime
    # END STUDENT CODE
        
    # Add all your before / after action functions here
    # BEGIN STUDENT CODE
    def handle_new_day(self):
        if self.new_day():
            self.reset_total_water()

    def start_watering(self):
        self.start_weight = self.weight_est
        self.setTimer(10)
        self.setPump(True)
    
    def stop_watering(self):
        self.setPump(False)
        self.setTimer(60)
    
    def calculate_water(self):
        dwater = max(0, self.weight_est - self.start_weight)
        self.total_water += dwater

    def stop_pump(self):
        self.setPump(False)
    
    def reset_total_water(self):
        self.total_water = 0
        self.setTimer(10)

    def setTimer(self, wait):
        self.waittime = self.time + wait

    def setTimer10(self):
        self.setTimer(10)

    def setTimer60(self):
        self.setTimer(60)
    # END STUDENT CODE

    def setPump(self,state):
        self.actuators.doActions((self.name, self.sensors.getTime(),
                                  {"wpump": state}))

"""
Soil moisture below the upper limit
"""
class LowerSMoist(Behavior):

    def __init__(self):
        super(LowerSMoist, self).__init__("LowerMoistBehavior")


        self.initial = 'Halt'
        self.states = [self.initial]
        # Add all your FSM state names to self.states
        # BEGIN STUDENT CODE
        self.states.extend(['init', 'toomoist', 'halt'])
        # END STUDENT CODE

        self.fsm = Machine(self, states=self.states, initial=self.initial,
                           ignore_invalid_triggers=True)

        # Add FSM transitions and actions
        # BEGIN STUDENT CODE
        self.fsm.add_transition('enable', 'Halt', 'init', after='setInitial')
        self.fsm.add_transition('doStep', 'init', 'toomoist', conditions=['should_fan_on'], after='start_fan')
        self.fsm.add_transition('doStep', 'toomoist', 'init', conditions=['should_fan_off'], after='stop_fan')
        self.fsm.add_transition('disable', '*', 'Halt', after='stop_fan')
        # END STUDENT CODE
        
    def enable(self):  self.trigger('enable')
    def disable(self): self.trigger('disable')
        
    def setInitial(self):
        self.setFan(False)
        
    def perceive(self):
        self.smoist = self.sensordata["smoist"]

    def act(self):
        # Use 'doStep' trigger for all other transitions
        self.trigger("doStep")

    # Add all your condition functions here
    # BEGIN STUDENT CODE
    def should_fan_on(self):
        return self.smoist >= limits['moisture'][1]
    
    def should_fan_off(self):
        return self.smoist <= optimal['moisture'][1]
    # END STUDENT CODE
        
    # Add all your before / after action functions here
    # BEGIN STUDENT CODE
    def start_fan(self):
        self.setFan(True)
    
    def stop_fan(self):
        self.setFan(False)
    # END STUDENT CODE
            
    def setFan(self, act_state):
        self.actuators.doActions((self.name, self.sensors.getTime(),
                                  {"fan": act_state}))

