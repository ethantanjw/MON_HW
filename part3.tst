#BASELINE= # Use a baseline file to start right before an image is to be taken
BASELINE = part3.bsl

# Whenever temperature is high, make sure the fan turns on for at least a minute
WHENEVER temperature > 29
  WAIT fan FOR 60
  ENSURE fan or temperature <= 25 for 180
 
# Whenever temperature is low between 6am and 10pm, and lights not already on
#   make sure the lights turn on for at least two minutes
WHENEVER temperature < 22 and not led and (mtime//3600) >= 6 and (mtime//3600) < 22
  WAIT led FOR 60
  ENSURE led or temperature >= 27 FOR 180
  
# Whenever lights are on, make sure the temperature is not too high
WHENEVER led
  ENSURE temperature <= 27
  
# When the humidity is high, make sure the fan turns on for at least a minute
WHENEVER humidity >= 90
  WAIT fan FOR 60
  PRINT "FAN ON at %s (humidity %d)" %(clock_time(time), humidity)
  ENSURE fan or humidity <= 80 FOR 180

# Turn pump on when dry
WHENEVER smoist < 500
  # Give it a chance to get started
  WAIT wpump FOR 60
  WAIT not wpump FOR 360 # Turn pump off before 6 minutes have elapsed
  # Wait an hour for both moisture sensors to be above threshold
  WAIT smoist > 500 FOR 3600

# Don't let the pump overwater things
WHENEVER wpump
  ENSURE smoist < 700 FOR 3600

WHENEVER 1-22:00:00
  # Wait for 6 minutes for lights to go off after 10pm each day
  WAIT not led FOR 360

WHENEVER 1-22:10:00
  # Ensure lights stay off until just before 6am the next day
  ENSURE not led UNTIL 2-05:55:55



QUIT AT 3-00:00:00 # Run for 2 days
