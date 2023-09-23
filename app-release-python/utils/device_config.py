#!/usr/bin/env python3

import sys
import os
import struct
from utils.config import read_global_config
import utils.firewall
from utils.firewall import firewall_json_to_bin
import utils.pinmux

EXIT_WITH_ERROR = 1

DEVICE_CONFIG_PIN_MUX           = 0x01
DEVICE_CONFIG_PIN_PROTECTION    = 0x02
DEVICE_CONFIG_EVENT_ROUTING     = 0x03
DEVICE_CONFIG_INTERRUPT_MAP     = 0x04
DEVICE_CONFIG_FIREWALL          = 0x05
DEVICE_CONFIG_WOUNDING          = 0x06
DEVICE_CONFIG_CLOCKS            = 0x07
DEVICE_CONFIG_REGISTER_SETTINGS = 0x08
DEVICE_CONFIG_END_OF_LIST       = 0xFE

HEADER_SIZE_MASK                = 0x00FFFFFF

VALID_SECTIONS = [
    "metadata",
    "firewall",
    "clocks",
    "pinmux",
    "wounding", 
    "register_settings"
]

def validateSections(sections, file):
    for sec in sections:
        if sec not in VALID_SECTIONS:
            # Don't terminate the script, just print than an unsupported section was found
            print('Unsupported section "' + sec + '" found in file ' + file)
            #sys.exit(EXIT_WITH_ERROR)

def createBinary(file):

    try:
        f = open(file, 'wb')
    except:
        print(sys.exc_info()[0])
        print('ERROR creating Device Configuration binary')
        sys.exit(EXIT_WITH_ERROR)

    return f

def closeBinary(f):
    f.close()

def writeBinary(f, data):
    f.write(data)

def processChangeSets(changeSets):
    print('Processing ChangeSets')
    data = bytearray()   
    for changeSet in changeSets:
        print(changeSet)
        data += bytes(int(changeSet['address'], 16).to_bytes(4, 'little'))
        data += bytes(int(changeSet['mask'], 16).to_bytes(4, 'little'))
        data += bytes(int(changeSet['value'], 16).to_bytes(4, 'little'))

    #print(data)
    #print(type(data))
    #print(len(data))
    return data

def processRegisterSettings(configuration):
    print("Process Register_Settings")
    data = bytearray()
    for sec in configuration:
        if sec == 'change_sets':
            data = processChangeSets(configuration[sec])
    print("register_settings: ", data)
    return data

def processClocks(configuration):
    print("Process Clocks")
    data = bytearray()
    for sec in configuration:
        if sec == 'change_sets':
            data = processChangeSets(configuration[sec])
        # TODO: process other clock settings
    print("clocks: ", data)
    return data

def processPinMux(configuration):
    print("Process PinMux")
    data = utils.pinmux.json_to_bin(configuration)
    return bytearray(data)

def processFirewall(configuration, is_icv):
    print("Process Firewall")
    utils.firewall.OUTPUT_FILE = 'build/images/fw_temp.bin'
    firewall_json_to_bin(configuration, is_icv)

def processWounding(configuration):
    print("Process Wounding")
    
    print("Wounding Data: ", configuration)
    
    num = int(configuration, 0)  
    data = num.to_bytes(4,byteorder='little')
     
    return bytearray(data)     
    
def gen_device_config(file, is_icv):

    cfg = read_global_config('build/config/' + file)
    validateSections(cfg, file)
    binFile = file[:-5] + '.bin'
    f = createBinary('build/images/' + binFile)
    for sec in cfg:
        #print(sec, cfg[sec])
        if sec == "metadata":
            continue
        
        print("Create area for: " + sec)
        if sec == "wounding":
            obj = processWounding(cfg[sec])
            header = (DEVICE_CONFIG_WOUNDING<<24) | (len(obj) & HEADER_SIZE_MASK)
            writeBinary(f, struct.pack("I", header))
            writeBinary(f, obj)
        
        if sec == "pinmux":
            obj = processPinMux(cfg[sec])
            header = (DEVICE_CONFIG_PIN_MUX<<24) | (len(obj) & HEADER_SIZE_MASK)
            writeBinary(f, struct.pack("I", header))
            writeBinary(f, obj)

        if sec == "clocks":
            obj = processClocks(cfg[sec])
            header = (DEVICE_CONFIG_CLOCKS<<24) | (len(obj) & HEADER_SIZE_MASK)
            writeBinary(f, struct.pack("I", header))
            writeBinary(f, obj)

        if sec == "register_settings":
            obj = processClocks(cfg[sec])
            header = (DEVICE_CONFIG_REGISTER_SETTINGS<<24) | (len(obj) & HEADER_SIZE_MASK)
            writeBinary(f, struct.pack("I", header))
            writeBinary(f, obj)

        if sec == "firewall":
            processFirewall(cfg[sec], is_icv)

            # checking the Alif TOC Package size
            try:
                fsize = os.path.getsize(utils.firewall.OUTPUT_FILE)
                print("Firewall binary size: " + str(fsize) + " bytes")
            except:
                print(sys.exc_info()[0])
                print("Error veryfing Firewall binary size")
                sys.exit(EXIT_WITH_ERROR)


            header = (DEVICE_CONFIG_FIREWALL<<24) | (fsize & HEADER_SIZE_MASK)
            writeBinary(f, struct.pack("I", header))

            # reading the file to include it in Device Config. binary
            with open(utils.firewall.OUTPUT_FILE, 'rb') as bin_file:
                writeBinary(f, bin_file.read())

    tail = DEVICE_CONFIG_END_OF_LIST<<24
    writeBinary(f, struct.pack("I", tail))
    closeBinary(f)
