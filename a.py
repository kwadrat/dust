#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

import serial
import time
import struct
import array
from datetime import datetime

verbose = 0

ser = serial.Serial()
ser.port = "COM20"
ser.baudrate = 9600
ser.open()
ser.flushInput()

byte = lastbyte = chr(0)
line_count = 0
excel_format = "{};{};{}\r\n"

def f2a(one_float):
    return str(one_float).replace('.', ',')

result_excel_ls = []

try:
    excel_line = excel_format.format('Time', 'PM 2.5', 'PM 10')
    result_excel_ls.append(excel_line)
    while True:
        lastbyte = byte
        byte = ser.read(size=1)
        if verbose:
            print"Got byte %x" % ord(byte)
        # We got a valid packet header
        if lastbyte == chr(170) and byte == chr(192):
            sentence = ser.read(size=8) # Read 8 more bytes
            if verbose:
                print "Sentence size {}".format(len(sentence))
                print array.array('B', sentence)
            # Decode the packet - big endian, 2 shorts for pm2.5 and pm10, 2 reserved bytes, checksum, message tail
            reading_ls = struct.unpack('<hhxxcc', sentence)
            pm_25 = reading_ls[0] / 10.0
            pm_10 = reading_ls[1] / 10.0
            # ignoring the checksum and message tail

            if line_count == 0:
                line = "PM 2.5: {} ug/m^3  PM 10: {} ug/m^3".format(pm_25, pm_10)
                the_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                excel_line = excel_format.format(the_time, f2a(pm_25), f2a(pm_10))
                result_excel_ls.append(excel_line)

                print(the_time + ' ' + line)
                
            line_count += 1
            if line_count == 5:
                line_count = 0
except serial.SerialException:
    the_time = datetime.now().strftime("%Y.%m.%d_%H.%M.%S")
    file_name = 'result_{}.csv'.format(the_time)
    fd = open(file_name, 'wb')
    one_big_text = ''.join(result_excel_ls)
    fd.write(one_big_text)
    fd.close()
    print "Written {} lines to file {}".format(len(result_excel_ls), file_name)
