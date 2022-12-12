# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from Odometry.bit_set import BitSet32


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    import time
    print_hi('PyCharm')
    t = time.perf_counter()
    time.sleep(1)
    t = time.perf_counter() - t
    print(f"perf_counter  {t}")
    with open('vmath\core\camera.py', 'rt') as file:
        print('#' * 10)
        print(file.name)
        print('#' * 10)
        for line in file:
            print(line)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
