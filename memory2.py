from launchpad import LaunchpadMK2
from typing import TypedDict
import time
import random


class PadEntry(TypedDict):
    """A single step in the memory sequence: a pad group and its colour."""
    pads: list[tuple[int, int]]
    color: tuple[int, int, int]


class MemoryPads:
    """Class representing the memory pads in the game.
    Can be divided into 2x2 / 3x3 / 4x4 / 8x8."""
    def __init__(self, difficulty: int = 1):
        self.difficulty = difficulty
        self.pad_list: list[PadEntry] = []

    def get_pads(self) -> list[list[tuple[int, int]]]:
        """Generate a list of pads based on the current level and difficulty."""
        if self.difficulty == 1:  # groups of 3 pads
            return [
                [
                    (0, 1), (0, 2), (0, 3),
                    (1, 1), (1, 2), (1, 3),
                    (2, 1), (2, 2), (2, 3)
                ],
                [
                    (5, 1), (5, 2), (5, 3),
                    (6, 1), (6, 2), (6, 3),
                    (7, 1), (7, 2), (7, 3)
                ],
                [
                    (0, 6), (0, 7), (0, 8),
                    (1, 6), (1, 7), (1, 8),
                    (2, 6), (2, 7), (2, 8)
                ],
                [
                    (5, 6), (5, 7), (5, 8),
                    (6, 6), (6, 7), (6, 8),
                    (7, 6), (7, 7), (7, 8)
                ]
            ]
        if self.difficulty == 2:  # groups of 2 pads (3x3 grid)
            return [
                [
                    (0, 1), (0, 2),
                    (1, 1), (1, 2)
                ],
                [
                    (3, 1), (3, 2),
                    (4, 1), (4, 2)
                ],
                [
                    (6, 1), (6, 2),
                    (7, 1), (7, 2)
                ],
                [
                    (0, 4), (0, 5),
                    (1, 4), (1, 5)
                ],
                [
                    (3, 4), (3, 5),
                    (4, 4), (4, 5)
                ],
                [
                    (6, 4), (6, 5),
                    (7, 4), (7, 5)
                ],
                [
                    (0, 7), (0, 8),
                    (1, 7), (1, 8)
                ],
                [
                    (3, 7), (3, 8),
                    (4, 7), (4, 8)
                ],
                [
                    (6, 7), (6, 8),
                    (7, 7), (7, 8)
                ]
            ]
        if self.difficulty == 3:  # groups of 2 pad (4x4 grid)
            return [
                [
                    (0, 1), (0, 2),
                    (1, 1), (1, 2)
                ],
                [
                    (2, 1), (2, 2),
                    (3, 1), (3, 2)
                ],
                [
                    (4, 1), (4, 2),
                    (5, 1), (5, 2)
                ],
                [
                    (6, 1), (6, 2),
                    (7, 1), (7, 2)
                ],
                [
                    (0, 3), (0, 4),
                    (1, 3), (1, 4)
                ],
                [
                    (2, 3), (2, 4),
                    (3, 3), (3, 4)
                ],
                [
                    (4, 3), (4, 4),
                    (5, 3), (5, 4)
                ],
                [
                    (6, 3), (6, 4),
                    (7, 3), (7, 4)
                ],
                [
                    (0, 5), (0, 6),
                    (1, 5), (1, 6)
                ],
                [
                    (2, 5), (2, 6),
                    (3, 5), (3, 6)
                ],
                [
                    (4, 5), (4, 6),
                    (5, 5), (5, 6)
                ],
                [
                    (6, 5), (6, 6),
                    (7, 5), (7, 6)
                ],
                [
                    (0, 7), (0, 8),
                    (1, 7), (1, 8)
                ],
                [
                    (2, 7), (2, 8),
                    (3, 7), (3, 8)
                ],
                [
                    (4, 7), (4, 8),
                    (5, 7), (5, 8)
                ],
                [
                    (6, 7), (6, 8),
                    (7, 7), (7, 8)
                ]
            ]
        else:  # groups of 1 pad (8x8 grid)
            return [[(x, y)] for x in range(8) for y in range(1, 9)]

    def change_difficulty(self, new_difficulty: int):
        """Change the difficulty level of the memory pads."""
        if new_difficulty not in [1, 2, 3, 4]:
            raise ValueError("Difficulty must be between 1 and 4")
        self.difficulty = new_difficulty

    def add_random_pad(self):
        """Add a new random pad group to the memory sequence."""
        group = random.choice(self.get_pads())
        color = (random.randint(50, 255), random.randint(50, 255),
                 random.randint(50, 255))
        self.pad_list.append({"pads": group, "color": color})


