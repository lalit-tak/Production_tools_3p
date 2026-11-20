import os


MAX_CURRENT = 1.6
MIN_CURRENT = 0.3
SOFTWARE_VERSION = [106]
OVERPOWER_LIMIT = 7200
TOTAL_ENERGY = 20
ALLOWED_ENERGY=100
TIME_DRIFT = 30
SERIAL_NO_TRIES = 3
FACTORY_TRIES = 4
ENERGY_TRIES = 8
LOG_PATH = os.path.join(
    (os.path.join(
        os.path.expanduser('~'),
        '.grampower/mri/log')))
MAPPING_LOG = os.path.join(
    (os.path.join(
        os.path.expanduser('~'),
        '.grampower/mri/serial_ip_map.json')))
