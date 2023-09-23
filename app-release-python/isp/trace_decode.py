"""
    trace buffer decoder (SEROM and SERAM)

     __author__ = "ronyett"
     __copyright__ = "ALIF Seminconductor"
     __version__ = "0.02.000"
     __status__ = "Dev"    "
"""
#!/usr/bin/env python3
#pylint: disable=invalid-name,superfluous-parens,anomalous-unicode-escape-in-string


TRACE_BASE_ADDRESS = 0
NUMBER_OF_TRACES   = 512 # SERAM Size = 0x200, 512 Words, 2K bytes

# Trace field encoding data
FLAG_MASK_SHIFT     = 0
SEQ_ID_MASK_SHIFT   = 2
MARKER_MASK_SHIFT   = 8
ADDR_MASK_SHIFT     = 16

FLAG_MASK           = (0x00000003)
SEQ_ID_MASK         = (0x000000FC)
MARKER_MASK         = (0x0000FF00)
ADDR_MASK           = (0xFFFF0000)
VOID_ENTRY          = (0xFFFFFFFF)

TRACE_FLAG_NO_DATA             =  0x00  # No data
TRACE_FLAG_BYTE_DATA           =  0x01  # Marker is 8 bit data
TRACE_FLAG_WORD_DATA           =  0x02  # Next entry is 32-bit data
TRACE_FLAG_TIMESTAMP           =  0x03  # Next entry is 32 bit TimeStamp

TRACE_BUFFER_END_MARKER        =  0xeeeeeeee 

#
# SEROM Trace Flags
#
TRACE_BEGIN_RESET              =  0x1
TRACE_SE_FIREWALL              =  0x2
TRACE_HOST_FIREWALL            =  0x3
TRACE_FIREWALL_CTRL_READY      =  0x4
TRACE_FIREWALLS_INITIALIZED    =  0x5
TRACE_LCS_INITIALIZATIONS      =  0x6
TRACE_LCS_CM                   =  0x7 #lcs=0
TRACE_LCS_DM                   =  0x8 #lcs=1
TRACE_LCS_UNKNOWN_1            =  0x9 #lcs=2
TRACE_LCS_UNKNOWN_2            =  0xA #lcs=3
TRACE_LCS_UNKNOWN_3            =  0xB #lcs=4
TRACE_LCS_SE                   =  0xC #lcs=5
TRACE_LCS_UNKNOWN_4            =  0xD #lcs=6
TRACE_LCS_RMA                  =  0xE #lcs=7
TRACE_BEGIN_MAIN               =  0xF
TRACE_FIND_STOC                =  0x10
TRACE_LOCATE_CERT_CHAIN        =  0x11
TRACE_RAW_BYPASS_CHECK         =  0x12
TRACE_RAW_BYPASS               =  0x13
TRACE_VERIFY_CERT_CHAIN        =  0x14
TRACE_SRAM_RETAINED            =  0x15
TRACE_SECURE_LCS_BOOT          =  0x16
TRACE_WAKE_UP_BROWNOUT         =  0x17
TRACE_START_CM55_HE            =  0x18
TRACE_CERT_CHAIN_VERIFY_START  =  0x19
TRACE_EACH_CERT_VERIFY         =  0x1A
TRACE_CERT_CHAIN_VERIFY_END    =  0x1B
TRACE_SERAM_JUMP               =  0x1C
TRACE_PROCESS_ERROR            =  0x1D
TRACE_CERTIFICATE_ERROR        =  0x1E
TRACE_CM55_HE_FORCE_COLD_BOOT  =  0x1F
TRACE_CLEAR_FIRST_BOOT_MRAM_WRITE_FAIL             = 0x20
TRACE_MARK_BANK_NOT_VALID_MRAM_WRITE_FAIL          = 0x21
TRACE_SET_IMAGE_BOOTED_MRAM_WRITE_FAIL             = 0x22
TRACE_UPDATE_ERROR_CODES_MRAM_WRITE_FAIL           = 0x23
TRACE_UPDATE_BOOTFLAGS_CHECKSUM_MRAM_WRITE_FAIL    = 0x24
TRACE_BANK_A_NOT_BOOTABLE                          = 0x25
TRACE_BANK_B_NOT_BOOTABLE                          = 0x26
TRACE_NEWER_BANK_A                                 = 0x27
TRACE_NEWER_BANK_B                                 = 0x28
TRACE_TOC1_SERAM_OFFSET_INVALID                    = 0x29
TRACE_TOC2_SERAM_OFFSET_INVALID                    = 0x2A
TRACE_TOC1_EXTENSION_HEADER_INVALID                = 0x2B
TRACE_TOC2_EXTENSION_HEADER_INVALID                = 0x2C
TRACE_TOC1_BOOT_FLAGS_CHECKSUM_INVALID             = 0x2D
TRACE_TOC2_BOOT_FLAGS_CHECKSUM_INVALID             = 0x2E
TRACE_BANK_A_BOOT_FAILED                           = 0x2F
TRACE_BANK_B_BOOT_FAILED                           = 0x30
TRACE_WAKE_UP_RESET                                = 0x31
TRACE_LOAD_MSP_ADDRESS                             = 0x32
TRACE_LOAD_JUMP_ADDRESS                            = 0x33
TRACE_DEFAULT_TOC_OFFSET                           = 0x34
TRACE_CM55_HE_CPU_WAIT_RELEASE                     = 0x35
TRACE_PROCESS_ERROR_EXTENDED                       = 0x36
TRACE_FAST_BOOT_FIREWALL_PROTECT                   = 0x37
TRACE_BEGIN_CGU_CLOCK_CONFIGURATION                = 0x38
TRACE_CGU_CLOCKS_CONFIGURED                        = 0x39
TRACE_MRAM_RESET_ERROR_BYPASS                      = 0x3A
TRACE_MRAM_SET_ERROR_BYPASS                        = 0x3B
TRACE_BAD_SERAM_JUMP_ADDRESS                       = 0x3C
TRACE_BOOT_LOADER_JUMP_RETURNED                    = 0x3D
TRACE_TURN_ON_SYSTEM_POWER                         = 0x3E
TRACE_SERAM_RETENTION_PATTERN                      = 0x3F

