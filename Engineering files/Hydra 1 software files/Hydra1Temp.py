
import RPi.GPIO as GPIO
import sys
import os
import time
import datetime
import csv
from w1thermsensor import W1ThermSensor
sensor = W1ThermSensor()

Sample=0
temperature=0

def get_filename_datetime():
    # Use current date to get a text file name.
    return "TempData-" + str(datetime.date.today()) + ".txt"

while True:
  temperature = sensor.get_temperature()
  #print("The temperature is %s celsius" % temperature)
  filename = get_filename_datetime()
  x = time.asctime()  # for time stamp in the temperature file file
  with open(os.path.join('/home/pi/Hydra1Log/TempratureLog',filename), 'a') as csvfile:  # to store temperature data in a file, as txt file
       writer = csv.DictWriter(csvfile, fieldnames=['Time', 'Sample', 'Temperature'], lineterminator='\n')
       writer.writerow({'Time': x, 'Sample': Sample,'Temperature': temperature})
  csvfile.close()
  Sample=Sample+1
  time.sleep(120)
        
