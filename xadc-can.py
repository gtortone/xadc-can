#!/usr/bin/python3

from time import sleep
import can

iiodev = "/sys/bus/iio/devices/iio:device0/"

metric = [ 
        "in_temp0", 
        "in_voltage0_vccint",
        "in_voltage1_vccaux",
        "in_voltage2_vccbram",
        "in_voltage3_vccpint",
        "in_voltage4_vccpaux",
        "in_voltage5_vccoddr",
        "in_voltage6_vrefp",
        "in_voltage7_vrefn"
] 

def read_metric(i):
   
   fraw = open(iiodev + metric[i] + "_raw")
   fscale = open(iiodev + metric[i] + "_scale")
   if (i == 0):
      foffset = open(iiodev + metric[i] + "_offset")
   
   raw = (int)(fraw.read())
   scale = (float)(fscale.read())

   if (i == 0):
      offset = (int)(foffset.read())
      value = (int)(((raw - offset) / scale) * 100)  # degC/100
      can_byte1 = (int)(value / 100)
   else:
      value = (int)((raw * scale) / 10)   # V/100
      can_byte1 = (int)(value / 100)

   can_byte2 = value - (can_byte1 * 100)

   return [can_byte1, can_byte2]
   

def canprod(bus):

   print("Start CAN producer thread")

   msg = []

   for i in range(9):
      msg.append(can.Message(arbitration_id=0xFA, data=[i] + read_metric(i), is_extended_id=False))

   while 1:

      for i in range(9):
         msg[i].data = [i] + read_metric(i)
         bus.send(msg[i])

      # msg update frequency
      sleep(2)

if __name__ == "__main__":

   bus = can.Bus(interface="socketcan", channel="can0", bitrate=125000)

   canprod(bus)
