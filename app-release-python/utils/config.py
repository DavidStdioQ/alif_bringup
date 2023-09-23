import sys
import json
from json.decoder import JSONDecodeError

# Define Version constant for each separate tool
# 0.06.000 added package and offset params
TOOL_VERSION = "0.06.000"

EXIT_WITH_ERROR = 1

# Device Part# and Revision
DEVICE_PART_NUMBER = ''
DEVICE_REVISION = ''
DEVICE_FAMILY = ''
DEVICE_FEATURE_SET = ''
DEVICE_PACKAGE = ''
DEVICE_REV_PACKAGE_EXT = ''
DEVICE_REV_BAUD_RATE = ''
DEVICE_OFFSET = ''

# MRAM Access Interface
MRAM_BURN_INTERFACE = ''

# JTAG Adapter
JTAG_ADAPTER = ''

# memory defines for Alif/OEM MRAM Addresses
MRAM_BASE_ADDRESS   = 0x00
ALIF_BASE_ADDRESS   = 0x00
APP_BASE_ADDRESS    = 0x00
# memory defines for Alif/OEM MRAM Sizes
MRAM_SIZE           = 0x00
ALIF_MRAM_SIZE      = 0x00
APP_MRAM_SIZE       = 0x00

# parameters by architecture
SERAM_BANKS     = 0

# ALIF TOC POINTER SIZE (pointers to)
ALIF_TOC_POINTER_SIZE = 16

REVISIONS = ['A0', 'A1', 'B0']

def read_global_config(file):

#    print("Opening file %s" % file);
    f = open(file, 'r')
    try:
        cfg = json.load(f)

    except JSONDecodeError as e:
        print("ERROR in JSON file.")
        print(str(e))
        sys.exit(EXIT_WITH_ERROR)

    except ValueError as v:
        print("ERROR in JSON file:")
        print(str(v))
        sys.exit(EXIT_WITH_ERROR)

    except:
        print("ERROR: Unknown error loading JSON file")
        sys.exit(EXIT_WITH_ERROR)

    f.close()
    return cfg

def checkAttribute(cfg, attribute):
    try:
        test = cfg[attribute]

    except KeyError as e:
        print('Parameter ' + str(e) + ' is not configured')
        sys.exit(EXIT_WITH_ERROR)

    except:
        print('General error checking attribute ' + attribute)
        sys.exit(EXIT_WITH_ERROR)

def load_global_config():
    global DEVICE_PART_NUMBER
    global DEVICE_REVISION
    global DEVICE_FAMILY
    global DEVICE_FEATURE_SET
    global DEVICE_PACKAGE
    global DEVICE_REV_PACKAGE_EXT
    global DEVICE_REV_BAUD_RATE
    global DEVICE_OFFSET
    global MRAM_BASE_ADDRESS
    global ALIF_BASE_ADDRESS
    global APP_BASE_ADDRESS
    global MRAM_SIZE
    global ALIF_MRAM_SIZE
    global APP_MRAM_SIZE
    global MRAM_BURN_INTERFACE
    global JTAG_ADAPTER
    global SERAM_BANKS
 
    cfg = read_global_config("utils/global-cfg.db")
 
    # validate configuration parameters
    # check parameter is configured...
    checkAttribute(cfg['DEVICE'], 'Revision')
    # validate configuration
    if cfg['DEVICE']['Revision'] not in REVISIONS:
        print('Revision in configuration is invalid!')
        sys.exit(EXIT_WITH_ERROR)

    DEVICE_REVISION = cfg['DEVICE']['Revision']
    MRAM_BASE_ADDRESS = 0x80000000
    # set values for this configuration
    if cfg['DEVICE']['Revision'] == 'A0':
        APP_OFFSET = 0x100
 
    elif cfg['DEVICE']['Revision'] == 'A1':
        APP_OFFSET = 0x00
 
    elif cfg['DEVICE']['Revision'] == 'B0':
        APP_OFFSET = 0x00

    # set MRAM BURNER Access Interface
    MRAM_BURN_INTERFACE = cfg['MRAM-BURNER']['Interface']

    # set JTAG Adapter
    JTAG_ADAPTER = cfg['MRAM-BURNER']['Jtag-adapter']

    # read devices DB
    db = read_global_config("utils/devicesDB.db")

    # read architectures DB
    features = read_global_config("utils/featuresDB.db")

    DEVICE_PART_NUMBER   = cfg['DEVICE']['Part#']
    DEVICE_FAMILY        = db[cfg['DEVICE']['Part#']]['family']
    DEVICE_FEATURE_SET   = db[cfg['DEVICE']['Part#']]['featureSet']
    DEVICE_PACKAGE       = db[cfg['DEVICE']['Part#']]['package']
    DEVICE_REV_PACKAGE_EXT = features[db[cfg['DEVICE']['Part#']]['featureSet']]['rev_package_ext']
    DEVICE_REV_BAUD_RATE   = features[db[cfg['DEVICE']['Part#']]['featureSet']]['rev_baud_rate']
    DEVICE_OFFSET        = db[cfg['DEVICE']['Part#']]['offset']

    # print("cfg['DEVICE']['Part#']                                                = %s" % DEVICE_PART_NUMBER)
    # print("db[cfg['DEVICE']['Part#']]['family']                                  = %s" % DEVICE_FAMILY)
    # print("db[cfg['DEVICE']['Part#']]['featureSet']                              = %s" % DEVICE_FEATURE_SET)
    # print("db[cfg['DEVICE']['Part#']]['package']                                 = %s" % DEVICE_PACKAGE)
    # print("features[db[cfg['DEVICE']['Part#']]['featureSet']]['rev_package_ext'] = %s" % DEVICE_REV_PACKAGE_EXT);
    #print("features[db[cfg['DEVICE']['Part#']]['featureSet']]['rev_baud_rate'] = %s" % DEVICE_REV_BAUD_RATE);
    # print("db[cfg['DEVICE']['Part#']]['offset']                                  = %s" % DEVICE_OFFSET)

    # set MRAM Size (same for all revisions)
    MRAM_SIZE = int(features[db[cfg['DEVICE']['Part#']]['featureSet']]['mram_total'], 16)
    SERAM_BANKS = features[db[cfg['DEVICE']['Part#']]['featureSet']]['seram_banks']

    # relative addresses (offsets)
    alif_offset = int(db[cfg['DEVICE']['Part#']]['alif_offset'], 16)
    app_size    = int(db[cfg['DEVICE']['Part#']]['app_size'], 16) - APP_OFFSET

    # calculate 
    ALIF_BASE_ADDRESS = MRAM_BASE_ADDRESS + alif_offset
    APP_BASE_ADDRESS  = MRAM_BASE_ADDRESS + APP_OFFSET
    ALIF_MRAM_SIZE = MRAM_SIZE - alif_offset - ALIF_TOC_POINTER_SIZE
    APP_MRAM_SIZE = app_size
