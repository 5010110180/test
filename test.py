#!/usr/bin/env python
import time
import os
import RPi.GPIO as GPIO
 
GPIO.setmode(GPIO.BCM)
DEBUG = 0
 
# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ( (adcnum > 7) or (adcnum < 0) ):
                return -1
        GPIO.output(cspin, True)
 
        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low
 
        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
 
        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1
 
        GPIO.output(cspin, True)
 
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout
 
# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25
 
# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)
 
# temperature sensor (TMP36) connected to adc #0
temperature_adc = 0;
humidity_adc = 1;
 
while True:
        # read the analog pin
        analog_temp_value = readadc(temperature_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
        analog_hum_value = readadc(humidity_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
 
        temp_voltage = (analog_temp_value * 3.3 / 1024.0) * 1000.0;
        temp = (temp_voltage - 500)/10;
 
        humidity = ((analog_hum_value * 12) / 75) - 26;
 
        if DEBUG:
                print "Temperature analog value: ", analog_temp_value
                print "Temperature voltage: ", temp_voltage
                print "Humidity analog value: ", analog_hum_value
 
        print "Temperature: ", temp
        print "Humidity: ", humidity
        print ""
 
        # hang out and do nothing for a second
        time.sleep(1)
