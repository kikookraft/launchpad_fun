#!/usr/bin/env python3
"""
launchpad_mk2.py - Full RGB control for Novation Launchpad MK2.

Coordinate system (for method set_xy and led_from_xy):
- x: 0 = left, 8 = right (max 8, but row 0 lacks x=8)
- y: 0 = top row (round buttons), 8 = bottom row (grid row 7)
- Row 0: x=0..7 valid
- Rows 1..8: x=0..8 valid

Usage:
    import launchpad_mk2
    lp = launchpad_mk2.LaunchpadMK2()
    lp.set_xy(0, 0, 255, 0, 0)   # top-left round button -> red
    lp.set_xy(8, 8, 0, 255, 0)   # bottom-right pad -> green
    lp.clear()
    lp.close()
"""

import rtmidi
import time


class LaunchpadMK2:
    """Launchpad MK2 controller with full RGB SysEx support."""

    NUM_LEDS = 112

    def __init__(self, input_port=None, output_port=None, auto_open=True):
        self.midi_in = None
        self.midi_out = None
        self.input_port_index = None
        self.output_port_index = None
        if auto_open:
            self.open(input_port, output_port)

    def open(self,
             input_port: int | None = None,
             output_port: int | None = None):
        self.midi_in = rtmidi.MidiIn()
        self.midi_out = rtmidi.MidiOut()
        in_ports = self.midi_in.get_ports()
        out_ports = self.midi_out.get_ports()
        if not in_ports or not out_ports:
            raise RuntimeError("No MIDI ports found")

        def find_port(ports, name_substring="Launchpad MK2"):
            for i, name in enumerate(ports):
                if name_substring in name:
                    return i
            return None

        if input_port is None:
            self.input_port_index = find_port(in_ports)
            if self.input_port_index is None:
                raise RuntimeError("Launchpad MK2 not found in input ports")
        else:
            self.input_port_index = input_port

        if output_port is None:
            self.output_port_index = find_port(out_ports)
            if self.output_port_index is None:
                raise RuntimeError("Launchpad MK2 not found in output ports")
        else:
            self.output_port_index = output_port

        self.midi_in.open_port(self.input_port_index)
        self.midi_out.open_port(self.output_port_index)
        self._send_programmer_mode()
        self.clear()

    def close(self):
        if self.midi_in:
            self.midi_in.close_port()
        if self.midi_out:
            self.midi_out.close_port()

    def _send_sysex(self, data):
        self.midi_out.send_message(data)
        time.sleep(0.005)

    def _send_programmer_mode(self):
        self._send_sysex([0xF0, 0x00, 0x20, 0x29, 0x02, 0x18, 0x0F, 0x00, 0xF7])

    def set_led(self, led, r, g, b):
        if not (0 <= led < self.NUM_LEDS):
            raise ValueError(f"LED index {led} out of range (0-{self.NUM_LEDS-1})")
        r6 = int(r / 255 * 63)
        g6 = int(g / 255 * 63)
        b6 = int(b / 255 * 63)
        sysex = [0xF0, 0x00, 0x20, 0x29, 0x02, 0x18, 0x0B, led, r6, g6, b6, 0xF7]
        self._send_sysex(sysex)

    # ----- Coordinate mapping (9 rows, 9 columns; top row lacks x=8) -----
    def led_from_xy(self, x, y):
        """
        Convert coordinate (x, y) to LED index.
        - x: 0-8, y: 0-8
        - If y==0, x must be 0-7 (no button at 8,0)
        - Rows 1-8: x=0-8 valid
        """
        if not (0 <= y <= 8):
            raise ValueError("y must be 0-8")
        if y == 0:
            if not (0 <= x <= 7):
                raise ValueError("Row 0 (top) has no button at x=8, use x=0-7")
            return 104 + x
        else:
            if not (0 <= x <= 8):
                raise ValueError("x must be 0-8 for rows 1-8")
            base = 91 - 10 * y   # yields 81,71,61,51,41,31,21,11 for y=1..8
            return base + x

    def xy_from_led(self, led):
        """
        Convert LED index to (x, y) coordinate.
        Returns (x, y) or raises ValueError if LED is not in the mapped range.
        """
        if not (0 <= led < self.NUM_LEDS):
            raise ValueError(f"LED {led} out of range")
        if 104 <= led <= 111:
            return (led - 104, 0)
        # Check rows 1-8: ranges 81-89, 71-79, ..., 11-19
        for y in range(1, 9):
            base = 91 - 10 * y
            if base <= led <= base + 8:
                return (led - base, y)
        raise ValueError(f"LED {led} is not a grid or top button (maybe side button?)")

    def set_xy(self, x, y, r, g, b):
        """
        Set a button by coordinate (x, y) to an RGB colour.
        """
        led = self.led_from_xy(x, y)
        self.set_led(led, r, g, b)

    # ----- Convenience methods -----
    def set_grid(self, row, col, r, g, b):
        """
        Legacy: row 0-7 (bottom), col 0-7 (left). Internally uses xy mapping.
        """
        # Convert legacy row/col to our x,y: row 0 bottom -> y=8-row? Actually our y=0 top.
        # We'll keep it simple: map row 0 to y=8, row 7 to y=1.
        y = 8 - row
        x = col  # columns same
        self.set_xy(x, y, r, g, b)

    def set_top_button(self, index, r, g, b):
        """Legacy: index 0-7 left to right."""
        self.set_xy(index, 0, r, g, b)

    def clear(self):
        for led in range(self.NUM_LEDS):
            self.midi_out.send_message([0xF0, 0x00, 0x20, 0x29, 0x02, 0x18, 0x0B, led, 0, 0, 0, 0xF7])
        time.sleep(0.01)

    def reset(self):
        self._send_programmer_mode()
        self.clear()

    # ----- Event handling -----
    def run(self, callback, include_release=False):
        try:
            while True:
                msg = self.midi_in.get_message()
                if msg:
                    data, _ = msg
                    if not data:
                        continue
                    status = data[0] & 0xF0
                    if status == 0x90:
                        if len(data) >= 3:
                            note = data[1]
                            velocity = data[2]
                            if note < self.NUM_LEDS:
                                pressed = velocity > 0
                                if pressed or include_release:
                                    callback(note, pressed)
                    elif status == 0xB0:
                        if len(data) >= 3:
                            controller = data[1]
                            value = data[2]
                            if 104 <= controller <= 111:
                                pressed = value == 0x7F
                                if pressed or include_release:
                                    callback(controller, pressed)
                time.sleep(0.001)
        except KeyboardInterrupt:
            print("\n[Launchpad] Exiting event loop...")
            self.clear()
            self.close()

    def poll(self):
        msg = self.midi_in.get_message()
        if not msg:
            return None
        data, _ = msg
        if not data:
            return None
        status = data[0] & 0xF0
        if status == 0x90:
            if len(data) >= 3:
                note = data[1]
                velocity = data[2]
                if note < self.NUM_LEDS:
                    return note, velocity > 0
        elif status == 0xB0:
            if len(data) >= 3:
                controller = data[1]
                value = data[2]
                if 104 <= controller <= 111:
                    return controller, value == 0x7F
        return None


# ----- Demo -----
if __name__ == "__main__":
    print("Launchpad MK2 Demo with coordinate mapping")
    print("Press any button; it will light up with a random colour.")
    print("Coordinates will be printed.")
    print("Press Ctrl+C to exit.\n")

    lp = LaunchpadMK2()
    lp.clear()

    def on_press(led, pressed):
        if pressed:
            try:
                x, y = lp.xy_from_led(led)
            except ValueError:
                print(f"LED {led} not in mapped range, skipping")
                return
            import random
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            lp.set_led(led, r, g, b)
            print(f"LED {led} -> coord ({x},{y})  RGB({r},{g},{b})")

    lp.run(on_press)