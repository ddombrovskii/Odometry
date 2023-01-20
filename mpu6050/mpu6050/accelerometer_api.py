from mpu6050 import Accelerometer, load_accelerometer_settings, save_accelerometer_settings, read_current_data
from cgeo import LoopTimer, BitSet32
import datetime as dt
import os.path

ACC_RUNNING = 0
ACC_LOGGING = 1
ACC_ALIVE = 2


class ConsoleAccelerometerInterface:
    _api_info = \
        [
            ["key", "key_arg", "description"],
            ["info/i", "-", "shows info"],
            ["reset", "-", "do accelerometer reset"],
            ["p/pause", "-", "pause accelerometer reading"],
            ["r/resume", "-", "resume accelerometer reading"],
            ["s/exit", "-", "do exit"],
            ["c/calibrate", "calibration time", "do accelerometer calibration"],
            ["t/time", "live time in secs", "accelerometer live time"],
            ["dt/dtime", "time delta in secs", "accelerometer update time"],
            ["ls/loadsettings", "settings file path", "load accelerometer settings"],
            ["ss/savesettings", "save settings file path", "save accelerometer settings"]
        ]

    def __init__(self):
        self._accelerometer: Accelerometer = Accelerometer()
        self._timer: LoopTimer = LoopTimer()
        self._live_time: float = -1.0
        self._state: BitSet32 = BitSet32()
        self._display_mode: int = 4
        self._log_file = None
        self._state.set_bit(ACC_ALIVE)
        self.is_running = True

    @property
    def is_logging(self) -> bool:
        return self._state.is_bit_set(ACC_LOGGING)

    @property
    def is_running(self) -> bool:
        return self._state.is_bit_set(ACC_RUNNING)

    @is_running.setter
    def is_running(self, value: bool) -> None:
        if value:
            self._state.set_bit(ACC_RUNNING)
            return
        self._state.clear_bit(ACC_RUNNING)

    @property
    def is_alive(self) -> bool:
        return self._state.is_bit_set(ACC_ALIVE)

    def run(self) -> None:
        self._show_info()
        while self.is_alive:
            with self._timer:
                if self._live_time > 0:
                    if self._timer.time < self._live_time:
                        self._state.clear_bit(ACC_ALIVE)
                self._input(input())
                if not self.is_running:
                    continue
                data = read_current_data(self._accelerometer, self._display_mode)
                print(data)
                if self.is_logging:
                    print(data, file=self._log_file)

    def _enable_logging(self, fp: str) -> bool:
        try:
            self._log_file = open(fp, "wt")
        except ValueError(f"Unable to create log file at path {fp}") as ex:
            try:
                if self._log_file is not None:
                    self._log_file.close()
            except Exception as ex:
                print(ex.args)
            return False
        print(f"{{\n\"record_date\": \"{dt.datetime.now().strftime('%H; %M; %S')}\",\n", file=self._log_file)
        print("\"way_points\" :[", file=self._log_file)
        return True

    def _disable_logging(self) -> None:
        try:
            if self._log_file is not None:
                print("]\n}", file=self._log_file)
                self._log_file.close()
        except Exception as ex:
            print(ex.args)

    def _show_info(self) -> None:
        print('\n'.join(f"|{arg[0]:<20}|{arg[1]:^25}|{arg[2]:>35}|" for arg in self._api_info))

    def _input(self, args: str):
        args = [val.strip() for val in args.split(' ') if len(val) != 0]
        if len(args) == 0:
            return
        while True:
            if len(args) == 1:
                if args[0] == "info" or args[0] == "i":
                    print(self._accelerometer)
                    break

                if args[0] == "reset":
                    self._accelerometer.reset()
                    break

                if args[0] == "p" or args[0] == "pause":
                    self.is_running = False
                    break

                if args[0] == "r" or args[0] == "resume":
                    self.is_running = True
                    break

                if args[0] == "s" or args[0] == "exit":
                    self._state.clear_bit(ACC_ALIVE)
                    break
                break

            if args[0] == "c" or args[0] == "calibrate":
                try:
                    ctime = str(args[1])
                except TypeError(f"incorrect calibrate time value: {args[1]}") as ex:
                    ctime = 10
                self.is_running = False
                self._accelerometer.calibrate(ctime)
                self.is_running = True
                break

            if args[0] == "t" or args[0] == "time":
                try:
                    self._live_time = float(args[1])
                except TypeError(f"incorrect timer time value: {args[1]}") as ex:
                    break

            if args[0] == "dt" or args[0] == "dtime":
                try:
                    self._timer.timeout = float(args[1])
                except TypeError(f"incorrect timer delta time value: {args[1]}") as ex:
                    break

            if args[0] == "fp" or args[0] == "filepath":
                if args[1] == "-":
                    self._disable_logging()
                    self._state.clear_bit(ACC_LOGGING)
                    return
                if not self._enable_logging(args[1]):
                    return
                self._state.set_bit(ACC_LOGGING)

            if args[0] == "ls" or args[0] == "loadsettings":
                if load_accelerometer_settings(self._accelerometer, args[1]):
                    print(f"accelerometer setting was successfully loaded from file{args[1]}")
                    break
                print(f"accelerometer setting was not loaded from file{args[1]}")
                break

            if args[0] == "ss" or args[0] == "savesettings":
                save_accelerometer_settings(self._accelerometer, args[1])
                break
            break


""""
timer: LoopTimer = LoopTimer()
while True:
    with timer:
        pass
"""



if __name__ == "__main__":
    api = ConsoleAccelerometerInterface()
    api.run()
