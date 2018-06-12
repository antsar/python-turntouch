"""Classes related to the Turn Touch remote."""

from concurrent.futures import ThreadPoolExecutor
import time
import logging
from bluepy import btle
from typing import List, Union

logger = logging.getLogger('TurnTouch')


class Button:
    """A button on the Turn Touch remote."""
    def __init__(self, label: str, name: str):
        """Define a button.
        :param label str: Human-readable name for the button
        :param name str: Machine name for the button"""
        if not name.isidentifier():
            raise TurnTouchException("Button name must be a valid identifier.")
        self.label = label
        self.name = name

    def __str__(self):
        return self.label

    def __repr__(self):
        return '<Button name="{name}">'.format(name=self.name)


class PressType:
    """A type of button press."""
    def __init__(self, label: str, name: str):
        """Define a button.
        :param label str: Human-readable name for the button
        :param name str: Machine name for the button"""
        if not name.isidentifier():
            raise TurnTouchException("Press name must be a valid identifier.")
        self.label = label
        self.name = name

    def __str__(self):
        return self.label

    def __repr__(self):
        return '<PressType name="{name}">'.format(name=self.name)


class Action:
    """A type of button press."""
    def __init__(self, data: bytes, label: str, name: str,
                 buttons: List[Button], press_type: PressType):
        """Define an action type.
        :param data bytes: Byte representation of this event
        :param label str: Human-readable name of this event
        :param name str: Machine name for this event
        :param buttons List[Button]: Machine name for this event
        :param press_type PressType: Type of press (single, double, hold)"""
        if not name.isidentifier():
            raise TurnTouchException("Press name must be a valid identifier.")
        self.data = data
        self.label = label
        self.name = name
        self.buttons = frozenset(buttons)
        self.press_type = press_type

    def __eq__(self, other):
        return self.data == other.data

    def __str__(self):
        return self.label

    def __repr__(self):
        return '<Action name="{name}">'.format(name=self.name)

    def __hash__(self):
        return self.data

    @property
    def is_multi(self):
        return len(self.buttons) > 1

    @property
    def is_off(self):
        return self.press_type == TurnTouch.PRESS_NONE

    @property
    def is_combo(self):
        return self.press_type in (TurnTouch.PRESS_DOUBLE,
                                   TurnTouch.PRESS_HOLD)


class TurnTouchException(Exception):
    """An error related to the Turn Touch bluetooth smart home remote."""
    pass


class DefaultActionHandler:
    """A callback handler class for button press events.
    Create a subclass of this class to define your button press behavior."""

    def action_any(self, action: Action = None): pass

    def action_off(self): pass

    def action_north(self): pass

    def action_north_double_tap(self): pass

    def action_north_hold(self): pass

    def action_east(self): pass

    def action_east_double_tap(self): pass

    def action_east_hold(self): pass

    def action_west(self): pass

    def action_west_double_tap(self): pass

    def action_west_hold(self): pass

    def action_south(self): pass

    def action_south_double_tap(self): pass

    def action_south_hold(self): pass

    def action_multi_north_east(self): pass

    def action_multi_north_west(self): pass

    def action_multi_north_south(self): pass

    def action_multi_east_west(self): pass

    def action_multi_east_south(self): pass

    def action_multi_west_south(self): pass

    def action_multi_north_east_west(self): pass

    def action_multi_north_east_south(self): pass

    def action_multi_north_west_south(self): pass

    def action_multi_east_west_south(self): pass

    def action_multi_north_east_west_south(self): pass


