
# pylint: disable=unused-argument, invalid-name
"""
    isp_util.py - commonly used functions used by ISP

    mainly used to support ISP based MRAM burning utlties.
"""
import os
import sys
import subprocess
import random
from isp_core import *
from utils.toc_common import *
import time

DATA_CHUNK_SIZE = 240

def file_get_size(fileHandle):
    """
        file_get_zsize - given a file handle return the size in bytes
    """
    fileHandle.seek(0,os.SEEK_END)
    sizeinbytes = fileHandle.tell()

    return sizeinbytes

def progress_bar(fileName, currentSize=0, maxSize=0, enablePrint=True):
    """
        progress_bar - print a progress bar
    """
    if maxSize <= 0:
        print("\n")
        return False

    progress  = int((currentSize / float(maxSize)) * 100)

    hashes   = int(progress / 5)
    printBar = (fileName.ljust(32) + "[" + "#" * hashes + " " * (20 - hashes)
                + "]")
    if enablePrint:
        progressVal = "%d%%: %d/%d bytes"%(progress, currentSize, maxSize)
    else:
        progressVal = " "

    print(printBar + progressVal + "\r", flush=True, end='')

#    if progress >= 100:
#       print("\n")

    return True

def checkArmdbgPath():
    """
        checkArmdbgPath
    """
    cmd = 'armdbg -v'
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         shell=True, universal_newlines=True)
    output, errors = p.communicate()
    #print(errors.find("'armdbg' is not recognized as an internal"))
    if errors.find("'armdbg' is not recognized as an internal") != -1:
        print('ERROR: The ARM Debugger is not found!')
        print('Be sure you are using ARM DS Command prompt')
        print('or add the <ARM DS install directory>/bin')
        print('directory to your PATH environmental variable')
        sys.exit(1)
    else:
        print('Invoking ARM Debugger: ' + output)

def download_file(isp, filename, chunkSize):
    """
        download_file
    """
    try:
        f = open(filename, 'rb')
    except IOError as e:
        print('[ERROR] {0}'.format(e))
        sys.exit()
    with f:
        fileSize = getFilesize(f)
        offset = 0

        while offset < fileSize:
            f.seek(offset)
            data_line = f.read(chunkSize)
            if isp_download_data_no_wait(isp, data_line) == False:
                break
            offset = offset + chunkSize

    f.close()

def send_authentication_command(isp, command, token):
    """
        send_authenitication_packet
    """
    cmd_packet = [0x03, command]          # authenticate execute
    cmd_packet = cmd_packet + list(int_to_bytes(token))
    cmd_packet[0] = len(cmd_packet) + 1
    cmd_packet = isp.checkSum(cmd_packet)  # add the checksum packet

    isp.writeSerial(bytearray(cmd_packet))
    isp_decode_packet(isp,"TX--> ", cmd_packet)
    #isp_wait(isp)
    message = isp_readmessage(isp)
    isp_decode_packet(isp,"RX<-- ", message)

certPath = Path("cert/")
imagePath = Path("build/images")

def authenticate_image(isp, fileName):
    """
        authenticate)image
    """
    signatureFileName = fileName + '.sign'
    print("Signature File: ", signatureFileName)

    # generate a random authentication token
    token = random.randrange(0xFFFFFFFF)
    print("Auth Token: ", hex(token))

    print("Verify Image")
    send_authentication_command(isp, ISP_COMMAND_VERIFY_IMAGE, token)
    download_file(isp, signatureFileName, DATA_CHUNK_SIZE)
    isp_download_done_no_wait(isp)

    return token

def burn_mram_isp(isp, handler, fileName, destAddress, verbose_display, auth_image):
    """
        burn_mram_isp - use ISP method to write MRAM
    """
    try:
        f = open(fileName, 'rb')
    except IOError as e:
        print('[ERROR] {0}'.format(e))
        sys.exit(1)

    print("Authenticate Image: ", auth_image)

    with f:
        fileSize = file_get_size(f)
        offset = 0
        data_size = DATA_CHUNK_SIZE
        if fileSize <= data_size:  # Deal with small ones
            data_size = 16         # CHUNK_SIZE

        token = 0x0
        if auth_image:
            token = authenticate_image(isp, fileName)

        isp_burn_mram_no_wait(isp, destAddress, fileSize, token)

        number_of_blocks = fileSize // data_size
        left_over_blocks = fileSize % data_size

        start_time = time.time()
        while number_of_blocks != 0:
            f.seek(offset)
            data_line = f.read(data_size)

            if verbose_display is False:
                progress_bar(fileName,offset+data_size,fileSize)

            if isp_download_data_no_wait(isp, data_line) == False:
                break

            offset = offset + data_size
            number_of_blocks = number_of_blocks - 1

            if handler.Handler_exit():
                print("[INFO] CTRL-C")
                break

        if number_of_blocks == 0:
            if left_over_blocks != 0:
                f.seek(offset)
                mram_line = f.read(left_over_blocks)
                isp_download_data_no_wait(isp, mram_line)

                if verbose_display is False:
                    progress_bar(fileName,offset+left_over_blocks,fileSize)
        end_time = time.time()

        isp_download_done_no_wait(isp)
        print("\r")
        print("{:10.2f} seconds".format(end_time-start_time))
    f.close()

def put_target_in_maintenance_mode(isp, baud_rate, Info=True):
    """
        enable target to be maintenance mode
        Info parameter toggles the output here
    """
    if Info:
        print("[INFO] Starting Maintenance Mode entry sequence...")
    isp_start_no_wait(isp)
    if Info:
        print("--> Set Maintenance Flag")
    isp_set_maintenance_flag_no_wait(isp)
    isp_stop_no_wait(isp)
    if Info:
        print("--> Reset Target")
    isp_reset_no_wait(isp)
    if Info:
        print("--> Close Serial Port")
    isp.closeSerial()
    if Info:
        print("--> Open Serial Port")
    isp.openSerial()
    if Info:
        print("--> Set Baud Rate")
    isp.setBaudRate(baud_rate)
    if Info:
        print("[INFO] Done. Target is in Maintenance Mode")
