#!/usr/bin/env python

import time
from beebotte import *
from subprocess import PIPE, Popen

from enviroplus import gas
from bme280 import BME280
from pms5003 import PMS5003, ReadTimeoutError as pmsReadTimeoutError
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

# config var
channel_token = 'token_UE7kVdFgTaW8PYNV'
channel_name = 'enviroplus'

bbt = BBT(token = channel_token)
period = 90 ## Sensor data reporting period (5 minutes)

temp_resource   = Resource(bbt, channel_name, 'temperature')
humd_resource   = Resource(bbt, channel_name, 'humidity')
pm1_resource   = Resource(bbt, channel_name, 'pm1')
pm25_resource   = Resource(bbt, channel_name, 'pm25')
pm10_resource   = Resource(bbt, channel_name, 'pm10')
pressure_resource   = Resource(bbt, channel_name, 'pressure')
lux_resource   = Resource(bbt, channel_name, 'lux')

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

def run():
  while True:
    unit = "C"
    cpu_temps = [get_cpu_temperature()] * 5
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
    pm25 = float(pm.pm_ug_per_m3(2.5))
    pm10 = float(pm.pm_ug_per_m3(10))

    unit = "hPa"
    pressure = bme280.get_pressure()

    unit = "Lux"
    proximity = ltr559.get_proximity()
    if proximity < 10:
        lux = ltr559.get_lux()
    else:
        lux = 1


    if temperature is not None: # and pressure is not None and lux is not None:
       temp_resource.write(temperature)
       humd_resource.write(humidity)
       pm1_resource.write(pm1)
       pm25_resource.write(pm25)
       pm10_resource.write(pm10)
       pressure_resource.write(pressure)
       lux_resource.write(lux)

    else:
        print ("Failed to get reading. Try again!")

    #Sleep some time
    time.sleep( period )

run()