#
# SERAM Trace Flags
#
TRACE_FIREWALL_STATIC_CONFIG_BEGIN                 = 0x40
TRACE_FIREWALL_STATIC_CONFIG_END                   = 0x41
TRACE_PLL_INIT_BEGIN                               = 0x42
TRACE_PLL_INIT_END                                 = 0x43
TRACE_MAINTENANCE_MODE_DETECT_BEGIN                = 0x44
TRACE_MAINTENANCE_MODE_DETECT_END                  = 0x45
TRACE_CC_LIB_INIT_BEGIN                            = 0x46
TRACE_CC_LIB_INIT_END                              = 0x47
TRACE_M55_HE_TCM_INIT_BEGIN                        = 0x48
TRACE_M55_HE_TCM_INIT_END                          = 0x49
TRACE_STOC_PROCESS_BEGIN                           = 0x50
TRACE_ATOC_PROCESS_BEGIN                           = 0x51
TRACE_TOC_PROCESS_END                              = 0x52
TRACE_TOC_PRINT_BEGIN                              = 0x53
TRACE_TOC_PRINT_END                                = 0x54
TRACE_BANK_MAINTENANCE_BEGIN                       = 0x55
TRACE_BANK_MAINTENANCE_END                         = 0x56
TRACE_CPU_RELEASE                                  = 0x57
TRACE_CPU_BOOT                                     = 0x58
TRACE_WAKE_UP                                      = 0x59
TRACE_COLD_BOOT                                    = 0x5A
TRACE_M55_FASTBOOT_SERAM                           = 0x5B
TRACE_M55_TCM_RETAINED                             = 0x5C
TRACE_M55_VTOR_SENTINEL                            = 0x5D
TRACE_STOP_MODE_ENABLE                             = 0x5E

TRACE_RTOS_WFI_BEGIN                               = 0x60
TRACE_RTOS_WFI_END                                 = 0x61

TRACE_DEBUG_0                                      = 0x62
TRACE_DEBUG_1                                      = 0x63
TRACE_ENTER_MAINTENANCE_MODE                       = 0x64
TRACE_DCU_CONFIG_BEGIN                             = 0x65
TRACE_DCU_CONFIG_END                               = 0x66

