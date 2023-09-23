#!/usr/bin/python3
"""
   @brief Clock Info decode and display

   __author__ onyettr
"""
# pylint: disable=unused-argument, invalid-name, consider-using-f-string
import struct
from isp_print import isp_print_color

PLL_CLK_STATUS_XTAL_STARTED       = (1 << 0)
PLL_CLK_STATUS_PLL_STATRTED       = (1 << 1)
PLL_CLK_STATUS_PLL_LOCKED         = (1 << 3)
PLL_CLK_STATUS_SWITCH_OSC_TO_XTAL = (1 << 4)
PLL_CLK_STATUS_SWITCH_OSC         = (1 << 5)
PLL_CLK_STATUS_SWITCH_PLL         = (1 << 6)

PLL_TARGET_SYSREFCLK              = 0
PLL_TARGET_SYSCLK                 = 1
PLL_TARGET_UART                   = 2
PLL_TARGET_ES0                    = 3
PLL_TARGET_ES1                    = 4
PLL_TARGET_SECENC                 = 5

PLL_SOURCE_PLL                    = 0
PLL_SOURCE_OSC                    = 1

OSCILLATOR_SOURCE_RC              = 0
OSCILLATOR_SOURCE_XTAL            = 1

OSCILLATOR_TARGET_SYS_CLOCKS      = 0
OSCILLATOR_TARGET_PERIPH_CLOCKS   = 1
OSCILLATOR_TARGET_S32K_CLOCK      = 2

CLOCK_FREQUENCY_800MHZ            = 0
CLOCK_FREQUENCY_400MHZ            = 1
CLOCK_FREQUENCY_300MHZ            = 2
CLOCK_FREQUENCY_200MHZ            = 3
CLOCK_FREQUENCY_160MHZ            = 4
CLOCK_FREQUENCY_120MHZ            = 5
CLOCK_FREQUENCY_80MHZ             = 6
CLOCK_FREQUENCY_60MHZ             = 7
CLOCK_FREQUENCY_100MHZ            = 8
CLOCK_FREQUENCY_50MHZ             = 9
CLOCK_FREQUENCY_20MHZ             = 10
CLOCK_FREQUENCY_10MHZ             = 11
CLOCK_FREQUENCY_76_8_RC_MHZ       = 12
CLOCK_FREQUENCY_38_4_RC_MHZ       = 13
CLOCK_FREQUENCY_76_8_XO_MHZ       = 14
CLOCK_FREQUENCY_38_4_XO_MHZ       = 15
CLOCK_FREQUENCY_DISABLED          = 16

CLKEN_SYSPLL                      = (1 << 0)
CLKEN_CPUPLL                      = (1 << 4)
CLKEN_ES0                         = (1 << 12)
CLKEN_ES1                         = (1 << 13)
CLKEN_HFXO_OUT                    = (1 << 18)
CLKEN_CLK_160M                    = (1 << 20)
CLKEN_CLK_100M                    = (1 << 21)
CLKEN_USB                         = (1 << 22)
CLKEN_HFOSC                       = (1 << 23)

A32_CLOCK_GATE                    = 0
A32_REFCLK                        = 1
A32_SYSPLL                        = 2
A32_CPUPLL                        = 4

ACLK_CLOCK_GATE                   = 0
ACLK_REFCLK                       = 1
ACLK_SYSPLL                       = 2

DIVIDER_CPUPLL                    = 0
DIVIDER_SYSPLL                    = 1
DIVIDER_ACLK                      = 2
DIVIDER_HCLK                      = 3
DIVIDER_PCLK                      = 4

pll_target_lut = {
  PLL_TARGET_SYSREFCLK : "SYS REF",
  PLL_TARGET_SYSCLK : "SYS CLK",
  PLL_TARGET_UART : "UART",
  PLL_TARGET_ES0  : "ES0",
  PLL_TARGET_ES1  : "ES1",
  PLL_TARGET_SECENC : "SECENC"
}

pll_source_lut = {
    PLL_SOURCE_PLL : "PLL",
    PLL_SOURCE_OSC : "OSC"
}

clock_divider_lut = {
  DIVIDER_CPUPLL : "DIVIDER_CPUPLL",
  DIVIDER_SYSPLL : "DIVIDER_SYSPLL",
  DIVIDER_ACLK : "DIVIDER_ACLK",
  DIVIDER_HCLK : "DIVIDER_HCLK",
  DIVIDER_PCLK : "DIVIDER_PCLK"
}

