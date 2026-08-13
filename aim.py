from launchpad import LaunchpadMK2
import random
import time


def main():
    lp = LaunchpadMK2()
    try:
        while True:
            lp.fill_all(0, 0, 0)
            times = []
            for i in range(11):
                x = random.randint(0, 7)
                y = random.randint(1, 8)
                if i == 0:
                    lp.set_xy(x, y, 0, 0, 255)
                else:
                    lp.set_xy(x, y, 255, 255, 255)
                t = time.time()
                while True:
                    lp.update()
                    event = lp.get_pressed()
                    if event and event[0] == x and event[1] == y:
                        break
                lp.set_xy(x, y, 0, 0, 0)
                if i > 0:
                    times.append(round((time.time() - t) * 1000))
            print(f"Average time: {sum(times)/len(times)} ms ; Min time: {min(times)} ms ; Max time: {max(times)} ms")
            lp.fill_all(0, 255, 0)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Launchpad] Exiting...")
        lp.clear()


if __name__ == "__main__":
    main()

