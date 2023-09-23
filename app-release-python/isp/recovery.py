#!/usr/bin/env python3
"""
    recovery.py

    Support
        - SEROM Recovery mode
        - Allows updating of the MRAM through SEROM
        - This is always ISP mode.
    __author__ = ""
    __copyright__ = "ALIF Seminconductor"
    __version__ = "0.1.0"
    __status__ = "Dev"

    TODO:
    - baud rate should be set to the SEROM default
"""
# pylint: disable=unused-argument, invalid-name, bare-except
import sys
sys.path.append("./isp")
from isp_protocol import *
from isp_core import *
from isp_util import *
import utils.config
from utils.config import *
from utils.user_validations import validateArgList
import device_probe
import time

# Probe error codes
PROBE_OK        = 0
PROBE_SEROM     = 1
PROBE_SERAM     = 2
PROBE_NO_MESSAGE= 3

EXIT_WITH_ERROR = 1

def burn_mram_isp(isp, fileName, destAddress, verbose_display):
    """
        burn_mram_isp - use ISP method to write MRAM
    """
    try:
        f = open(fileName, 'rb')
    except IOError as e:
        print('[ERROR] {0}'.format(e))
        sys.exit(EXIT_WITH_ERROR)
    with f:
        fileSize = file_get_size(f)
#        print("FILESIZE = %d" %fileSize)

        # SEROM Recovery uses an Offset rather than an address
        MRAM_BASE_ADDRESS = utils.config.MRAM_BASE_ADDRESS
        offset = 0
        data_size = 16
        writeAddress = int(destAddress,base=16) - MRAM_BASE_ADDRESS

#        print("Actual offset = ", hex(writeAddress))
        number_of_blocks = fileSize // data_size
        left_over_blocks = fileSize % data_size

        start_time = time.time()
        while number_of_blocks != 0:
            f.seek(offset)
            mram_line = f.read(data_size)

            if verbose_display is False:
                progress_bar(fileName,offset+data_size,fileSize)
            message = isp_mram_write_no_wait(isp,writeAddress,mram_line)

            number_of_blocks = number_of_blocks - 1
            offset = offset + data_size
            writeAddress = writeAddress + data_size # increment by 16
            if isp.CTRLCHandler.Handler_exit():
                print("[INFO] CTRL-C")
                break

        if number_of_blocks == 0:
            if left_over_blocks != 0:
                f.seek(offset)
                mram_line = f.read(left_over_blocks)
                print("leftovers!")
                if verbose_display is False:
                    progress_bar(fileName,offset+left_over_blocks,fileSize)
        end_time = time.time()
        print("\r")

        if verbose_display is False:
            print("[INFO] recovery time {:10.2f} seconds".format(end_time-start_time))

    f.close()

def recovery_action(isp):
    """
        Recover MRAM via SEROM
    """
    # memory defines for Alif/OEM MRAM Addresses and Sizes
    load_global_config()
    DEVICE_PART_NUMBER = utils.config.DEVICE_PART_NUMBER
    DEVICE_REVISION = utils.config.DEVICE_REVISION
    DEVICE_PACKAGE = utils.config.DEVICE_PACKAGE
    DEVICE_REV_PACKAGE_EXT = utils.config.DEVICE_REV_PACKAGE_EXT
    DEVICE_OFFSET  = utils.config.DEVICE_OFFSET    
    MRAM_BASE_ADDRESS = utils.config.MRAM_BASE_ADDRESS
    ALIF_BASE_ADDRESS = utils.config.ALIF_BASE_ADDRESS
    MRAM_SIZE = utils.config.MRAM_SIZE

    # this check below should be removed as soon as we deprecate
    # REV_A1, because in the future we might have other parts with REV_A1
    # that might not need this hack!
    # improvement: we should actually test the SEROM version to base
    # this decisions upon...
    if DEVICE_REVISION != 'A1':
        # probe the device before update
        device = device_probe.device_get_attributes(isp)
        # check SERAM is the bootloader stage
        print('Bootloader stage: ' + device_probe.STAGE_TEXT[device.stage])
        if device.stage == device_probe.STAGE_SERAM:
            print('[ERROR] Device not in Recovery mode, use systemUpdatePackage Tool')
#            sys.exit(EXIT_WITH_ERROR)
            return
        #print('Device Part#: ' + device.part_number)
        print('Device Revision: ' + device.revision)
        if device.revision != DEVICE_REVISION:
            print("[ERROR] Target device revision (%s) mismatch with configured device (%s)"
                % (device.revision,DEVICE_REVISION))
            sys.exit(EXIT_WITH_ERROR)


    # Start the recovery process
    print('[INFO] System TOC Recovery with parameters:')
    print('- Device Part# ' + DEVICE_PART_NUMBER + ' - Rev: ' + DEVICE_REVISION)
    print('- MRAM Base Address: ' + hex(ALIF_BASE_ADDRESS))

    argList = ''
    action = 'Burning: '

#    argList = '../alif/SystemPackage.bin ' + hex(ALIF_BASE_ADDRESS) + \
#              ' ../alif/offset.bin ' + hex(MRAM_BASE_ADDRESS + MRAM_SIZE - 16)

    rev_ext = DEVICE_REV_PACKAGE_EXT[DEVICE_REVISION]
    alif_image = 'alif/' + DEVICE_PACKAGE + '-' + rev_ext + '.bin'
    alif_offset = 'alif/' + DEVICE_OFFSET + '-' + rev_ext + '.bin'

    argList = '../' + alif_image + ' ' + hex(ALIF_BASE_ADDRESS) + \
              ' ../' + alif_offset + ' ' + hex(MRAM_BASE_ADDRESS + MRAM_SIZE - 16)      

    # validate all parameters
    argList = validateArgList(action, argList.strip())
    if sys.platform == "linux":
        argList = argList.replace('../','')
    else:
        argList = argList.replace('/','\\')

    items = argList.split(' ')

    for e in range(1, len(items),2):
        addr = items[e]
        fileName = items[e-1]
        fileName = fileName.replace('..\\','')

        burn_mram_isp(isp, fileName, addr, False)

    print("[INFO] Target reset")
    isp_reset_no_wait(isp)      # Reset the target
