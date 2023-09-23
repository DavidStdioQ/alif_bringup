#!/usr/bin/env python3

# TODO: Check images are present in alif/ folder.
# check for online updates? Download and apply?

import os
import sys
import signal
import argparse
sys.path.append("./isp")
from serialport import serialPort
from serialport import COM_BAUD_RATE_MAXIMUM
#import ispcommands
from isp_core import *
from isp_util import *
#from utils.discover import getValues
import utils.config
from utils.config import *
#from device import *
import device_probe

# Define Version constant for each separate tool 
#  Version                  Feature
# 0.16.000     Addition of baud rate increase for bulk transfer
# 0.20.000     Removed JTAG access
# 0.21.000     Reset option set as default
# 0.21.001     Suppress maintenance mode output
# 0.21.002     Added python error exit code  
# 0.22.000     Added support for multi-packages update (Alif's packages for different Part#/Revs) 
#              also, removed A0 related-code 
# 0.23.000     Added probe to detect the target and abort if Revision mismatchs the selection 
# 0.24.000     get baudrate from DBs 
TOOL_VERSION ="0.24.000"

EXIT_WITH_ERROR = 1

def getSeramImageString(isp, image):
    address = isp_get_seram_update_address_no_wait(isp)
    return image + ' ' + hex(address)

