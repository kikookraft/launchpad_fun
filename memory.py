from launchpad import LaunchpadMK2
import time
import random


def generate_memory_chunk(
        level: int = 1) -> list[tuple[int, int]]:
    """
    Generate a list of `level` amount of random pads
    Returns a list of tuples (x, y) where x and y are
    the coordinates of the pads
    """
    pads: list[tuple[int, int]] = []
    while len(pads) < level:
        x = random.randint(0, 7)
        y = random.randint(1, 8)
        if (x, y) not in pads:
            pads.append((x, y))
    return pads


def display_memory_chunk(lp: LaunchpadMK2,
                         pads: list[tuple[int, int]],
                         color: tuple[int, int, int] = (255, 255, 255),
                         lives: int = 3):
    """
    Display the memory chunk on the Launchpad
    Pads is a list of tuples (x, y) where x and y are
    the coordinates of the pads
    """
    for x, y in pads:
        lp.set_xy(x, y, *color)
    show_lives(lp, lives)


def clear_memory_chunk(lp: LaunchpadMK2,
                       pads: list[tuple[int, int]]):
    """
    Clear the memory chunk on the Launchpad
    Pads is a list of tuples (x, y) where x and y are
    the coordinates of the pads
    """
    for x, y in pads:
        lp.set_xy(x, y, 0, 0, 0)


def check_input(correct_pads: list[tuple[int, int]], lp: LaunchpadMK2,
                lives: int = 3) -> bool:
    """
    Check if the user pressed the correct pads
    Returns True if all correct pads were pressed, False otherwise

    Light up all pad that the user pressed, in green if in the correct pads,
    in red if not in the correct pads
    At the first red, blink all the correct pads in green for 1 second,
    then clear all pads and return False
    If all correct pads were pressed, blink all the correct pads in green for
    1 second, then clear all pads and return True
    """
    pressed_pads: list[tuple[int, int]] = []
    lp.clear_events()
    show_lives(lp, lives)
    while len(pressed_pads) < len(correct_pads):
        lp.update()  # fetch all pending events
        event = lp.get_pressed()
        if event is None:
            continue
        x, y = event
        if (x, y) in pressed_pads:
            continue
        pressed_pads.append((x, y))
        if (x, y) in correct_pads:
            lp.set_xy(x, y, 255, 255, 255)
        else:
            lp.set_xy(x, y, 255, 0, 0)
            display_memory_chunk(lp, correct_pads, color=(0, 255, 0), lives=lives)
            time.sleep(1)
            lp.clear()
            return False

    display_memory_chunk(lp, correct_pads, color=(0, 255, 0), lives=lives)
    time.sleep(.5)
    lp.clear()
    show_lives(lp, lives)
    return True


def show_lives(lp: LaunchpadMK2, lives: int):
    """
    Show the number of lives left on the Launchpad
    Lives is an integer between 0 and 3
    """
    for i in range(lives):
        lp.set_xy(i, 0, 0, 255, 0)
    for i in range(lives, 8):
        lp.set_xy(i, 0, 255, 0, 0)


def main():
    lp = LaunchpadMK2()
    lp.clear()
    level = 1
    lives = 8
    show_lives(lp, lives)
    while True:
        pads = generate_memory_chunk(level)
        display_memory_chunk(lp, pads, lives=lives)
        time.sleep(.5 + (level * 0.1))
        lp.clear()
        if check_input(pads, lp, lives=lives):
            level += 1
        else:
            lives -= 1
            if lives == 0:
                print("Game Over")
                level = 1
                lives = 3


if __name__ == "__main__":
    main()
