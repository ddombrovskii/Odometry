import os, sys
os.system("")
LINE_UP = '\033[1A'
LINE_CLEAR = '\033[2K'
COLOR = {
    "HEADER": "\033[95m",
    "BLUE": "\033[94m",
    "GREEN": "\033[92m",
    "RED": "\033[91m",
    "ENDC": "\033[0m",
}

#print(COLOR["HEADER"], "Testing Green!!", COLOR["ENDC"])

if __name__ == "__main__":

    sys.stdout.write('123\n')
    sys.stdout.write('123\n')
    sys.stdout.write('123\n')
    sys.stdout.write(LINE_UP)
    sys.stdout.write('456\n')
    a = input()
    #print("ty kurva")

    # imu = IMU()
    # imu.run()