TRACE_BEGIN_SERAM_BANK_COPY                        = 0x70
TRACE_END_SERAM_BANK_COPY                          = 0x71
TRACE_M55_FASTBOOT_SERAM_XIP                       = 0x72
TRACE_WARM_BOOT                                    = 0x73
TRACE_A32_0_RELEASED                               = 0x74
TRACE_A32_1_RELEASED                               = 0x75
TRACE_M55_HP_RELEASED                              = 0x76
TRACE_M55_HE_RELEASED                              = 0x77
TRACE_MODEM_RELEASED                               = 0x78
TRACE_GNSS_RELEASED                                = 0x79
TRACE_DSP_RELEASED                                 = 0x7A

TRACE_SERAM_BOOT_COMPLETE                          = 0x80
TRACE_SERAM_BOOT_ERROR                             = 0x81
TRACE_SERAM_OS_ERROR                               = 0x82

# Marker trace translation
marker_lookup = {
    TRACE_BEGIN_RESET                              : 'Begin Reset_Handler',
    TRACE_SE_FIREWALL                              : 'SE Firewall configuration',
    TRACE_HOST_FIREWALL                            : 'HOST Firewall configuration',
    TRACE_FIREWALL_CTRL_READY                      : 'Firewall controller ready',
    TRACE_FIREWALLS_INITIALIZED                    : 'Firewall initialized',
    TRACE_LCS_INITIALIZATIONS                      : 'Begin CC312 initializations',
    TRACE_LCS_CM                                   : 'LCS = 0 -> CM',
    TRACE_LCS_DM                                   : 'LCS = 1 -> DM',
    TRACE_LCS_UNKNOWN_1                            : 'LCS = 2 -> UNKNOWN_1',
    TRACE_LCS_UNKNOWN_2                            : 'LCS = 3 -> UNKNOWN_2',
    TRACE_LCS_UNKNOWN_3                            : 'LCS = 4 -> UNKNOWN_3',
    TRACE_LCS_SE                                   : 'LCS = SE',
    TRACE_LCS_UNKNOWN_4                            : 'LCS = 6 -> UNKNOWN_4',
    TRACE_LCS_RMA                                  : 'LCS = RMA',
    TRACE_BEGIN_MAIN                               : 'Begin Main',
    TRACE_FIND_STOC                                : 'Find STOC in MRAM',
    TRACE_LOCATE_CERT_CHAIN                        : 'Locate certificate chain',
    TRACE_RAW_BYPASS_CHECK                         : 'Raw Bypass check',
    TRACE_RAW_BYPASS                               : 'Raw Bypass method invoked',
    TRACE_VERIFY_CERT_CHAIN                        : 'Verify certificate chain',
    TRACE_SRAM_RETAINED                            : 'SRAM retained',
    TRACE_SECURE_LCS_BOOT                          : 'SECURE LCS Cold Boot',
    TRACE_WAKE_UP_BROWNOUT                         : 'Brownout detected',
    TRACE_START_CM55_HE                            : 'Fast Boot Start CM55_HE',
    TRACE_CERT_CHAIN_VERIFY_START                  : 'Begin certificate chain verification',
    TRACE_EACH_CERT_VERIFY                         : 'Verify each certificate',
    TRACE_CERT_CHAIN_VERIFY_END                    : 'End certificate chain verification',
    TRACE_SERAM_JUMP                               : 'Jump to SERAM',
    TRACE_PROCESS_ERROR                            : 'SEROM Error Detected',
    TRACE_CERTIFICATE_ERROR                        : 'Certificate Processing Error Detected',
    TRACE_CM55_HE_FORCE_COLD_BOOT                  : 'Force CM55-HE cold boot',
    TRACE_CLEAR_FIRST_BOOT_MRAM_WRITE_FAIL         : 'Clear boot flag MRAM write failed',
    TRACE_MARK_BANK_NOT_VALID_MRAM_WRITE_FAIL      : 'Mark Bank not valid MRAM write failed',
    TRACE_SET_IMAGE_BOOTED_MRAM_WRITE_FAIL         : 'Set Image Booted Flag in MRAM failed',
    TRACE_UPDATE_ERROR_CODES_MRAM_WRITE_FAIL       : 'Update Error Codes in MRAM failed',
    TRACE_UPDATE_BOOTFLAGS_CHECKSUM_MRAM_WRITE_FAIL: 'Update Boot Flags Checksum in MRAM failed',
    TRACE_BANK_A_NOT_BOOTABLE                      : 'Bank A not bootable',
    TRACE_BANK_B_NOT_BOOTABLE                      : 'Bank B not bootable',
    TRACE_NEWER_BANK_A                             : 'Bank A is newer',
    TRACE_NEWER_BANK_B                             : 'Bank B is newer',
    TRACE_TOC1_SERAM_OFFSET_INVALID                : 'TOC1 SERAM Offset invalid',
    TRACE_TOC2_SERAM_OFFSET_INVALID                : 'TOC2 SERAM Offset invalid',
    TRACE_TOC1_EXTENSION_HEADER_INVALID            : 'TOC1 Extension Header invalid',
    TRACE_TOC2_EXTENSION_HEADER_INVALID            : 'TOC2 Extension Header invalid',
    TRACE_TOC1_BOOT_FLAGS_CHECKSUM_INVALID         : 'TOC1 Boot Flags Checksum invalid',
    TRACE_TOC2_BOOT_FLAGS_CHECKSUM_INVALID         : 'TOC2 Boot Flags Checksum invalid',
    TRACE_BANK_A_BOOT_FAILED                       : 'BANK A boot failed',
    TRACE_BANK_B_BOOT_FAILED                       : 'BANK B boot failed',
    TRACE_WAKE_UP_RESET                            : 'SOC reset was triggered',
    TRACE_LOAD_MSP_ADDRESS                         : 'Load MSP Address',
    TRACE_LOAD_JUMP_ADDRESS                        : 'Load JUMP Address',
    TRACE_DEFAULT_TOC_OFFSET                       : 'Default Alif TOC offset set',
    TRACE_CM55_HE_CPU_WAIT_RELEASE                 : 'CM55 HE CPU wait release',
    TRACE_PROCESS_ERROR_EXTENDED                   : 'SEROM Error Detected - extended error',
    TRACE_FAST_BOOT_FIREWALL_PROTECT               : 'FAST BOOT configure firewall protection',
    TRACE_BEGIN_CGU_CLOCK_CONFIGURATION            : 'Begin CGU clock configuration',
    TRACE_CGU_CLOCKS_CONFIGURED                    : 'CGU clock configuration complete',
    TRACE_MRAM_RESET_ERROR_BYPASS                  : 'Enable MRAM ECC Error Interrupts',
    TRACE_MRAM_SET_ERROR_BYPASS                    : 'Disable MRAM ECC Error Interrupts',
    TRACE_BAD_SERAM_JUMP_ADDRESS                   : 'Bad SERAM Jump Address',
    TRACE_BOOT_LOADER_JUMP_RETURNED                : 'Boot Loader Jump Returned',
    TRACE_TURN_ON_SYSTEM_POWER                     : 'Turn On System Power',
    TRACE_SERAM_RETENTION_PATTERN                  : 'SERAM retention pattern detected',
    TRACE_FIREWALL_STATIC_CONFIG_BEGIN             : 'Firewall Static BEGIN',
    TRACE_FIREWALL_STATIC_CONFIG_END               : 'Firewall Static END  ',
    TRACE_PLL_INIT_BEGIN                           : 'PLL BEGIN',
    TRACE_PLL_INIT_END                             : 'PLL END',
    TRACE_MAINTENANCE_MODE_DETECT_BEGIN            : 'Maintenance Detection BEGIN',
    TRACE_MAINTENANCE_MODE_DETECT_END              : 'Maintenance Detection END',
    TRACE_CC_LIB_INIT_BEGIN                        : 'CC Lib BEGIN',
    TRACE_CC_LIB_INIT_END                          : 'CC Lib END',
    TRACE_M55_HE_TCM_INIT_BEGIN                    : 'M55 HE TCM Init BEGIN',
    TRACE_M55_HE_TCM_INIT_END                      : 'M55 HE TCM Init END',
    TRACE_STOC_PROCESS_BEGIN                       : 'STOC Process BEGIN',
    TRACE_ATOC_PROCESS_BEGIN                       : 'ATOC Process BEGIN',
    TRACE_TOC_PROCESS_END                          : 'TOC Process END',
    TRACE_TOC_PRINT_BEGIN                          : 'TOC Print BEGIN',
    TRACE_TOC_PRINT_END                            : 'TOC Print END',
    TRACE_BANK_MAINTENANCE_BEGIN                   : 'BANK Maintenance BEGIN',
    TRACE_BANK_MAINTENANCE_END                     : 'BANK Maintenance END',
    TRACE_CPU_RELEASE                              : 'CPU release',
    TRACE_CPU_BOOT                                 : 'CPU boot',
    TRACE_WAKE_UP                                  : 'Wake up',
    TRACE_COLD_BOOT                                : 'Cold boot',
    TRACE_M55_FASTBOOT_SERAM                       : 'M55 fast boot by SERAM',
    TRACE_M55_TCM_RETAINED                         : 'M55 TCM was retained',
    TRACE_M55_VTOR_SENTINEL                        : 'M55 VTOR SENTINEL detected',
    TRACE_STOP_MODE_ENABLE                         : 'Stop mode enabled',
    TRACE_RTOS_WFI_BEGIN                           : 'RTOS Wfi BEGIN',
    TRACE_RTOS_WFI_END                             : 'RTOS Wfi END',
    TRACE_DEBUG_0                                  : 'Debug 0',
    TRACE_DEBUG_1                                  : 'Debug 1',
    TRACE_ENTER_MAINTENANCE_MODE                   : 'Enter maintenance mode',
    TRACE_DCU_CONFIG_BEGIN                         : 'Begin DCU configuration',
    TRACE_DCU_CONFIG_END                           : 'Finish DCU configuration',
    TRACE_BEGIN_SERAM_BANK_COPY                    : 'SERAM bank copy BEGIN',
    TRACE_END_SERAM_BANK_COPY                      : 'SERAM bank copy END',
    TRACE_M55_FASTBOOT_SERAM_XIP                   : 'M55 XIP fast boot by SERAM',
    TRACE_WARM_BOOT                                : 'Warm boot',
    TRACE_A32_0_RELEASED                           : 'A32_0 released',
    TRACE_A32_1_RELEASED                           : 'A32_1 released',
    TRACE_M55_HP_RELEASED                          : 'M55_HP released',
    TRACE_M55_HE_RELEASED                          : 'M55_HE released',
    TRACE_MODEM_RELEASED                           : 'M55 MODEM released',
    TRACE_GNSS_RELEASED                            : 'M55 GNSS released',
    TRACE_DSP_RELEASED                             : 'DSP released',
    TRACE_SERAM_BOOT_COMPLETE                      : 'SERAM boot complete',
    TRACE_SERAM_BOOT_ERROR                         : 'SERAM boot error',
    TRACE_SERAM_OS_ERROR                           : 'SERAM operating system boot error'
}