a32_clock_source_lut = {
    0 : "<not set>",
    A32_CLOCK_GATE : "A32 Clock gate",
    A32_REFCLK : "A32 ref clk",
    A32_SYSPLL : "A32 SYS PLL",
    A32_CPUPLL : "A32 CPUPLL"
}

osc_source_lut = {
    OSCILLATOR_SOURCE_RC : "RC",
    OSCILLATOR_SOURCE_XTAL : "XTAL"
}

osc_target_lut = {
    OSCILLATOR_TARGET_SYS_CLOCKS : "Sys clocks",
    OSCILLATOR_TARGET_PERIPH_CLOCKS : "Peripheral clocks",
    OSCILLATOR_TARGET_S32K_CLOCK : "S32K clock"
}

clk_frequency_lut = {
    CLOCK_FREQUENCY_800MHZ : "800Mhz",
    CLOCK_FREQUENCY_400MHZ : "400Mhz",
    CLOCK_FREQUENCY_300MHZ : "300Mhz",
    CLOCK_FREQUENCY_200MHZ : "200Mhz",
    CLOCK_FREQUENCY_160MHZ : "160Mhz",
    CLOCK_FREQUENCY_120MHZ : "120Mhz",
    CLOCK_FREQUENCY_80MHZ : "80Mhz",
    CLOCK_FREQUENCY_60MHZ : "60Mhz",
    CLOCK_FREQUENCY_100MHZ : "100Mhz",
    CLOCK_FREQUENCY_50MHZ : "50Mhz",
    CLOCK_FREQUENCY_20MHZ : "20Mhz" ,
    CLOCK_FREQUENCY_10MHZ : "10Mhz",
    CLOCK_FREQUENCY_76_8_RC_MHZ : "76.8Mhz RC",
    CLOCK_FREQUENCY_38_4_RC_MHZ : "38.4<hz RC",
    CLOCK_FREQUENCY_76_8_XO_MHZ : "76.8Mhz XO",
    CLOCK_FREQUENCY_38_4_XO_MHZ : "38.4Mhz XO",
    CLOCK_FREQUENCY_DISABLED : "Disabled"
}

aclk_clock_source_lut = {
  ACLK_CLOCK_GATE : "ACLK Clock gate",
  ACLK_REFCLK : "ACLK Ref Clock",
  ACLK_SYSPLL : "ACLK Sys PLL"
}

def pll_target_to_string(target):
    """
    Convert input to string

    @param target:
    @return: string based on input
    """
    return pll_target_lut.get(target)

def pll_source_to_string(source):
    """
    Convert input to string

    @param source:
    @return: string based on input
    """

    return pll_source_lut.get(source)

def divider_to_string(divider):
    """
    Convert input to string

    @param divider:
    @return: string based on input
    """

    return clock_divider_lut.get(divider)

def aclk_clock_source_to_string(aclk_source):
    """
    Convert input to string

    @param aclk_source:
    @return: string based on input
    """

    return aclk_clock_source_lut.get(aclk_source)

def a32_clock_source_to_string(a32_source):
    """
    Convert input to string

    @param a32_source:
    @return: string based on input
    """

    return a32_clock_source_lut.get(a32_source)

def osc_source_to_string(osc_source):
    """
    Convert input to string

    @param osc_source:
    @return: string based on input
    """

    return osc_source_lut.get(osc_source)

def osc_target_to_string(osc_target):
    """
    Convert input to string

    @param osc_target:
    @return: string based on input
    """

    return osc_target_lut.get(osc_target)

def clk_frequency_to_string(clk_frequency):
    """
    Convert input to string

    @param clk_frequency:
    @return: string based on input
    """

    return clk_frequency_lut.get(clk_frequency)

def clk_enable_to_string(clk_enable):
    """
    parse the bit fields and return a printable string
    @param clk_enable: bit encoded values
    @return: string based on input
    """
    status_string = ''
    if clk_enable & CLKEN_SYSPLL:
        status_string += "\tSYSPLL\n"
    if clk_enable & CLKEN_SYSPLL:
        status_string += "\tES0CPUPLL\n"
    if clk_enable & CLKEN_ES0:
        status_string += "\tES0\n"
    if clk_enable & CLKEN_ES1:
        status_string += "\tES1\n"
    if clk_enable & CLKEN_HFXO_OUT:
        status_string += "\tHFXO_OUT\n"
    if clk_enable & CLKEN_CLK_160M:
        status_string += "\tCLK_160MHz\n"
    if clk_enable & CLKEN_CLK_100M:
        status_string += "\tCLK_100Mhz\n"
    if clk_enable & CLKEN_USB:
        status_string += "\tUSB\n"
    if clk_enable & CLKEN_HFOSC:
        status_string += "\tHFOSC\n"

    return status_string

