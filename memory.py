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
                lives: int = 3,
                additional_pad: tuple[int, int] = None) -> bool:
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
    pressed_pads: list[tuple[int, int]] = [additional_pad] if additional_pad else []
    lp.update()  # fetch all pending events
    # lp.clear_events()
    show_lives(lp, lives)
    # check pre pressed pad
    if additional_pad:
        x, y = additional_pad
        if (x, y) in correct_pads:
            lp.set_xy(x, y, 255, 255, 255)
        else:
            missing_pad = [pad for pad in correct_pads if pad not in pressed_pads]
            lp.set_xy(x, y, 255, 0, 0)
            display_memory_chunk(lp, missing_pad, color=(0, 255, 0), lives=lives)
            time.sleep(.2)
            clear_memory_chunk(lp, missing_pad)
            time.sleep(.2)
            display_memory_chunk(lp, missing_pad, color=(0, 255, 0), lives=lives)
            time.sleep(.2)
            clear_memory_chunk(lp, missing_pad)
            time.sleep(.2)
            display_memory_chunk(lp, missing_pad, color=(0, 255, 0), lives=lives)
            time.sleep(.2)
            clear_memory_chunk(lp, missing_pad)
            time.sleep(.2)
            display_memory_chunk(lp, missing_pad, color=(0, 255, 0), lives=lives)
            time.sleep(.2)
            clear_memory_chunk(lp, missing_pad)
            clear_memory_chunk(lp, pressed_pads)
            time.sleep(.2)
            lp.set_xy(x, y, 0, 0, 0)
            lp.clear_events()
            return False
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
            missing_pad = [pad for pad in correct_pads if pad not in pressed_pads]
            lp.set_xy(x, y, 255, 0, 0)
            display_memory_chunk(lp, missing_pad, color=(0, 255, 0), lives=lives)
            time.sleep(.2)
            clear_memory_chunk(lp, missing_pad)
            time.sleep(.2)
            display_memory_chunk(lp, missing_pad, color=(0, 255, 0), lives=lives)
            time.sleep(.2)
            clear_memory_chunk(lp, missing_pad)
            time.sleep(.2)
            display_memory_chunk(lp, missing_pad, color=(0, 255, 0), lives=lives)
            time.sleep(.2)
            clear_memory_chunk(lp, missing_pad)
            time.sleep(.2)
            display_memory_chunk(lp, missing_pad, color=(0, 255, 0), lives=lives)
            time.sleep(.2)
            clear_memory_chunk(lp, missing_pad)
            clear_memory_chunk(lp, pressed_pads)
            time.sleep(.2)
            lp.set_xy(x, y, 0, 0, 0)
            lp.clear_events()
            return False

    display_memory_chunk(lp, correct_pads, color=(0, 255, 0), lives=lives)
    time.sleep(.5)
    clear_memory_chunk(lp, correct_pads)
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


def wait_user(lp: LaunchpadMK2, timeout: float = 0):
    """
    Wait for the user to press any pad and return the coordinates of the pad pressed
    """
    lp.update()  # fetch all pending events
    lp.clear_events()
    if not timeout:
        lp.clear()
    last_update = time.time()
    status = False
    while True:
        lp.update()  # fetch all pending events
        event = lp.get_pressed()
        if time.time() - last_update > 0.1 and not timeout:
            status = not status
            last_update = time.time()
            if status:
                lp.set_xy(8, 8, 0, 0, 255)
            else:
                lp.set_xy(8, 8, 0, 0, 0)
        if event is not None or (timeout and time.time() - last_update > timeout):
            break
    if not timeout:
        for x in range(8):
            lp.set_xy(x, 0, 0, 255, 0)
            time.sleep(.05)
    return event


def game_loop(lp: LaunchpadMK2) -> int:
    lp.clear()
    level = 1
    lives = 8
    show_lives(lp, lives)
    stats = {}
    while True:
        pads = generate_memory_chunk(level)
        display_memory_chunk(lp, pads, lives=lives)
        pressed_pad = wait_user(lp, timeout=.5 + (level * 0.1))
        clear_memory_chunk(lp, pads)
        press_time = time.time()
        if check_input(pads, lp, lives=lives, additional_pad=pressed_pad):
            print(f"Level {level} completed in {round((time.time() - press_time) * 1000)} ms")
            stats[f"Level {level}"] = {"status": "completed", "time": time.time() - press_time}
            level += 1
        else:
            print(f"Level {level} failed in {round((time.time() - press_time) * 1000)} ms")
            stats["failed"] = {"status": "failed", "time": time.time() - press_time}
            if level >= 2:
                level -= 1
            lives -= 1
            if lives == 0:
                print("Game Over")
                lp.fill_all(255, 0, 0)
                # time.sleep(.1)
                lp.fill_all(0, 0, 0)
                break
    # Only count successful levels, and weight them by level
    successful = [stat for stat in stats.values() if stat['status'] == 'completed']
    if successful:
        weighted_sum = sum(level * (1 / stat['time']) for level, stat in enumerate(successful, start=1))
        score = weighted_sum * 1000
    else:
        score = 0

    # Penalise failures: each failure subtracts a fixed amount (e.g., 50)
    score = max(0, round(score/10, 0))
    print(f"Final Score: {score}")
    return score


def main():
    lp = LaunchpadMK2()
    try:
        while True:
            wait_user(lp)
            game_loop(lp)
    except KeyboardInterrupt:
        print("\n[Launchpad] Exiting...")
        lp.clear()


if __name__ == "__main__":
    main()