def readMemory32(address,offset):
    """
        return an integer from byte list provided
    """
    return int.from_bytes([address[offset+0],
                           address[offset+1],
                           address[offset+2],
                           address[offset+3]],"little")

def trace_find_marker(marker_value, buffer):
    """
        look for the Trace end marker in the trace buffer
        @todo should look for the full 32-bits of the marker
    """
    marker_found = False
    position = 0

    if marker_value in buffer:
        marker_found = True
        position = buffer.index(marker_value)

    return marker_found, position

def trace_find_end_marker(end_marker_value, trace_buffer):
    """
        look for the Trace end marker in the trace buffer
        @todo should look for the full 32-bits of the marker
    """
    marker_found = False
    position = 0

    for each_trace_item in range(0,NUMBER_OF_TRACES+4,4):
        trace_word = readMemory32(trace_buffer,
                                  each_trace_item)
#        print("[{0:08x}] {1:8x}".format(trace_word,end_marker_value))
        if trace_word == end_marker_value :
            marker_found = True
            position = each_trace_item
            break
    return marker_found, position

def trace_buffer_decode(trace_buffer):
    """
        trace_buffer_decode
            based on the JYTHON code from ARM-DS

        Instead of using actual memory addresses, it is using an array passed

    """
    print("*** SERAM Trace Buffer decode ***")

