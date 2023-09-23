#!/usr/bin/python3

"""
   @brief OTP data decode - ALoif Manufacturing info
   - 256 Bits (32 bytes) of total data
     * CP1    72    9
     * CP2    72    9
   __author__ onyettr
"""
# pylint: disable=unused-argument, invalid-name, consider-using-f-string
import struct
from isp_print import isp_print_color

SRAM0_SIZE_lut = {
        0 : "4.0",
        1 : "2.0"
    }

SRAM1_SIZE_lut = {
        0 : "2.5",
        1 : "0.0"
    }

MRAM_SIZE_lut = {
        0 : "6.0",
        1 : "4.5",
        2 : "3.0",
        3 : "1.5"
    }

class CP_data_t:
    """
        OTP manufactoring data
        @todo need to add more methods
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self):
        """
            CP Fuses - 72bits
        """
        self.cp_mfgr_id_x_loc = 0
        self.cp_mfgr_id_y_loc = 0
        self.cp_mfgr_id_wfr_id = 0
        self.cp_mfgr_id_lot_id = 0
        self.cp_mfgr_id_lot_id_year = 0
        self.cp_mfgr_id_lot_id_FABID = 0
        self.cp_mfgr_id_lot_id_workweek = 0
        self.cp_mfgr_id_lot_id_serialno = 0
        self.cp_memory_sizes = 0
        self.cp_memory_sizes_SRAM0 = 0
        self.cp_memory_sizes_SRAM1 = 0
        self.cp_memory_sizes_MRAM = 0
        self.cp_test_revision = 0
        self.cp_test_revision_revision = 0
        self.cp_temperature = 0
        self.cp_last_byte = 0
        self.cp_CP1_write_ok = 0
        self.cp_SRAM_repaired = 0
        self.cp_future = 0

    def otp_manufacture_cp_fuses_decode(self, message):
        """
            otp_manufacture_cp_fuses_decode
                parse otp Mfgr data
        """

        if len(message) == 0:
            return

        # CP1 decode 72 Bits / 9 BYTES
        # Byte         Field description
        #   0        x-loc
        #   1        y-loc
        #   2        lot _id - 32 bits
        #     3      year
        #     4      FabId:2 Work Week: 6
        #     5      Serial No
        #     6        RAM Sizes SRAM0:1 SRAM1:1 MRAM:2 CP1 Bin#:4
        #   7        Test PrigramRev:4Temperature:4
        #   8        SRAM repaired:1 FUTURE:6
        (self.cp_mfgr_id_x_loc,) = struct.unpack("<B",bytes(message[0:1]))
        (self.cp_mfgr_id_y_loc,) = struct.unpack("<B",bytes(message[1:2]))
        (self.cp_mfgr_id_wfr_id,) = struct.unpack("<B",bytes(message[2:3]))
        (self.cp_mfgr_id_lot_id,) = struct.unpack("<I",bytes(message[3:7]))
        (self.cp_memory_sizes,) = struct.unpack("<B",bytes(message[6:7]))
        (self.cp_test_revision,) = struct.unpack("<B",bytes(message[7:8]))
        (self.cp_temperature,) = struct.unpack("<B",bytes(message[7:8]))
        (self.cp_last_byte,) = struct.unpack("<B",bytes(message[8:9]))

    def display_manufacture_otp_info(self):
        """
            display_display_manufacture_otp_info
                display otp data sent back from Target
        """
        isp_print_color('blue', "\t+ Mfgr id: x-loc  %x\n" %
                        (self.cp_mfgr_id_x_loc))
        isp_print_color('blue', "\t+ Mfgr id: y-loc  %x\n" %
                        (self.cp_mfgr_id_y_loc))
        isp_print_color('blue', "\t+ Mfgr id: Wfr_id %x\n" %
                        (self.cp_mfgr_id_wfr_id))
        isp_print_color('blue', "\t+ Mfgr id: lot_id %x\n" %
                        (self.cp_mfgr_id_lot_id))
        size_bit = self.cp_mfgr_id_lot_id & 0x1
        isp_print_color('blue', "\t+ SRAM0 Size      %s MB\n" % (
                        SRAM0_SIZE_lut.get(size_bit)))
        size_bit = self.cp_mfgr_id_lot_id & 0x2
        isp_print_color('blue', "\t+ SRAM1 Size      %s MB\n" % (
                        SRAM1_SIZE_lut.get(size_bit)))
        size_bit = (self.cp_mfgr_id_lot_id & 0xC) >> 2
        isp_print_color('blue', "\t+ MRAM  Size      %s MB\n" % (
                        MRAM_SIZE_lut.get(size_bit)))

def decode_otp_manufacture(message):
    """
        decode_otp_manufacture
            decode and display the OTP bits for manufatcuring
    """
    CP1_info = CP_data_t()
    CP2_info = CP_data_t()

    CP1_info.otp_manufacture_cp_fuses_decode(message)
    isp_print_color('blue', "CP1\n")
    CP1_info.display_manufacture_otp_info()

    CP2_info.otp_manufacture_cp_fuses_decode(message)
    isp_print_color('blue', "CP2\n")
    CP2_info.display_manufacture_otp_info()

if __name__ == "__main__":
    message = [ 0x1, 0x2, 0x3, 0x0, 0x0,
                0x1, 0x2, 0x3, 0x0, 0x0,
                0x1, 0x2, 0x3, 0x0, 0x0,
                0x1, 0x2, 0x3, 0x0, 0x0,
                0x1, 0x2, 0x3, 0x0, 0x0,
                0x1, 0x2, 0x3, 0x0, 0x0,
                0x1, 0x2, 0x3, 0x0, 0x0,
                0x1, 0x2, 0x3, 0x0, 0x0]
    decode_otp_manufacture(message)
