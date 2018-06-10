# TurnTouch Python library

This library provides support for the [Turn Touch](https://shop.turntouch.com/)
bluetooth smart home remote.

It is written in Python 3, originally for use with [Home Assistant](https://www.home-assistant.io/).

# Status

This is currently pre-alpha status. It is not usable.

# Usage

## Scanning for Turn Touch devices

```python
import turntouch

# Example 1: Find all devices
devices = turntouch.scan()

# Example 2: Find just one device
device = turntouch.scan(only_one=True)[0]

# Example 3: Extend scan timeout to 60 seconds (default is 10)
devices = turntouch.scan(timeout=60)
```

`turntouch.scan()` returns a list of `turntouch.TurnTouch` objects.

## Interacting with a Turn Touch device

`turntouch.TurnTouch` is a subclass of
[`bluepy.btle.Peripheral`](http://ianharvey.github.io/bluepy-doc/peripheral.html).