#    print("[DEBUG] trace_buffer_len %d Marker Pos %d\n" % (
#        len(trace_buffer),
#        trace_buffer.index(0xee)))

    # Look for the end of trace marker
    marker_found, end_of_trace = trace_find_end_marker(TRACE_BUFFER_END_MARKER,
                                                       trace_buffer)
    if not marker_found:
        print("[ERROR] No end of trace marker was found")
        return

    # trace vars structure is at the end of the trace buffer
    # header start
    trace_vars_address = end_of_trace - 4

    trace_vars_p = readMemory32(trace_buffer, trace_vars_address)
    print("*** Trace Header ***")
    print("[{0:08d}] {1:8x}".format(trace_vars_address,trace_vars_p))

    trace_total = trace_vars_p >> 16
    trace_total = min(trace_total, NUMBER_OF_TRACES)

    trace_vars_address += 4
    trace_vars_p = trace_buffer[trace_vars_address]
    print("[%08d] %8x" %(trace_vars_address,
                         readMemory32(trace_buffer,trace_vars_address)))
    print("trace_total = %d" %(trace_total))
    print("********************")

    # Decode the trace buffer
    print("  Address      Seq#      LR                   Trace Marker                           Marker Data")

    word_offset = 0

    while trace_total > 0:
        variable_enabled = False
        read_address = TRACE_BASE_ADDRESS + word_offset
        trace_item = readMemory32(trace_buffer,read_address)
        if trace_item == VOID_ENTRY:
            print("  XXXXXXXX")
        else:
            flag   = (trace_item & FLAG_MASK)   >> FLAG_MASK_SHIFT
            seq_id = (trace_item & SEQ_ID_MASK) >> SEQ_ID_MASK_SHIFT
            addr   = (trace_item & ADDR_MASK)   >> ADDR_MASK_SHIFT
            marker = (trace_item & MARKER_MASK) >> MARKER_MASK_SHIFT

            if TRACE_FLAG_WORD_DATA == flag:
                read_address = TRACE_BASE_ADDRESS + word_offset
                # second 32-bit word is data we need, advance the word_offset
                word_offset = word_offset + 4
                word_data_address = TRACE_BASE_ADDRESS + word_offset
                word_data = readMemory32(trace_buffer,word_data_address)