def clk_status_to_string(clk_status):
    """
    parse the bit fields and return a printable string
    @param clk_status: bit encoded values
    @return: string based on input
    """
    status_string = ''
    if clk_status & PLL_CLK_STATUS_XTAL_STARTED:
        status_string += "\tXTAL STARTED\n"
    if clk_status & PLL_CLK_STATUS_PLL_STATRTED:
        status_string += "\tPLL STARTED\n"
    if clk_status & PLL_CLK_STATUS_PLL_LOCKED:
        status_string += "\tPLL LOCKED\n"
    if clk_status & PLL_CLK_STATUS_SWITCH_OSC_TO_XTAL:
        status_string += "\tSwitch OSC->XTAL\n"
    if clk_status & PLL_CLK_STATUS_SWITCH_OSC:
        status_string += "\tSwitch OSC\n"
    if clk_status & PLL_CLK_STATUS_SWITCH_PLL:
        status_string += "\tSwitch PLL\n"

    return status_string

def display_clk_pll_info(clk_pll_status, osc_source,
                         osc_target, clk_frequency,
                         clk_freq_es0, clk_freq_es1,
                         clk_state,
                         clk_divider,clk_divider_value,
                         pll_source, pll_target,
                         a32_source, aclk_source):
    """ display_clk_pll
        - show Clock, Pll Xtal info
    """
    isp_print_color("blue","Clock Status\n")
    isp_print_color("blue" ,"%s" % (clk_status_to_string(clk_pll_status)))
    isp_print_color("blue" ,"OSC source   %s\n" %
                    (osc_source_to_string(osc_source)))
    isp_print_color("blue" ,"OSC target   %s\n" %
                    (osc_target_to_string(osc_target)))
    isp_print_color("blue" ,"CLK freq     %s\n" %
                    (clk_frequency_to_string(clk_frequency)))
    isp_print_color("blue" ,"CLK freq ES0 %s\n" %
                    (clk_frequency_to_string(clk_freq_es0)))
    isp_print_color("blue" ,"CLK freq ES1 %s\n" %
                    (clk_frequency_to_string(clk_freq_es1)))
    isp_print_color("blue" ,"CLK Enable   0x%08x\n" % (clk_state))
    isp_print_color("blue" ,"%s" % clk_enable_to_string(clk_state))
    isp_print_color("blue" ,"CLK divider  %s 0x%08X\n" %
                    (divider_to_string(clk_divider),
                     clk_divider_value))
    isp_print_color("blue" ,"PLL source   %s\n" %
                    (pll_source_to_string(pll_source)))
    isp_print_color("blue" ,"PLL target   %s\n" %
                    (pll_target_to_string(pll_target)))
    isp_print_color("blue" ,"A32 source   %s\n" %
                    (a32_clock_source_to_string(a32_source)))
    isp_print_color("blue" ,"ACLK source  %s\n" %
                    (aclk_clock_source_to_string(aclk_source)))

def display_clock_info(message):
    """
        display clock, pll, xtal entries sent back from Target
        message    -- ISP data to parse
    """

    # Unpack the power_status_t::PPU from SERAM
    (clk_pll_status,) = struct.unpack("<I",bytes(message[0:4]))
    (osc_source,) = struct.unpack("<I",bytes(message[4:8]))
    (osc_target,) = struct.unpack("<I",bytes(message[8:12]))
    (clk_frequency,) = struct.unpack("<I",bytes(message[12:16]))
    (clk_freq_es0,) = struct.unpack("<I",bytes(message[16:20]))
    (clk_freq_es1,) = struct.unpack("<I",bytes(message[20:24]))
    (clk_state,) = struct.unpack("<I",bytes(message[24:28]))
    (clk_divider,) = struct.unpack("<I",bytes(message[28:32]))
    (clk_divider_value,) = struct.unpack("<I",bytes(message[32:36]))
    (pll_source,) = struct.unpack("<I",bytes(message[36:40]))
    (pll_target,) = struct.unpack("<I",bytes(message[40:44]))
    (a32_source,) = struct.unpack("<I",bytes(message[44:48]))
    (aclk_source,) = struct.unpack("<I",bytes(message[48:52]))

    display_clk_pll_info(clk_pll_status, osc_source,
                         osc_target, clk_frequency,
                         clk_freq_es0, clk_freq_es1,
                         clk_state,
                         clk_divider,clk_divider_value,
                         pll_source,pll_target,
                         a32_source, aclk_source)
    