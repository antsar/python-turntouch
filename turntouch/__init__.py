""" Python library for the Turn Touch bluetooth smart home remote."""
import logging
from bluepy import btle
from typing import List


logger = logging.getLogger('TurnTouch')


class TurnTouch(btle.Peripheral):
    """A Turn Touch smart home remote."""


def scan(device_index: int = 0,
         timeout: float = 10,
         only_one: bool = False) -> List[TurnTouch]:
    """Scan for Turn Touch devices.
    :param device_index int: Index of the bluetooth device (eg. 0 for hci0)
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
                logger.info("Discovered device {address}".format(
                    address=device.addr))
                if self.only_one:
                    raise DeviceFoundException()

    def is_turn_touch(device: btle.ScanEntry) -> bool:
        """Determine whether a ScanEntry (device) is a Turn Touch."""
        short_name = device.getValueText(BLE_SHORT_DEVICE_NAME)
        name = device.getValueText(BLE_COMPLETE_DEVICE_NAME)
        return name == TT_DEVICE_NAME or short_name == TT_SHORT_DEVICE_NAME

    scanner = btle.Scanner(device_index)
    try:
        scanner.withDelegate(ScanDelegate(only_one)).scan(timeout)
    except DeviceFoundException:
        pass
    finally:
        return [TurnTouch(device) for device in scanner.scanned.values()
                if is_turn_touch(device)]