#                print("word_offset = %x" %(word_offset))
#                print("trace_item = %x" %(trace_item))
#                print("flag = %x" %(flag))
#                print("marker = %x" %(marker))
#                print("read_address = %x" %(read_address))

                if marker in marker_lookup:
                    marker_string = marker_lookup[marker]
                    if marker_string is None:
                        marker_string = "MARKER?"
                    variable_enabled = False
                else:
                    variable_enabled = True
                marker = (trace_item & MARKER_MASK) >> MARKER_MASK
#          print("[%08x] %2d    %8X   %4X      %2X" %(read_address,
#                                                      seq_id,
#                                                      trace_item,
#                                                      addr,
#                                                      marker))
#          print("variable_enabled = %d" %(variable_enabled))
                if variable_enabled is True:
                    print("[%08x]     %2d      0x%04X       %8X                       0x%08X" %(read_address,
                          seq_id,
                          addr,
                          trace_item,
                          word_data))
                else:
                    print("[%08x]     %2d      0x%04X       %-45s    0x%08X" %(read_address,
                          seq_id,
                          addr,
                          marker_string,
                          word_data))
            elif TRACE_FLAG_TIMESTAMP == flag:
                # second 32-bit word is time stamp, advance the word_offset
                word_offset = word_offset + 4
                read_address = TRACE_BASE_ADDRESS + word_offset
                trace_item_dword = readMemory32(trace_buffer,read_address)

                if marker in marker_lookup:
                    marker_string = marker_lookup[marker]
                    if marker_string is None:
                        marker_string = "MARKER?"
                    variable_enabled = False
                else:
                    variable_enabled = True
                print("[%08x]     %2d      0x%04X       %-45s    T:%8d" %(
                      read_address,
                      seq_id,
                      addr,
                      marker_string,
                      trace_item_dword))
            elif TRACE_FLAG_BYTE_DATA == flag:
                if marker in marker_lookup:
                    marker_string = marker_lookup[marker]
                    if marker_string is None:
                        marker_string = "MARKER?"
                    variable_enabled = False
                else:
                    variable_enabled = True

                if variable_enabled is True:
                    print("[%08x]     %2d      0x%04X       %2X"               %(read_address,
                           seq_id,
                           addr,
                           marker))
                else:
                    print("[%08x]     %2d      0x%04X       %-45s" %(read_address,
                           seq_id,
                           addr,
                           marker_string))
            else:
                print("[%08x]     %2d      %8X           0x%04X        %2X" %(read_address,
                      seq_id,
                      trace_item,
                      addr,
                      marker))
        word_offset = word_offset + 4
        trace_total = trace_total - 1

#        if word_offset >= (NUMBER_OF_TRACES * 4):
        if word_offset >= (NUMBER_OF_TRACES):
            break