class MemoryGame:
    def __init__(self, lp: LaunchpadMK2, lives: int = 3, difficulty: int = 1):
        self.lp: LaunchpadMK2 = lp
        self.lives = lives
        self.starting_lives = lives
        self.level = 1
        self.pads = MemoryPads(difficulty=difficulty)

    def show_lives(self):
        """Display the remaining lives on the Launchpad."""
        for i in range(3):
            if i < self.lives:
                self.lp.set_top_button(i, 0, 255, 0)  # Green for remaining lives
            else:
                self.lp.set_top_button(i, 255, 0, 0)    # Red for lost lives

    def wait_user(self, timeout: float = 0, lit = False) -> tuple[int, int] | None:
        """
        Wait for the user to press any pad and return the coordinates of the pad pressed
        """
        self.lp.update()  # fetch all pending events
        self.lp.clear_events()
        if not timeout:
            self.lp.clear()
        last_update = time.time()
        status = False
        while True:
            self.lp.update()  # fetch all pending events
            event = self.lp.get_pressed()
            if time.time() - last_update > 0.1 and not timeout and lit:
                status = not status
                last_update = time.time()
                if status:
                    self.lp.set_xy(8, 8, 0, 0, 255)
                else:
                    self.lp.set_xy(8, 8, 0, 0, 0)
            if event is not None or (timeout and time.time() - last_update > timeout):
                break
        if not lit:
            self.lp.set_xy(8, 8, 0, 0, 0)
        return event

    def lit_pads(self, pads: list[tuple[int, int]], color: tuple[int, int, int]):
        """Light up the specified pads with the given color."""
        for pad in pads:
            self.lp.set_xy(pad[0], pad[1], color[0], color[1], color[2])

    def blink_pads(self,
                   pads: list[tuple[int, int]],
                   color: tuple[int, int, int],
                   times: int = 1,
                   interval: float = 0.6,
                   after_blink: bool = False):
        """Blink the specified pads with the given color for a number of times."""
        for _ in range(times):
            self.lit_pads(pads, color)
            time.sleep(interval)
            self.lit_pads(pads, (0, 0, 0))  # Turn off
            if after_blink:
                time.sleep(interval)

    def convert_pad_coord(self, pad: tuple[int, int]) -> list[tuple[int, int]] | None:
        """Return the pad group containing the pressed pad, or None if not playable."""
        for pad_group in self.pads.get_pads():
            if pad in pad_group:
                return pad_group
        return None

    def play_sequence(self, interval: float = 0.6):
        """Play the memory sequence, lighting each pad group in turn."""
        for entry in self.pads.pad_list:
            pads = entry["pads"]
            color = entry["color"]
            self.lit_pads(pads, color)
            time.sleep(interval)
            self.lit_pads(pads, (0, 0, 0))  # Turn off

    def show_difficulty(self):
        """Show the current difficulty level by lighting up the corresponding pads."""
        for elem in self.pads.get_pads():
            self.lit_pads(elem, (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)))  # Show new pattern in blue

    def show_menu(self):
        """Show the menu for changing difficulty and starting the game."""
        self.lp.clear()
        for i in range(4):
            if i == self.pads.difficulty - 1:
                self.lp.set_top_button(i, 255, 0, 255)
            else:
                self.lp.set_top_button(i, 0, 0, 255)
        self.lp.set_top_button(7, 0, 255, 0)  # Start Game
        self.show_difficulty()

    def change_difficulty(self, new_difficulty: int):
        """Change the difficulty level of the memory game."""
        self.pads.change_difficulty(new_difficulty)
        self.show_menu()

    def check_input(self, timeout: float = 0) -> bool:
        """Read the user's pads and compare them to the sequence, in order.

        Returns True only if the full sequence was reproduced correctly.
        Presses that land while a pad is flashing are kept for the next step,
        so a fast player can speedrun the sequence.
        """
        self.lp.update()
        self.lp.clear_events()
        start_time = time.time()
        index = 0
        while index < len(self.pads.pad_list):
            self.lp.update()  # fetch all pending events
            event = self.lp.get_pressed()
            if event is not None:
                pad_group = self.convert_pad_coord((event[0], event[1]))
                if pad_group is not None:
                    if pad_group == self.pads.pad_list[index]["pads"]:
                        # Flash green; stop early if the next pad is pressed.
                        self.lit_pads(pad_group, (0, 255, 0))
                        self.wait_flash(0.3)
                        self.lit_pads(pad_group, (0, 0, 0))
                        index += 1
                    else:
                        # Flash red, then clear before replaying the sequence.
                        self.lit_pads(pad_group, (255, 0, 0))
                        time.sleep(0.3)
                        self.lit_pads(pad_group, (0, 0, 0))
                        return False
            if timeout and time.time() - start_time > timeout:
                return False
            time.sleep(0.05)
        return True

    def wait_flash(self, duration: float = 0.3):
        """Wait up to `duration` seconds, returning early if a pad is pressed.

        The press is left in the event queue so check_input can read it.
        """
        deadline = time.time() + duration
        while time.time() < deadline:
            self.lp.update()
            if self.lp.pressed:
                return
            time.sleep(0.01)

    def game_loop(self):
        """Main game loop for the memory game."""
        self.lp.clear()
        # Reset state for a fresh game.
        self.lives = self.starting_lives
        self.level = 1
        self.pads.pad_list = []
        self.show_lives()
        while self.lives > 0:
            self.pads.add_random_pad()  # extend the sequence only on a new round
            correct = False
            while not correct and self.lives > 0:
                # Replay the whole sequence each attempt.
                interval = 1.5 * (5 / (self.level * 8)) + 0.2
                self.play_sequence(interval=interval)
                if self.check_input(timeout=5.0+(self.level * 0.5)):
                    correct = True
                    self.level += 1
                    print(f"Level {self.level} reached!")
                else:
                    self.lives -= 1
                    self.show_lives()
        print(f"Game over! Level {self.level}, Score: {self.level * self.pads.difficulty * 10}")


if __name__ == "__main__":
    lp = LaunchpadMK2()
    lp.clear()
    game = MemoryGame(lp, lives=3, difficulty=1)
    game.show_menu()
    try:
        while True:
            lp.update()
            event = lp.get_pressed()
            if event is not None:
                if event[1] == 0:  # Top buttons for difficulty and start
                    if event[0] in [0, 1, 2, 3]:  # Difficulty buttons
                        game.change_difficulty(event[0] + 1)
                    elif event[0] == 7:  # Start game button
                        game.game_loop()
                        game.show_menu()
    except KeyboardInterrupt:
        lp.clear()
        print("Exiting game.")