class TurnTouch(btle.Peripheral):
    """A Turn Touch smart home remote."""

    BUTTON_STATUS_CHARACTERISTIC_UUID = '99c31525-dc4f-41b1-bb04-4e4deb81fadd'
    BATTERY_LEVEL_CHARACTERISTIC_UUID = '2a19'
    DEVICE_NAME_CHARACTERISTIC_UUID = '99c31526-dc4f-41b1-bb04-4e4deb81fadd'
    DEVICE_NAME_LENGTH = 32
    MAX_DELAY = 0.75
    LISTEN_TIMEOUT = 0.1
    BUTTON_NORTH = Button('North', 'north')
    BUTTON_EAST = Button('East', 'east')
    BUTTON_WEST = Button('West', 'west')
    BUTTON_SOUTH = Button('South', 'south')
    PRESS_NONE = PressType('None (off)', 'none')
    PRESS_SINGLE = PressType('Single', 'single')
    PRESS_DOUBLE = PressType('Double', 'double')
    PRESS_HOLD = PressType('Hold', 'hold')
    ACTIONS = {
        0xFF00: Action(0xFF00, 'Off', 'action_off', [], PRESS_NONE),

        0xFE00: Action(0xFE00, 'North', 'action_north', [BUTTON_NORTH],
                       PRESS_SINGLE),
        0xEF00: Action(0xEF00, 'North double tap', 'action_north_double_tap',
                       [BUTTON_NORTH], PRESS_DOUBLE),
        0xFEFF: Action(0xFEFF, 'North hold', 'action_north_hold',
                       [BUTTON_NORTH], PRESS_HOLD),

        0xFD00: Action(0xFD00, 'East', 'action_east', [BUTTON_EAST],
                       PRESS_SINGLE),
        0xDF00: Action(0xDF00, 'East double tap', 'action_east_double_tap',
                       [BUTTON_EAST], PRESS_DOUBLE),
        0xFDFF: Action(0xFDFF, 'East hold', 'action_east_hold', [BUTTON_EAST],
                       PRESS_HOLD),

        0xFB00: Action(0xFB00, 'West', 'action_west', [BUTTON_WEST],
                       PRESS_SINGLE),
        0xBF00: Action(0xBF00, 'West double tap', 'action_west_double_tap',
                       [BUTTON_WEST], PRESS_DOUBLE),
        0xFBFF: Action(0xFBFF, 'West hold', 'action_west_hold', [BUTTON_WEST],
                       PRESS_HOLD),

        0xF700: Action(0xF700, 'South', 'action_south', [BUTTON_SOUTH],
                       PRESS_SINGLE),
        0x7F00: Action(0x7F00, 'South double tap', 'action_south_double_tap',
                       [BUTTON_SOUTH], PRESS_DOUBLE),
        0xF7FF: Action(0xF7FF, 'South hold', 'action_south_hold',
                       [BUTTON_SOUTH], PRESS_HOLD),

        0xFC00: Action(0xFC00, 'Multi North East', 'action_multi_north_east',
                       [BUTTON_NORTH, BUTTON_EAST], PRESS_SINGLE),
        0xFA00: Action(0xFA00, 'Multi North West', 'action_multi_north_west',
                       [BUTTON_NORTH, BUTTON_WEST], PRESS_SINGLE),
        0xF600: Action(0xF600, 'Multi North South', 'action_multi_north_south',
                       [BUTTON_NORTH, BUTTON_SOUTH], PRESS_SINGLE),
        0xF900: Action(0xF900, 'Multi East West', 'action_multi_east_west',
                       [BUTTON_EAST, BUTTON_WEST], PRESS_SINGLE),
        0xF500: Action(0xF500, 'Multi East South', 'action_multi_east_south',
                       [BUTTON_EAST, BUTTON_SOUTH], PRESS_SINGLE),
        0xF300: Action(0xF300, 'Multi West South', 'action_multi_west_south',
                       [BUTTON_WEST, BUTTON_SOUTH], PRESS_SINGLE),

        0xF800: Action(0xF800, 'Multi North East West',
                       'action_multi_north_east_west',
                       [BUTTON_NORTH, BUTTON_EAST, BUTTON_WEST], PRESS_SINGLE),
        0xF400: Action(0xF400, 'Multi North East South',
                       'action_multi_north_east_south',
                       [BUTTON_NORTH, BUTTON_EAST, BUTTON_SOUTH],
                       PRESS_SINGLE),
        0xF200: Action(0xF200, 'Multi North West South',
                       'action_multi_north_west_south',
                       [BUTTON_NORTH, BUTTON_WEST, BUTTON_SOUTH],
                       PRESS_SINGLE),
        0xF100: Action(0xF100, 'Multi East West South',
                       'action_multi_east_west_south',
                       [BUTTON_EAST, BUTTON_WEST, BUTTON_SOUTH], PRESS_SINGLE),

        0xF000: Action(0xF000, 'Multi North East West South',
                       'action_multi_north_east_west_south',
                       [BUTTON_NORTH, BUTTON_EAST, BUTTON_WEST, BUTTON_SOUTH],
                       PRESS_SINGLE),
    }

    def __init__(self,
                 address: Union[str, btle.ScanEntry],
                 handler: DefaultActionHandler = None,
                 debounce: bool = True,
                 listen: bool = False,
                 interface: int = None):
        """Connect to the Turn Touch remote.
        Set appropriate address type (overriding btle default).
        :param address Union[str, btle.ScanEntry]:
            MAC address (or btle.ScanEntry object) of this device
        :param debounce bool:
            Suppress single presses during a hold, double-tap or multi-press.
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
        self.handler = handler or DefaultActionHandler
        self.debounce = debounce
        self._combo_action = set()
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

    @property
    def battery(self) -> int:
        """Read the battery level (percentage) of this remote."""
        battery_bytes = self.getCharacteristics(
            uuid=self.BATTERY_LEVEL_CHARACTERISTIC_UUID)[0].read()
        logger.debug("Read device {address} battery level: '{battery}'".format(
            address=self.addr, battery=battery_bytes))
        return int.from_bytes(battery_bytes, byteorder='big')

    def listen_forever(self):
        """Listen for button press events indefinitely."""
        self.listen(only_one=False)

    def listen(self, only_one: bool = True):
        """Listen for a button press event.
        Will listen indefinitely if `only_one` is False."""
        self._enable_notifications()
        if self.debounce:
            self.executor = ThreadPoolExecutor(5)
        try:
            if only_one:
                self.waitForNotifications(0)
            else:
                while True:
                    self.waitForNotifications(0)
        except btle.BTLEException as e:
            raise TurnTouchException(e)
        self._enable_notifications(enable=False)

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
        """Handle callbacks for notifications from the device.
        This is an internal-use class. To handle button presses, you should
        subclass DefaultActionHandler, not this class."""
        def __init__(self, turn_touch):
            """Retain a reference to the parent TurnTouch object."""
            self.turn_touch = turn_touch

        def _handle_combo(self, action):
            """Handle an action immediately.
            This action may be the end of a complex press (double-tap or hold),
            so we record that. See _handle_single for the other side."""
            self.turn_touch._combo_action.add(action)
            self.handle_action(action)
            time.sleep(self.turn_touch.MAX_DELAY)
            self.turn_touch._combo_action.remove(action)

        def _handle_multi(self, action):
            """Handle a multi-button action.
            Occurs immediately, but we need to debounce because it can fire
            more than once."""
            for combo_action in self.turn_touch._combo_action:
                if combo_action.buttons.issuperset(action.buttons):
                    # This was already handled
                    logger.debug("Debounce Multi: ignoring action {action}."
                                 .format(action=action))
                    return
            # Not a duplicate; proceed
            self.turn_touch._combo_action.add(action)
            self.handle_action(action)
            time.sleep(self.turn_touch.MAX_DELAY)
            self.turn_touch._combo_action.remove(action)

        def _handle_off(self, action):
            """Handle the "Off' action
            Occurs with a delay, and we need to debounce because it can fire
            more than once."""
            if action in self.turn_touch._combo_action:
                logger.debug("Debounce Off: ignoring action {action}."
                             .format(action=action))
                return
            # Not a duplicate; proceed
            self.turn_touch._combo_action.add(action)
            time.sleep(self.turn_touch.MAX_DELAY)
            self.handle_action(action)
            self.turn_touch._combo_action.remove(action)

        def _handle_single(self, action):
            """Handle an action which may be the beginning of a complex press
            (double tap, or hold). Wait for further actions before handling."""
            time.sleep(self.turn_touch.MAX_DELAY)
            for combo_action in self.turn_touch._combo_action:
                if combo_action.buttons.issuperset(action.buttons):
                    # This button press was part of a combo; ignore it.
                    logger.debug("Debounce: ignoring action {action}."
                                 .format(action=action))
                    return
            # Apparently there was no combo, so handle the original action
            self.handle_action(action)

        def handle_action(self, action):
            """Actually invoke the handlers for this action."""
            # Call the generic (any button) callback.
            self.turn_touch.handler.action_any(action)
            # Call the button-specific callback
            getattr(self.turn_touch.handler, action.name)()

        def handleNotification(self, cHandle, data):
            """Call the appropriate button press handler method(s)."""
            logger.debug("Got notification {notification}".format(
                notification=data))
            type_int = int.from_bytes(data, byteorder='big')
            try:
                action = self.turn_touch.ACTIONS[type_int]
            except IndexError:
                raise TurnTouchException('Unknown notification received: {}'
                                         .format(data))
            if self.turn_touch.debounce:
                if action.is_combo:
                    self._handle_combo(action)
                elif action.is_multi:
                    logger.debug("Debounce: delaying action {action}.".format(
                        action=action))
                    self.turn_touch.executor.submit(
                        self._handle_multi, (action))
                elif action.is_off:
                    logger.debug("Debounce: delaying action {action}.".format(
                        action=action))
                    self.turn_touch.executor.submit(
                        self._handle_off, (action))
                else:
                    logger.debug("Debounce: delaying action {action}.".format(
                        action=action))
                    self.turn_touch.executor.submit(
                        self._handle_single, (action))
            else:
                self.handle_action(action)
