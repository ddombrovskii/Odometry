try:
    import RPi.GPIO as GPIO
except:
    class PWM:
        def __init__(self):
            pass
        @staticmethod
        def start(aa):
            pass

        @staticmethod
        def ChangeDutyCycle(a):
            pass


    class _GPIO:
        OUT = 0
        IN = 0
        LOW = 0
        HIGH = 0
        BCM = 0

        def __init__(self):
            pass

        @staticmethod
        def getmode():
            return 0

        @staticmethod
        def setup(a, b, initial):
            pass

        @staticmethod
        def PWM(arg1, arg2):
            return PWM()

        @staticmethod
        def setmode(a):
            pass

        @staticmethod
        def setwarnings(a):
            pass

        @staticmethod
        def output(a, b):
            pass

    GPIO = _GPIO()


class MotorController:
    def __init__(self, freq: int = None, dir_pin: int = None, pwm_pin: int = None):
        self._pwm_freq: int = 400 if freq is None else freq
        self._pwm_ff: float = 0.0
        self._dir_pin: int = 18 if dir_pin is None else dir_pin
        self._pwm_pin: int = 19 if pwm_pin is None else pwm_pin
        self._zero_threshold: float = 0.5
        self._pwm = None
        try:
            if GPIO.getmode() != GPIO.BCM:
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
            GPIO.setup(self._dir_pin, GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(self._pwm_pin, GPIO.OUT, initial=GPIO.LOW)
            self._pwm = GPIO.PWM(self._pwm_pin, self._pwm_freq)
            self._pwm.start(self._pwm_ff)
        except RuntimeError as err:
            print(f"GPIO setup error:\n {err.args}")

    def __str__(self):
        return f"{{\n" \
               f"\t\"dir_pin\"        : {self.dir_pin},\n" \
               f"\t\"pwm_pin\"        : {self.pwm_pin},\n" \
               f"\t\"pwm_ff\"         : {self.pwm_ff},\n" \
               f"\t\"pwm_freq\"       : {self.pwm_freq},\n" \
               f"\t\"zero_threshold\" : {self.zero_threshold}\n" \
               f"}}"

    @property
    def zero_threshold(self) -> float:
        return self._zero_threshold

    @zero_threshold.setter
    def zero_threshold(self, val: float) -> None:
        self._zero_threshold = min(max(0.05, val), 1.0)

    @property
    def pwm_freq(self) -> int:
        return self._pwm_freq

    @property
    def dir_pin(self) -> int:
        return self._dir_pin

    @property
    def pwm_pin(self) -> int:
        return self._pwm_pin

    @property
    def pwm_ff(self) -> float:
        return self._pwm_ff

    @pwm_ff.setter
    def pwm_ff(self, val: float) -> None:
        self._pwm_ff = min(max(-1.0, val), 1.0)
        if self.pwm_ff > 0.0 + self.zero_threshold:
            self.pwm.ChangeDutyCycle(self.pwm_ff * 100.0)
            GPIO.output(self.dir_pin, GPIO.HIGH)
            return
        if self.pwm_ff < 0.0 - self.zero_threshold:
            self.pwm.ChangeDutyCycle((1.0 - self.pwm_ff) * 100.0)
            GPIO.output(self.dir_pin, GPIO.LOW)
            return
        GPIO.output(self.dir_pin, GPIO.LOW)
        self.pwm.ChangeDutyCycle(0.0)

    @property
    def pwm(self):
        return self._pwm