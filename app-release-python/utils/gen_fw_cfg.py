#!/usr/bin/env python3
"""
    __author__ = ""
    __copyright__ = "ALIF Seminconductor"
    __version__ = "0.1.0"
    __status__ = "Dev"
"""
# pylint: disable=unused-argument, invalid-name, bare-except

import sys
import argparse
import json
import os
import utils.toc_common

TOOL_VERSION ="0.1.001"      # Define Version constant for each separate tool

EXIT_WITH_ERROR = 1

FW_CFG_FILE = "build/fw_cfg.json"

def mram_size_to_address(mram_size):
    mram_size_mb = int(float(mram_size) * 1024 * 1024)
    mram_base_int = int("0x80000000", 16)
    stoc_start = mram_base_int + mram_size_mb
    atoc_end = stoc_start - 1
    atoc_end_str = "0x" + hex(atoc_end).lstrip("0x").upper()
    stoc_start_str = "0x" + hex(stoc_start).lstrip("0x").upper()
    return atoc_end_str, stoc_start_str

def handle_sram(sram_size, is_rev_a, firewall_components, protected_areas):

    if "13.5" == sram_size: # no SRAM wounding
        return

    # load the definitions for FCs #12 (EXPMST1), #4 (XNVM) and #5 CVM
    with open('firewall/sram.json', "r") as json_file:
        sram_json = json.load(json_file)

    # FC12 covers the Modem TCMs, and in REV_Ax - the M55-HE as well.
    fc12_json = sram_json["firewall_components"][0]
    fc12_prot_area_json = sram_json["protected_areas"][0]
    
    if "12.75" == sram_size: # GNSS enabled E7/E5/E3
        regions = fc12_json["configured_regions"]
        if is_rev_a:
            regions[0]["end_address"] = "0x63FFFFFF"
            fc12_prot_area_json["start_address"] = "0x64000000"
        else:
            regions[0]["start_address"] = "0x62000000"
            regions[0]["end_address"] = "0x6FFFFFFF"
            regions.pop(1)
            fc12_prot_area_json["start_address"] = "0x60000000"
            fc12_prot_area_json["end_address"] = "0x61FFFFFF"

        firewall_components.append(fc12_json)
        protected_areas.append(fc12_prot_area_json)
        return
    
    # The stock configuration enables access to the address range 0x60000000-0x62000000.
    # In REV_A, that is the M55-HE TCM and it should always be accessible
    # In REV_B, that is the GNSS TCM. Access to it should be disabled in the 8.25 MB SRAM configuration
    if not is_rev_a:
        regions = fc12_json["configured_regions"]
        regions.clear()
        fc12_prot_area_json["start_address"] = "0x60000000"

    firewall_components.append(fc12_json)
    protected_areas.append(fc12_prot_area_json)

    if "8.25" == sram_size: # no other wounding
        return

    # Wound SRAM1 - FC #4 - XNVM
    firewall_components.append(sram_json["firewall_components"][1])
    protected_areas.append(sram_json["protected_areas"][1])

    if "5.75" == sram_size: # no SRAM0 wounding
        return

    # Wound FC #5 (CVM/SRAM0) to different sizes
    fc5_json = sram_json["firewall_components"][2]
    fc5_prot_area_json = sram_json["protected_areas"][2]

    regions = fc5_json["configured_regions"]
    if "4.25" == sram_size: # E1
        regions[0]["end_address"] = "0x0227FFFF"
        fc5_prot_area_json["start_address"] = "0x02280000"
    elif "3.75" == sram_size: # E3
        regions[0]["end_address"] = "0x021FFFFF"
        fc5_prot_area_json["start_address"] = "0x02200000"
    elif "3.5" == sram_size: # GNSS enabled E1
        regions[0]["end_address"] = "0x0237FFFF"
        fc5_prot_area_json["start_address"] = "0x02380000"
    else: # 2.5, 2.0?, 1.75 # E1
        regions.clear()
        fc5_prot_area_json["start_address"] = "0x02000000"

    firewall_components.append(fc5_json)
    protected_areas.append(fc5_prot_area_json)

def gen_fw_cfg(family, mram_size, sram_size, device_revision):
    # MRAM
    # The following code is tightly coupled with the structure of the file mram.json.
    # Should we define the data structures in Python code instead of reading them from a JSON file?
    with open('firewall/mram.json', "r") as json_file:
        mram_json = json.load(json_file)
    atoc_end_address, stoc_start_address = mram_size_to_address(mram_size)
    mram_json["firewall_components"][0]["configured_regions"][0]["end_address"] = atoc_end_address
    mram_json["protected_areas"][0]["start_address"] = stoc_start_address

    if family != "Balletto":
        is_rev_a = device_revision == 'A0' or device_revision == 'A1'
        if is_rev_a:
            extra_cfg = "firewall/fw_cfg_rev_a.json"
        else:
            extra_cfg = "firewall/fw_cfg_rev_b.json"

        with open(extra_cfg, "r") as extra_cfg_file:
            extra_cfg_json = json.load(extra_cfg_file)
            firewall_components = extra_cfg_json['firewall_components']
    else:
        firewall_components = []

    firewall_components.append(mram_json['firewall_components'][0])
    protected_areas = mram_json['protected_areas']

    # SRAM
    if family != "Balletto":
        handle_sram(sram_size, is_rev_a, firewall_components, protected_areas)

    out_json = {}
    out_json['firewall_components'] = firewall_components
    out_json['protected_areas'] = protected_areas
    
    out_file = FW_CFG_FILE
    if (os.path.exists(out_file)):
        os.remove(out_file)
    
    with open(out_file, 'w') as f:
        json.dump(out_json, f, indent=2)

def main():
    """
    """
    if sys.version_info.major == 2:
        print("[ERROR] You need Python 3 for this application!")
        sys.exit(EXIT_WITH_ERROR)

    # Deal with Command Line
    parser = argparse.ArgumentParser(description=
                                     'Generate STOC device configuration')
    parser.add_argument("-m", "--mram", type=str, default="5.5", help='MRAM size in MB, default 5.5')
    parser.add_argument("-s", "--sram", type=str, default="13.5", help="SRAM size in MB, default 13.5")
    parser.add_argument("-V" , "--version",
                        help="Display Version Number", action="store_true")
    args = parser.parse_args()
    if args.version:
        print(TOOL_VERSION)
        sys.exit()
        
    mram_size = args.mram.rstrip('0').rstrip('.')
    sram_size = args.sram.rstrip('0').rstrip('.')
    
    gen_fw_cfg("", mram_size, sram_size)
        
if __name__ == "__main__":
    main()
