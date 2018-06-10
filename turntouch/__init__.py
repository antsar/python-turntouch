""" Python library for the Turn Touch bluetooth smart home remote."""
import logging
from bluepy import btle
from typing import List, Union


logger = logging.getLogger('TurnTouch')


class PressType:
    """A type of button press."""
    def __init__(self, data: bytes, name: str, function_name: str,
                 multi: bool = False):
        self.data = data
        self.name = name
        self.function_name = function_name
        self.multi = multi

    def __repr__(self):
        return '<PressType name="{name}">'.format(name=self.name)


class DefaultButtonPressHandler:
    """A callback handler class for button press events.
    Create a subclass of this class to define your button press behavior."""

    def button_any(self, press_type: PressType = None): pass

    def button_off(self): pass

    def button_north(self): pass

    def button_north_double_tap(self): pass

    def button_north_hold(self): pass

    def button_east(self): pass

    def button_east_double_tap(self): pass

    def button_east_hold(self): pass

    def button_west(self): pass

    def button_west_double_tap(self): pass

    def button_west_hold(self): pass

    def button_south(self): pass

    def button_south_double_tap(self): pass

    def button_south_hold(self): pass

    def button_multi_north_east(self): pass

    def button_multi_north_west(self): pass

    def button_multi_north_south(self): pass

    def button_multi_east_west(self): pass

    def button_multi_east_south(self): pass

    def button_multi_west_south(self): pass

    def button_multi_north_east_west(self): pass

    def button_multi_north_east_south(self): pass

    def button_multi_north_west_south(self): pass

    def button_multi_east_west_south(self): pass

    def button_multi_north_east_west_south(self): pass


class TurnTouch(btle.Peripheral):
    """A Turn Touch smart home remote."""

    BUTTON_STATUS_CHARACTERISTIC_UUID = '99c31525-dc4f-41b1-bb04-4e4deb81fadd'
    BATTERY_LEVEL_CHARACTERISTIC_UUID = '2a19'
    DEVICE_NAME_CHARACTERISTIC_UUID = '99c31526-dc4f-41b1-bb04-4e4deb81fadd'
    DEVICE_NAME_LENGTH = 32
    PRESS_TYPES = {
        0xFF00: PressType(0xFF00, 'Off', 'button_off'),

        0xFE00: PressType(0xFE00, 'North', 'button_north'),
        0xEF00: PressType(0xEF00, 'North double tap',
                          'button_north_double_tap'),
        0xFEFF: PressType(0xFEFF, 'North hold', 'button_north_hold'),

        0xFD00: PressType(0xFD00, 'East', 'button_east'),
        0xDF00: PressType(0xDF00, 'East double tap', 'button_east_double_tap'),
        0xFDFF: PressType(0xFDFF, 'East hold', 'button_east_hold'),

        0xFB00: PressType(0xFB00, 'West', 'button_west'),
        0xBF00: PressType(0xBF00, 'West double tap', 'button_west_double_tap'),
        0xFBFF: PressType(0xFBFF, 'West hold', 'button_west_hold'),

        0xF700: PressType(0xF700, 'South', 'button_south'),
        0x7F00: PressType(0x7F00, 'South double tap',
                          'button_south_double_tap'),
        0xF7FF: PressType(0xF7FF, 'South hold', 'button_south_hold'),

        0xFC00: PressType(0xFC00, 'Multi North East',
                          'button_multi_north_east', True),
        0xFA00: PressType(0xFA00, 'Multi North West',
                          'button_multi_north_west', True),
        0xF600: PressType(0xF600, 'Multi North South',
                          'button_multi_north_south', True),
        0xF900: PressType(0xF900, 'Multi East West',
                          'button_multi_east_west', True),
        0xF500: PressType(0xF500, 'Multi East South',
                          'button_multi_east_south', True),
        0xF300: PressType(0xF300, 'Multi West South',
                          'button_multi_west_south', True),

        0xF800: PressType(0xF800, 'Multi North East West',
                          'button_multi_north_east_west', True),
        0xF400: PressType(0xF400, 'Multi North East South',
                          'button_multi_north_east_south', True),
        0xF200: PressType(0xF200, 'Multi North West South',
                          'button_multi_north_west_south', True),
        0xF100: PressType(0xF100, 'Multi East West South',
                          'button_multi_east_west_south', True),

        0xF000: PressType(0xF000, 'Multi North East West South',
                          'button_multi_north_east_west_south', True),
    }

    def __init__(self,
                 address: Union[str, btle.ScanEntry],
                 handler: DefaultButtonPressHandler = None,
                 listen: bool = False,
                 interface: int = None):
        """Connect to the Turn Touch remote.
        Set appropriate address type (overriding btle default).
        :param address Union[str, btle.ScanEntry]:
            MAC address (or btle.ScanEntry object) of this device
        :param listen bool: Start listening for button presses
        :param interface int: Index of the bluetooth device (eg. 0 for hci0)"""
        try:
            logger.info("Connecting to device {address}...".format(
                address=address))
            super(TurnTouch, self).__init__(
                address, btle.ADDR_TYPE_RANDOM, interface)
            logger.info("Successfully connected to device {address}.".format(
                address=self.addr))
        except btle.BTLEException:
            raise TurnTouchException("Failed to connect to device {address}"
                                     .format(address=address))
        self.withDelegate(self.NotificationDelegate(turn_touch=self))
        self.set_handler(handler)
        if listen:
            self.listen_forever()

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

    def set_handler(self, handler: DefaultButtonPressHandler = None):
        """Set the button press handler class for this remote."""
        self._handler = handler or DefaultButtonPressHandler

    def listen(self, timeout: int = 0, only_one: bool = True):
        """Listen for a button press event.
        Will listen indefinitely if `only_one` is False."""
        self._enable_notifications()
        if only_one:
            self.waitForNotifications(timeout)
        else:
            while True:
                self.waitForNotifications(timeout)
        self._enable_notifications(enable=False)

    def listen_forever(self):
        """Listen for button press events indefinitely."""
        self.listen(only_one=False)

    def _enable_notifications(self, enabled=True):
        """Tell the remote to start sending button press notifications."""
        notification_handle = self.getCharacteristics(
            uuid=self.BUTTON_STATUS_CHARACTERISTIC_UUID)[0].getHandle()
        notification_enable_handle = notification_handle + 1
        logger.debug("{action} notifications for device {address}...".format(
            action="Enabling" if enabled else "Disabling", address=self.addr))
        self.writeCharacteristic(notification_enable_handle,
                                 bytes([0x01 if enabled else 0x00, 0x00]),
                                 withResponse=True)
        logger.debug("Notifications {action} for device {address}.".format(
            action="enabled" if enabled else "disabled", address=self.addr))

    class NotificationDelegate(btle.DefaultDelegate):
        """Handle callbacks for notifications from the device."""
        def __init__(self, turn_touch):
            """Retain a reference to the calling object."""
            self.turn_touch = turn_touch

        def handleNotification(self, cHandle, data):
            """Call the appropriate button press handler method(s)."""
            logger.debug("Got notification {notification}".format(
                notification=data))
            type_int = int.from_bytes(data, byteorder='big')
            # Call the generic (any button) callback.
            self.turn_touch._handler.button_any(
                self.turn_touch.PRESS_TYPES.get(type_int))
            # Call the button-specific callback
            getattr(self.turn_touch._handler,
                    self.turn_touch.PRESS_TYPES.get(type_int).function_name)()


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
