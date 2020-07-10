#!/usr/bin/env python

import time
#from envirophat import light, weather
from enviroplus import gas
from beebotte import *

# import ST7735
# try:
#     # Transitional fix for breaking change in LTR559
#     from ltr559 import LTR559
#     ltr559 = LTR559()
# except ImportError:
#     import ltr559

from bme280 import BME280
from pms5003 import PMS5003, ReadTimeoutError as pmsReadTimeoutError

### Replace CHANNEL_TOKEN with that of your channel
bbt = BBT(token = 'CHANNEL_TOKEN')
period = 300 ## Sensor data reporting period (5 minutes)

### Change channel name as suits you - in this instance, it is called Enviro_pHAT
temp_resource   = Resource(bbt, 'Enviro_pHAT', 'temperature')
# pressure_resource  = Resource(bbt, 'Enviro_pHAT', 'pressure')
# light_resource = Resource(bbt, 'Enviro_pHAT', 'light')

# BME280 temperature/pressure/humidity sensor
bme280 = BME280()

# PMS5003 particulate sensor
pms5003 = PMS5003()

def get_cpu_temperature():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE, universal_newlines=True)
    output, _error = process.communicate()
    return float(output[output.index('=') + 1:output.rindex("'")])
# Tuning factor for compensation. Decrease this number to adjust the
# temperature down, and increase to adjust up
factor = 2.25

cpu_temps = [get_cpu_temperature()] * 5
def run():
  while True:
    ### Assume - the '-9' is a temperature calibration to take the Pi's heat into consideration. Adjust if needed.
    unit = "C"
    cpu_temp = get_cpu_temperature()
    # Smooth out with some averaging to decrease jitter
    cpu_temps = cpu_temps[1:] + [cpu_temp]
    avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
    raw_temp = bme280.get_temperature()
    temperature = raw_temp - ((avg_cpu_temp - raw_temp) / factor)

    unit = "%"
    humidity = bme280.get_humidity()

    pm = pms5003.read()
    pm1 = float(pm.pm_ug_per_m3(1.0))
    pm2.5 = float(pm.pm_ug_per_m3(2.5))
    pm10 = float(pm.pm_ug_per_m3(10))

    if temperature is not None: # and pressure is not None and lux is not None:
       temp_resource.write(temperature)
        
   
    
    else:
        print ("Failed to get reading. Try again!")

    #Sleep some time
    time.sleep( period )

run()
