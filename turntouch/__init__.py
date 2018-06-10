""" Python library for the Turn Touch bluetooth smart home remote."""
import logging
from bluepy import btle
from typing import List, Union


logger = logging.getLogger('TurnTouch')


class TurnTouch(btle.Peripheral):
    """A Turn Touch smart home remote."""

    BUTTON_STATUS_CHARACTERISTIC_UUID = '99c31525-dc4f-41b1-bb04-4e4deb81fadd'
    BATTERY_LEVEL_CHARACTERISTIC_UUID = '2a19'
    DEVICE_NAME_CHARACTERISTIC_UUID = '99c31526-dc4f-41b1-bb04-4e4deb81fadd'
    DEVICE_NAME_LENGTH = 32

    def __init__(self,
                 device_address: Union[str, btle.ScanEntry],
                 interface: int = None,
                 enable_notifications: bool = True):
        """Connect to the Turn Touch remote.
        Set appropriate address type (overriding btle default).
        :param device_address Union[str, btle.ScanEntry]:
            MAC address (or btle.ScanEntry object) of this device
        :param interface int: Index of the bluetooth device (eg. 0 for hci0)
        :param enable_notifications bool: Start listening for button presses"""
        try:
            logger.info("Connecting to device {address}...'".format(
                address=self.addr))
            super(TurnTouch, self).__init__(
                device_address, btle.ADDR_TYPE_RANDOM, interface)
            logger.info("Successfully connected to device {address}.'".format(
                address=self.addr))
        except btle.BTLEException:
            raise TurnTouchException("Failed to connect to device {address}"
                                     .format(address=device_address))

    @property
    def name(self) -> str:
        """Read the nickname of this remote."""
        name_bytes = self.getCharacteristics(
            uuid=self.DEVICE_NAME_CHARACTERISTIC_UUID)[0].read()
        logger.debug("Read name of device {address}: '{name}'".format(
            address=self.addr, name=name_bytes))
        return name_bytes.decode('utf-8').rstrip('\0')

    @name.setter
    def name(self, name: str):
        """Set the nickname of this remote."""
        if len(name) > self.DEVICE_NAME_LENGTH:
            raise(TurnTouchException("Name must be {limit} characters or less."
                                     .format(limit=self.DEVICE_NAME_LENGTH)))
        name_characteristic = self.getCharacteristics(
            uuid=self.DEVICE_NAME_CHARACTERISTIC_UUID)[0]
        name_bytes = name.encode('utf-8').ljust(self.DEVICE_NAME_LENGTH, b'\0')
        name_characteristic.write(name_bytes, withResponse=True)
        logger.debug("Set name for device {address} to '{name}'".format(
            address=self.addr, name=name_bytes))


class TurnTouchException(Exception):
    """An error related to the Turn Touch bluetooth smart home remote."""
    pass


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
