"""
Scan nearby Bluetooth Low Energy (BLE) devices and list them by signal strength.

RSSI (Received Signal Strength Indicator) is measured in dBm: values closer to
zero mean a stronger signal and, usually, a closer device (about -40 dBm is a
few centimetres away; below -90 dBm is the edge of the range).

Reference:
    https://en.wikipedia.org/wiki/Bluetooth_Low_Energy
    https://en.wikipedia.org/wiki/Received_signal_strength_indicator

Requirements:
    pip install bleak

Usage:
    python3 other/scan_bluetooth.py

Notes:
    * Only BLE devices are found; Bluetooth Classic-only devices do not answer.
    * Many devices advertise without a name.
    * On macOS the address is a UUID, and many phones rotate their address
      periodically for privacy.
"""

import asyncio
from typing import Iterable, List, Optional, Tuple

# (address, rssi, name)
Device = Tuple[str, int, Optional[str]]


def sort_by_rssi(devices: Iterable[Device]) -> List[Device]:
    """
    Sort devices from the strongest (closest) signal to the weakest.

    >>> sort_by_rssi([("AA", -80, "far"), ("BB", -40, "near"), ("CC", -60, None)])
    [('BB', -40, 'near'), ('CC', -60, None), ('AA', -80, 'far')]
    >>> sort_by_rssi([])
    []
    """
    return sorted(devices, key=lambda device: device[1], reverse=True)


def format_devices(devices: Iterable[Device]) -> str:
    """
    Build a table of devices, closest first.

    >>> print(format_devices([("AA:BB", -70, None), ("CC:DD", -45, "Headset")]))
    Address                                      RSSI  Name
    ----------------------------------------------------------------------
    CC:DD                                     -45 dBm  Headset
    AA:BB                                     -70 dBm  (no name)
    <BLANKLINE>
    Total: 2 device(s).
    >>> print(format_devices([]))
    Address                                      RSSI  Name
    ----------------------------------------------------------------------
    <BLANKLINE>
    Total: 0 device(s).
    """
    ordered = sort_by_rssi(devices)
    lines = [f"{'Address':<40} {'RSSI':>8}  Name", "-" * 70]
    for address, rssi, name in ordered:
        signal = f"{rssi} dBm"
        lines.append(f"{address:<40} {signal:>8}  {name or '(no name)'}")
    lines.append(f"\nTotal: {len(ordered)} device(s).")
    return "\n".join(lines)


async def scan(timeout: float = 10.0) -> List[Device]:
    """
    Scan for BLE devices for `timeout` seconds (requires a Bluetooth adapter).
    """
    from bleak import BleakScanner

    found = await BleakScanner.discover(timeout=timeout, return_adv=True)
    return [
        (device.address, adv.rssi, device.name or adv.local_name)
        for device, adv in found.values()
    ]


if __name__ == "__main__":
    seconds = 10.0
    print(f"Scanning for Bluetooth LE devices for {seconds:.0f} seconds...\n")
    print(format_devices(asyncio.run(scan(seconds))))
