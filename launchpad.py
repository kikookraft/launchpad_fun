#!/usr/bin/env python3
"""
launchpad_mk2.py - Full RGB control for Novation Launchpad MK2.

Methods added:
    fill_all(r,g,b)      -> all 112 LEDs
    fill_row(y, r,g,b)   -> row y (0=top, 8=bottom)
    fill_col(x, r,g,b)   -> column x (0..8, but row0 lacks x=8)
"""

import rtmidi
import time
import sys

class LaunchpadMK2:
    """Launchpad MK2 controller with full RGB SysEx support and event queue."""

    NUM_LEDS = 112

    def __init__(self, input_port=None, output_port=None, auto_open=True, return_coords=True):
        self.return_coords = return_coords
        self._event_queue = []
        self.midi_in = None
        self.midi_out = None
        self.input_port_index = None
        self.output_port_index = None
        if auto_open:
            self.open(input_port, output_port)

    def open(self, input_port=None, output_port=None):
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
        if not (0 <= y <= 8):
            raise ValueError("y must be 0-8")
        if y == 0:
            if not (0 <= x <= 7):
                raise ValueError("Row 0 (top) has no button at x=8, use x=0-7")
            return 104 + x
        else:
            if not (0 <= x <= 8):
                raise ValueError("x must be 0-8 for rows 1-8")
            base = 91 - 10 * y
            return base + x

    def xy_from_led(self, led):
        if not (0 <= led < self.NUM_LEDS):
            raise ValueError(f"LED {led} out of range")
        if 104 <= led <= 111:
            return (led - 104, 0)
        for y in range(1, 9):
            base = 91 - 10 * y
            if base <= led <= base + 8:
                return (led - base, y)
        raise ValueError(f"LED {led} is not a grid or top button")

    def set_xy(self, x, y, r, g, b):
        led = self.led_from_xy(x, y)
        self.set_led(led, r, g, b)

    # ----- Convenience methods -----
    def set_grid(self, row, col, r, g, b):
        y = 8 - row
        x = col
        self.set_xy(x, y, r, g, b)

    def set_top_button(self, index, r, g, b):
        self.set_xy(index, 0, r, g, b)

    def clear(self):
        for led in range(self.NUM_LEDS):
            self.midi_out.send_message([0xF0, 0x00, 0x20, 0x29, 0x02, 0x18, 0x0B, led, 0, 0, 0, 0xF7])
        time.sleep(0.01)

    def reset(self):
        self._send_programmer_mode()
        self.clear()

    # ----- Fill methods (NEW) -----
    def fill_all(self, r, g, b):
        """Set all 112 LEDs to the same RGB colour."""
        for led in range(self.NUM_LEDS):
            self.set_led(led, r, g, b)

    def fill_row(self, y, r, g, b):
        """
        Fill a whole row with one colour.
        y: 0 = top round buttons, 1..8 = grid rows.
        For y=0: fills x=0..7; for y>=1: fills x=0..8.
        """
        if y == 0:
            for x in range(8):
                self.set_xy(x, y, r, g, b)
        else:
            for x in range(9):
                self.set_xy(x, y, r, g, b)

    def fill_col(self, x, r, g, b):
        """
        Fill a whole column with one colour.
        x: 0..7 -> fills y=0..8 (all rows)
        x: 8 -> fills y=1..8 (grid only, since row 0 has no x=8)
        """
        if x == 8:
            for y in range(1, 9):
                self.set_xy(x, y, r, g, b)
        else:
            for y in range(9):
                self.set_xy(x, y, r, g, b)

    # ----- Event Queue -----
    def update(self):
        while True:
            msg = self.midi_in.get_message()
            if not msg:
                break
            data, _ = msg
            if not data:
                continue
            status = data[0] & 0xF0
            if status == 0x90:
                if len(data) >= 3:
                    led = data[1]
                    velocity = data[2]
                    if led < self.NUM_LEDS and velocity > 0:
                        self._event_queue.append(led)
            elif status == 0xB0:
                if len(data) >= 3:
                    controller = data[1]
                    value = data[2]
                    if 104 <= controller <= 111 and value == 0x7F:
                        self._event_queue.append(controller)

    @property
    def pressed(self):
        return len(self._event_queue) > 0

    def get_pressed(self):
        if not self._event_queue:
            return None
        led = self._event_queue.pop(0)
        if self.return_coords:
            try:
                return self.xy_from_led(led)
            except ValueError:
                return led
        else:
            return led

    def clear_events(self):
        self._event_queue.clear()

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
                            led = data[1]
                            velocity = data[2]
                            if led < self.NUM_LEDS:
                                pressed = velocity > 0
                                if pressed or include_release:
                                    callback(led, pressed)
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


# ----- Demo (with fill methods) -----
if __name__ == "__main__":
    print("Launchpad MK2 Fill Demo")
    print("Testing fill methods...")

    lp = LaunchpadMK2()
    lp.clear()

    # Fill all pads with a dim blue
    print("Filling all pads with blue (0,0,50)")
    lp.fill_all(0, 0, 50)
    time.sleep(2)

    # Fill row 0 (top buttons) with red
    print("Filling top row with red")
    lp.fill_row(0, 255, 0, 0)
    time.sleep(1)

    # Fill row 4 with green
    print("Filling middle row (y=4) with green")
    lp.fill_row(4, 0, 255, 0)
    time.sleep(1)

    # Fill column 4 with yellow
    print("Filling middle column (x=4) with yellow")
    lp.fill_col(4, 255, 255, 0)
    time.sleep(1)

    # Fill column 8 (rightmost) with magenta
    print("Filling rightmost column (x=8) with magenta")
    lp.fill_col(8, 255, 0, 255)
    time.sleep(2)

    # Clear all
    lp.clear()
    print("Done.")
    lp.close()