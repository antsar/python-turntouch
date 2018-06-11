"""Classes related to the Turn Touch remote."""

import logging
from bluepy import btle
from typing import Union

logger = logging.getLogger('TurnTouch')


class Action:
    """A type of button press."""
    def __init__(self, data: bytes, label: str, name: str,
                 multi: bool = False):
        if not name.isidentifier():
            raise TurnTouchException("Press name must be a valid identifier.")
        self.data = data
        self.label = label
        self.name = name
        self.multi = multi

    def __repr__(self):
        return '<Action name="{name}">'.format(name=self.name)


class TurnTouchException(Exception):
    """An error related to the Turn Touch bluetooth smart home remote."""
    pass


class DefaultActionHandler:
    """A callback handler class for button press events.
    Create a subclass of this class to define your button press behavior."""

    def button_any(self, action: Action = None): pass

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
        0xFF00: Action(0xFF00, 'Off', 'button_off'),

        0xFE00: Action(0xFE00, 'North', 'button_north'),
        0xEF00: Action(0xEF00, 'North double tap',
                       'button_north_double_tap'),
        0xFEFF: Action(0xFEFF, 'North hold', 'button_north_hold'),

        0xFD00: Action(0xFD00, 'East', 'button_east'),
        0xDF00: Action(0xDF00, 'East double tap', 'button_east_double_tap'),
        0xFDFF: Action(0xFDFF, 'East hold', 'button_east_hold'),

        0xFB00: Action(0xFB00, 'West', 'button_west'),
        0xBF00: Action(0xBF00, 'West double tap', 'button_west_double_tap'),
        0xFBFF: Action(0xFBFF, 'West hold', 'button_west_hold'),

        0xF700: Action(0xF700, 'South', 'button_south'),
        0x7F00: Action(0x7F00, 'South double tap',
                       'button_south_double_tap'),
        0xF7FF: Action(0xF7FF, 'South hold', 'button_south_hold'),

        0xFC00: Action(0xFC00, 'Multi North East',
                       'button_multi_north_east', True),
        0xFA00: Action(0xFA00, 'Multi North West',
                       'button_multi_north_west', True),
        0xF600: Action(0xF600, 'Multi North South',
                       'button_multi_north_south', True),
        0xF900: Action(0xF900, 'Multi East West',
                       'button_multi_east_west', True),
        0xF500: Action(0xF500, 'Multi East South',
                       'button_multi_east_south', True),
        0xF300: Action(0xF300, 'Multi West South',
                       'button_multi_west_south', True),

        0xF800: Action(0xF800, 'Multi North East West',
                       'button_multi_north_east_west', True),
        0xF400: Action(0xF400, 'Multi North East South',
                       'button_multi_north_east_south', True),
        0xF200: Action(0xF200, 'Multi North West South',
                       'button_multi_north_west_south', True),
        0xF100: Action(0xF100, 'Multi East West South',
                       'button_multi_east_west_south', True),

        0xF000: Action(0xF000, 'Multi North East West South',
                       'button_multi_north_east_west_south', True),
    }

    def __init__(self,
                 address: Union[str, btle.ScanEntry],
                 handler: DefaultActionHandler = None,
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

    def set_handler(self, handler: DefaultActionHandler = None):
        """Set the button press handler class for this remote."""
        self._handler = handler or DefaultActionHandler

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
                    self.turn_touch.PRESS_TYPES.get(type_int).name)()
