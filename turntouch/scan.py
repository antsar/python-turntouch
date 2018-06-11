"""Functions related to scanning for Turn Touch devices. Note that scanning
may require root privileges."""

import logging
from typing import List
from bluepy import btle
from .turntouch import TurnTouch

logger = logging.getLogger('TurnTouch')


def scan(interface: int = 0,
         timeout: float = 10,
         only_one: bool = False) -> List[TurnTouch]:
    """Scan for Turn Touch devices.
    :param interface int: Index of the bluetooth device (eg. 0 for hci0)
    :param timeout float: Scanning timeout, in seconds
    :param only_one float: Stop scanning after one Turn Touch is found
    :return list: Found TurnTouch devices"""

    TT_DEVICE_NAME = 'Turn Touch Remote'
    TT_SHORT_DEVICE_NAME = 'Turn Touch Rem'
    BLE_SHORT_DEVICE_NAME = 0x08
    BLE_COMPLETE_DEVICE_NAME = 0x09

    class DeviceFoundException(Exception):
        """Exception thrown when a device is found."""
        pass

    class ScanDelegate(btle.DefaultDelegate):
        """Handle callbacks for devices discovered by a BLE scan."""
        only_one = False

        def __init__(self, only_one=False, *args, **kwargs):
            self.only_one = only_one
            super(ScanDelegate, self).__init__(*args, **kwargs)

        def handleDiscovery(self, device, is_new_device, is_new_data):
            """When a Turn Touch device is discovered, log a message.
            If only searching for one device, short-circuit the scan by raising
            a DeviceFoundException once we've found a Turn Touch device."""
            if is_new_device and is_turn_touch(device):
                logger.debug("Discovered device {address}".format(
                    address=device.addr))
                if self.only_one:
                    raise DeviceFoundException()

    def is_turn_touch(device: btle.ScanEntry) -> bool:
        """Determine whether a ScanEntry (device) is a Turn Touch."""
        short_name = device.getValueText(BLE_SHORT_DEVICE_NAME)
        name = device.getValueText(BLE_COMPLETE_DEVICE_NAME)
        return name == TT_DEVICE_NAME or short_name == TT_SHORT_DEVICE_NAME

    scanner = btle.Scanner(interface)
    logger.info("Scanning for Turn Touch devices...")
    try:
        scanner.withDelegate(ScanDelegate(only_one)).scan(timeout)
    except DeviceFoundException:
        pass
    finally:
        devices = [device
                   for device in scanner.scanned.values()
                   if is_turn_touch(device)]
        logger.info("Scan finished. Found {count} device(s)."
                    .format(count=len(devices)))
        return [TurnTouch(device) for device in devices]