def main():
    if sys.version_info.major == 2:
        print("You need Python 3 for this application!")
        sys.exit(EXIT_WITH_ERROR)

    parser = argparse.ArgumentParser(description='Update System Package in MRAM')
    parser.add_argument("-d" , "--discover", action='store_true', \
                        default=False, help="COM port discovery for ISP")
    parser.add_argument("-b", "--baudrate", help="(isp) serial port baud rate",
                        type=int)
    parser.add_argument("-s", "--switch", 
                        help="(isp) dynamic baud rate switch toggle, default=on",
                        action="store_false")
    #parser.add_argument("-sr", "--seram", 
    #                    help="(isp) update a single SERAM image with the specified new image",
    #                    type=str)
    parser.add_argument("-x", "--exit", default=True, 
                        help="(isp) exit on NAK", action="store_true")
    parser.add_argument("-nr", "--no_reset", default=False, 
                        help="do not reset target before operation", action="store_true")                        
    parser.add_argument("-na", "--no_authentication", action='store_true', 
                        help="run in non-authenticated mode", 
                        default=False)
    parser.add_argument("-V" , "--version",
                        help="Display Version Number", action="store_true")
    parser.add_argument("-v" , "--verbose",
                        help="verbosity mode", action="store_true")    
    args = parser.parse_args()
    if args.version:     
        print(TOOL_VERSION)
        sys.exit()

    # memory defines for Alif/OEM MRAM Addresses and Sizes
    load_global_config()
    DEVICE_PART_NUMBER = utils.config.DEVICE_PART_NUMBER
    DEVICE_REVISION = utils.config.DEVICE_REVISION
    DEVICE_REV_BAUD_RATE = utils.config.DEVICE_REV_BAUD_RATE
    DEVICE_PACKAGE = utils.config.DEVICE_PACKAGE
    DEVICE_REV_PACKAGE_EXT = utils.config.DEVICE_REV_PACKAGE_EXT
    DEVICE_OFFSET  = utils.config.DEVICE_OFFSET
    MRAM_BASE_ADDRESS = utils.config.MRAM_BASE_ADDRESS
    ALIF_BASE_ADDRESS = utils.config.ALIF_BASE_ADDRESS
    OEM_BASE_ADDRESS = utils.config.APP_BASE_ADDRESS
    MRAM_SIZE = utils.config.MRAM_SIZE

    os.system('')                   # Help MS-DOS window with ESC sequences

    #if args.seram:
    #    print('Burning: SERAM Image in MRAM')
    #else:
    print('Burning: System Package in MRAM')
    
    print('Selected Device:')   
    print('Part# ' + DEVICE_PART_NUMBER + ' - Rev: ' + DEVICE_REVISION)   
    print('- MRAM Base Address: ' + hex(ALIF_BASE_ADDRESS))

    rev_ext = DEVICE_REV_PACKAGE_EXT[DEVICE_REVISION]
    alif_image = 'alif/' + DEVICE_PACKAGE + '-' + rev_ext + '.bin'
    alif_offset = 'alif/' + DEVICE_OFFSET + '-' + rev_ext + '.bin'

    baud_rate = DEVICE_REV_BAUD_RATE[DEVICE_REVISION]
    if args.baudrate is not None:
        baud_rate = args.baudrate

    dynamic_baud_rate_switch = args.switch

    if sys.platform == "linux":
        imageList = alif_image + ' ' + hex(ALIF_BASE_ADDRESS) + \
            ' ' + alif_offset + ' ' + hex(MRAM_BASE_ADDRESS + MRAM_SIZE - 16)

    else:
        imageList = '../' + alif_image + ' ' + hex(ALIF_BASE_ADDRESS) + \
            ' ../' + alif_offset + ' ' + hex(MRAM_BASE_ADDRESS + MRAM_SIZE - 16)  

    print('\n')

    dynamic_string = "Enabled" if dynamic_baud_rate_switch else "Disabled"
    print("[INFO] baud rate ", baud_rate)
    print("[INFO] dynamic baud rate change ", dynamic_string)

    handler = CtrlCHandler()     # handle ctrl-c key press
    isp = serialPort(baud_rate)  # Serial dabbling open up port.

    if args.discover:            # discover the COM ports if requested
        isp.discoverSerialPorts()

    errorCode = isp.openSerial()
    if errorCode is False:
        print("[ERROR] isp openSerial failed for %s" %isp.getPort())
        sys.exit(EXIT_WITH_ERROR)
    print("[INFO] %s open Serial port success" %isp.getPort())

    isp.setBaudRate(baud_rate)

    if not args.no_reset:
        put_target_in_maintenance_mode(isp, baud_rate, args.verbose)

    isp.setVerbose(args.verbose)
    isp.setExit(args.exit)

    # probe the device before update
    device = device_probe.device_get_attributes(isp)
    # check SERAM is the bootloader stage
    print('Bootloader stage: ' + device_probe.STAGE_TEXT[device.stage])
    if device.stage != device_probe.STAGE_SERAM:
        print('Please use Recovery option from ROM menu in Maintenance Tool')
        sys.exit(EXIT_WITH_ERROR)

    #print('Device Part#: ' + device.part_number)
    print('Device Revision: ' + device.revision)
    if device.revision != DEVICE_REVISION:
        print("[ERROR] Target device revision (%s) mismatch with configured device (%s)"
            % (device.revision,DEVICE_REVISION))
        sys.exit(EXIT_WITH_ERROR)

    isp_start_no_wait(isp)                         # Start ISP Sequence

    # if updating a single SERAM image, generate the image string for it
    #if args.seram:
    #    imageList = getSeramImageString(isp, args.seram)
        
    if sys.platform == "linux":
        imageList = imageList.replace('\\','/')
    else:
        imageList = imageList.replace('/','\\')

    if dynamic_baud_rate_switch:
        isp_set_baud_rate_no_wait(isp,COM_BAUD_RATE_MAXIMUM) # Jack up Baud rate
        isp.setBaudRate(COM_BAUD_RATE_MAXIMUM)         # Sets the HOST baud rate

    # issue enquiry command to check if SERAM is in Maintenance Mode
    mode = isp_get_maintenance_status(isp)
    isp_show_maintenance_mode(isp, mode)

    authenticate = True if not args.no_authentication else False

    items = imageList.split(' ')
    for e in range(1, len(items),2):
        addr = items[e]
        address = int(addr,base=16)
        fileName = items[e-1]
        fileName = fileName.replace('..\\','')

        burn_mram_isp(isp, handler, fileName, address, 
                      args.verbose, authenticate)

    # Restore the default Baud rate
    if dynamic_baud_rate_switch:
        isp_set_baud_rate_no_wait(isp,baud_rate)
        isp.setBaudRate(baud_rate) 

    isp_reset_no_wait(isp)

    isp.closeSerial()

if __name__ == "__main__":
    main()
