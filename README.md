# TurnTouch Python library

This library provides support for the [Turn Touch](https://shop.turntouch.com/)
bluetooth smart home remote.

It is written in Python 3, originally for use with [Home Assistant](https://www.home-assistant.io/).

# Usage

Install this library from PyPI:

```
pip install TurnTouch
```

## Scanning for Turn Touch devices

**Note:** Scanning requires root privileges on Linux. To avoid this, skip
to the next section and connect to the device without scanning.

```python
import turntouch

# Example 1: Find all devices
devices = turntouch.scan()

# Example 2: Find just one device
device = turntouch.scan(only_one=True)[0]

# Example 3: Extend scan timeout to 60 seconds (default is 10)
devices = turntouch.scan(timeout=60)
```

`turntouch.scan()` returns a list of `turntouch.TurnTouch` objects. A connection
is automatically opened to each device, so it is ready to use.

`turntouch.TurnTouch` is a subclass of
[`bluepy.btle.Peripheral`](http://ianharvey.github.io/bluepy-doc/peripheral.html).

## Interacting with a Turn Touch device

```python
import turntouch

# Connect to a device by MAC address
tt = turntouch.TurnTouch('c0:ff:ee:c0:ff:ee')

# Read the device nickname and battery percentage
print("Name: {}\nBattery: {}".format(tt.name, tt.battery))

# Update the device nickname (max. 32 characters)
tt.name = 'Living Room Remote'
```

## Listening for button presses

```python
from turntouch import TurnTouch, DefaultActionHandler

class MyHandler(DefaultActionHandler):
    def action_north(self):
        print("Up button pressed.")
    def action_east_double_tap(self):
        print("Right button double-tapped.")
    def action_south_hold(self):
        print("Down button held.")

tt = TurnTouch('c0:ff:ee:c0:ff:ee')
tt.handler = MyHandler()
tt.listen_forever()

# One-liner alternative (same as listen_forever)
TurnTouch('c0:ff:ee:c0:ff:ee', handler=MyHandler(), listen=True)
```

## More advanced usage

Here's a more complex example, triggering some existing functions.

```python
import turntouch

# Define a handler
class MyFancyHandler(turntouch.DefaultActionHandler):

    def __init__(some_object, other_function):
        """Use the __init__ method to pass references to parts of your code,
        such as objects, methods, or variables."""
        self.thing_1 = some_object
        self.other_func = other_function

    def action_any(action):
        """Special handler which is fired for ALL actions.
        `action` is an instance of turntouch.Action."""
        if action.name == "North":
            self.thing_1.some_method()
        elif action.name in ["South", "East", "West"]:
            self.thing_1.other_method()
        else:
            self.other_func()

    def action_south_hold():
        print("You can combine per-button handlers with action_any!")


# Instantiate the handler, passing some application data into it
my_handler = MyFancyHandler(some_object_from_my_application, a_function)

# Scan until we find a device
devices = []
while not devices:
    devices = turntouch.scan(only_one=True)
tt = devices[0]

# Assign the handler to your device.
tt.handler = my_handler

tt.listen_forever()
```

## Listening for just one button press

If you don't want the listener to run forever, do this:

```python
tt = TurnTouch('c0:ff:ee:c0:ff:ee', handler=SomeHandler)
tt.listen()  # Will return as soon as one action occurs.
```

## Error handling

Connection failures will raise `turntouch.TurnTouchException`. You may want to
catch and ignore this exception to retry connecting.
