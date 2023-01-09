import math
from threading import Thread
import datetime as datetime
import numpy as np
import cv2 as cv
import time

from cgeo import mutils

run_in_debug_mode = True
run_with_errors = True
TlFactory = None

try:
    from pypylon import genicam
    from pypylon import pylon
except ImportError as ex:
    print(f"PyPylon import error!!! application will close now!!!\n{ex.args}")
    if not run_with_errors:
        exit(1)

try:
    TlFactory = pylon.TlFactory.GetInstance()
except NameError as ex:
    print(f"PyPylon create factory error!!!\n{ex.args}")
    if not run_with_errors:
        exit(1)


def get__scr_size():
    import ctypes
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


def auto_exposure_calibration(camera, calib_time: float):
    if run_in_debug_mode:
        print(f"auto exposure calibration during {calib_time} seconds")
        print(f"exposure time on begin: {camera.exposure_time}")
    camera.exposure_mode = "Continuous"
    time.sleep(calib_time)
    camera.exposure_mode = "Off"
    if run_in_debug_mode:
        print(f"exposure time on end  : {camera.exposure_time}")


class BaslerCamera: #  (Camera):
    __GIG_E_DEVICE = 'BaslerGigE'

    __USB_DEVICE = 'BaslerUsb'

    def __init__(self):
        # super().__init__()
        self.converting_enable: bool = True
        self.__device_class: str = "none"
        self.__device_model: str = "none"
        self.__auto_process_run = False
        self.__cam_device = None
        self.__camera = None
        self.__image_converter = pylon.ImageFormatConverter()
        # Converting to opencv bgr format
        self.__image_converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        self.__image_converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
        self.__frames_buffer: [np.ndarray] = []
        self.__frames_buffer_depth = 8
        # cashed values
        # camera size
        self.__frame_time: float = 0.0
        self.__width: int = -1
        self.__height: int = -1
        self.__offset_x: int = -1
        self.__offset_y: int = -1
        self.__pixel_format = ""
        # gain
        self.__gain_mode: str = ""
        self.__gain: float = 0.0
        self.__gain_max: float = 0.0
        self.__gain_min: float = 0.0
        # exposure
        self.__exposure_mode: str = ""
        self.__exposure_time: float = 0.0
        self.__exposure_time_max: float = 0.0
        self.__exposure_time_min: float = 0.0
        self.__packet_delay: int = -1
        self.__packet_size: int = -1
        self.__run_back_ground_function: bool = False
        self.__show_info: bool = False
        self.__init_camera()

    def __del__(self):
        self.close()

    def __str__(self):
        if self.__device_class == BaslerCamera.__GIG_E_DEVICE:
            return f"class         : {self.device_class},\n" \
                   f"width         : {self.camera_width},\n" \
                   f"height        : {self.camera_height},\n" \
                   f"offset x      : {self.offset_x},\n" \
                   f"offset y      : {self.offset_y},\n" \
                   f"pix format    : {self.pixel_format},\n" \
                   f"gain mode     : {self.gain_mode},\n" \
                   f"gain value    : {self.gain},\n" \
                   f"gain max      : {self.gain_max},\n" \
                   f"gain min      : {self.gain_min},\n" \
                   f"exposure mode : {self.exposure_mode},\n" \
                   f"exposure time : {self.exposure_time},\n" \
                   f"exposure max  : {self.exposure_time_max},\n" \
                   f"exposure min  : {self.exposure_time_min},\n" \
                   f"packet delay  : {self.packet_delay},\n" \
                   f"packet size   : {self.packet_size},\n" \
                   f"frame time    : {self.frame_time}.\n"

        if self.__device_class == BaslerCamera.__USB_DEVICE:
            return f"class         : {self.device_class},\n" \
                   f"width         : {self.camera_width},\n" \
                   f"height        : {self.camera_height},\n" \
                   f"offset x      : {self.offset_x},\n" \
                   f"offset y      : {self.offset_y},\n" \
                   f"pix format    : {self.pixel_format},\n" \
                   f"gain mode     : {self.gain_mode},\n" \
                   f"gain value    : {self.gain},\n" \
                   f"gain max      : {self.gain_max},\n" \
                   f"gain min      : {self.gain_min},\n" \
                   f"exposure mode : {self.exposure_mode},\n" \
                   f"exposure time : {self.exposure_time},\n" \
                   f"exposure max  : {self.exposure_time_max},\n" \
                   f"exposure min  : {self.exposure_time_min},\n" \
                   f"frame time    : {self.frame_time}.\n"
        return ""

    def start(self):
        if self.__camera is None:
            return
        if not self.__camera.IsGrabbing():
            self.__camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    def stop(self):
        self.__camera.StopGrabbing()

    def __init_camera(self) -> bool:

        devices = TlFactory.EnumerateDevices()

        if len(devices) == 0:
            print("Empty devices...")
            return False

        self.__cam_device = devices[0]
        try:
            self.__device_class = self.__cam_device.GetDeviceClass()
            self.__device_model = self.__cam_device.GetModelName()
            self.__camera = pylon.InstantCamera()
            self.__camera.Attach(TlFactory.CreateDevice(self.__cam_device))
            self.__camera.Open()
            try:
                self.__camera.AcquisitionFrameRateEnable.SetValue(True)
                self.__camera.AcquisitionMode.SetValue('Continuous')
            except Exception as ex_:
                print(ex_.args)

            try:
                self.__camera.BslColorSpaceMode.SetValue("RGB")
                self.__camera.LightSourcePreset.SetValue("Off")
            except Exception as ex_:
                print(ex_.args)

            if self.device_class == BaslerCamera.__USB_DEVICE:
                self.pixel_format = "RGB8"

            if self.device_class == BaslerCamera.__GIG_E_DEVICE:
                self.pixel_format = "YUV422Packed"

            self.gain_mode = "Off"
            self.gain_max = 20
            self.gain_min = 0
            self.gain = 0
            self.offset_x = 8
            self.offset_y = 8
            self.camera_width = 1920
            self.camera_height = 1200
            self.frame_time = 1.0 / 60
            self.exposure_mode = "Off"
            self.exposure_time_min = 40
            self.exposure_time_max = 400000
            self.exposure_time = 30000

            if self.device_class == BaslerCamera.__GIG_E_DEVICE:
                self.packet_size = 10000
                self.packet_delay = 0
            # self.transform.sx = self.camera_width  # camera focal length x
            # self.transform.sy = self.camera_height # camera focal length x
            # self.transform.x = self.camera_width  * 0.5 # camera center x
            # self.transform.y = self.camera_height * 0.5 # camera center y

            # self.__camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
            return True

        except RuntimeError as ex_:
            self.__camera.Close()
            if run_in_debug_mode:
                print(f"Camera creating error ::  {ex_.args}")
            return False

    def __try_get_node(self, node_name: str) -> "GENAPI_NAMESPACE::INode *":
        try:
            return self.__camera.GetNode(node_name)
        except Exception as ex_:
            print(f"node {node_name:40} not exist in {self.device_class}")
            print(ex_.args)
            return None

    def __append_frames_buffer(self, frame: np.ndarray) -> None:
        if len(self.__frames_buffer) == self.__frames_buffer_depth:
            del self.__frames_buffer[0]
        self.__frames_buffer.append(frame)

    def auto_exp_calibration(self, calibration_time: float = 5.0):
        if self.exposure_mode == "Continuous":
            return
        th = Thread(target=auto_exposure_calibration, daemon=True, args=(self, calibration_time,))
        th.start()

    def set_auto_function_aoi_usage_intensity(self, value=True) -> None:
        node = self.__try_get_node('AutoFunctionAOIUsageIntensity')
        if node is None:
            return
        if not genicam.IsWritable(node):
            return
        node.SetValue(value)

    def set_auto_function_aoi_usage_white_balance(self, value=True) -> None:
        node = self.__try_get_node('AutoFunctionAOIUsageWhiteBalance')
        if node is None:
            return
        if not genicam.IsWritable(node):
            return
        node.SetValue(value)

    def close(self):
        try:
            if self.__camera is None:
                return

            self.stop()
            self.__camera.Close()
        except RuntimeError as _ex:
            if run_in_debug_mode:
                print(f"dispose error {_ex.args}")

    @property
    def basler_camera(self) -> pylon.InstantCamera:
        return self.__camera

    @property
    def is_open(self) -> bool:
        if self.__camera is None:
            return False
        return self.__camera.IsGrabbing()

    @property
    def device_model(self) -> str:
        return self.__device_model

    @property
    def device_class(self) -> str:
        return self.__device_class

    @property
    def frame_time(self) -> float:
        return self.__frame_time

    @frame_time.setter
    def frame_time(self, time_: float) -> None:
        if self.device_class == BaslerCamera.__GIG_E_DEVICE:
            if not genicam.IsWritable(self.__camera.AcquisitionFrameRateAbs):
                self.__frame_time = self.__camera.AcquisitionFrameRateAbs.GetValue()
                return

            self.__camera.AcquisitionFrameRateAbs.SetValue(1.0 / time_)
            self.__frame_time = time_
            return

        if self.device_class == BaslerCamera.__USB_DEVICE:
            if not genicam.IsWritable(self.__camera.AcquisitionFrameRate):
                self.__frame_time = self.__camera.AcquisitionFrameRate.GetValue()
                return

            print(type(self.__camera.AcquisitionFrameRate.GetValue()))
            self.__camera.AcquisitionFrameRate.SetValue(1.0 / time_)
            self.__frame_time = time_
            return

        raise RuntimeError(f"frame time min set :: unsupported device class: {self.device_class}")

    @property
    def is_buffer_empty(self) -> bool:
        return len(self.__frames_buffer) == 0

    @property
    def pixel_format(self) -> str:
        return self.__pixel_format  # self.__camera.PixelFormat.GetValue()

    @pixel_format.setter
    def pixel_format(self, pixel_format: str) -> None:
        self.stop()
        if not genicam.IsWritable(self.__camera.PixelFormat):
            self.__pixel_format = self.__camera.PixelFormat.GetValue()
            self.start()
            return

        try:
            self.__camera.PixelFormat.SetValue(pixel_format)
            self.__pixel_format = pixel_format
        except Exception as er:
            self.__camera.PixelFormat.SetValue('Mono8')
            self.__pixel_format = 'Mono8'
            print(f"pixel format SET error:\n{er.args}")
        self.start()

    @property
    def camera_width(self) -> int:
        return self.__width

    @camera_width.setter
    def camera_width(self, w: int) -> None:
        self.stop()
        if not genicam.IsWritable(self.__camera.Width):
            self.__width = self.__camera.Width.GetValue()
            self.start()
            return

        new_val = (w + self.__camera.Width.Inc // 2) // self.__camera.Width.Inc * self.__camera.Width.Inc

        self.__camera.Width.SetValue(mutils.clamp(new_val, self.__camera.Width.Min, self.__camera.Width.Max))

        self.__width = new_val

        self.aspect = self.camera_width / float(self.camera_height)
        self.start()

    @property
    def camera_height(self) -> int:
        return self.__height

    @camera_height.setter
    def camera_height(self, h: int) -> None:
        self.stop()
        if not genicam.IsWritable(self.__camera.Height):
            self.__height = self.__camera.Height.GetValue()
            self.start()
            return

        new_val = (h + self.__camera.Height.Inc // 2) // self.__camera.Height.Inc * self.__camera.Height.Inc

        self.__camera.Height.SetValue(mutils.clamp(new_val, self.__camera.Height.Min, self.__camera.Height.Max))

        self.__height = new_val

        self.aspect = self.camera_width / float(self.camera_height)

        self.start()

    @property
    def offset_x(self) -> int:
        return self.__offset_x

    @offset_x.setter
    def offset_x(self, value) -> None:
        self.stop()
        if not genicam.IsWritable(self.__camera.OffsetX):
            self.__offset_x = self.__camera.OffsetX.GetValue()
            self.start()
            return

        new_val = (value + self.__camera.OffsetX.Inc // 2) // self.__camera.OffsetX.Inc * self.__camera.OffsetX.Inc
        self.__camera.OffsetX.SetValue(mutils.clamp(new_val, self.__camera.OffsetX.Min, self.__camera.OffsetX.Max))
        self.__offset_x = new_val
        self.start()

    @property
    def offset_y(self) -> int:
        return self.__offset_y

    @offset_y.setter
    def offset_y(self, value) -> None:
        self.stop()
        if not genicam.IsWritable(self.__camera.OffsetY):
            self.__offset_y = self.__camera.OffsetY.GetValue()
            self.start()
            return

        new_val = (value + self.__camera.OffsetY.Inc // 2) // self.__camera.OffsetY.Inc * self.__camera.OffsetY.Inc
        self.__camera.OffsetY.SetValue(mutils.clamp(new_val, self.__camera.OffsetY.Min, self.__camera.OffsetY.Max))
        self.__offset_y = new_val
        self.start()

    @property
    def exposure_mode(self) -> str:
        return self.__exposure_mode

    def __update_exposure_time_value(self):
        if self.device_class == BaslerCamera.__GIG_E_DEVICE:
            if not genicam.IsWritable(self.__camera.ExposureTimeAbs):
                self.__exposure_time = self.__camera.ExposureTimeAbs.GetValue()
                return

        if self.device_class == BaslerCamera.__USB_DEVICE:
            if not genicam.IsWritable(self.__camera.ExposureTime):
                self.__exposure_time = self.__camera.ExposureTime.GetValue()
                return

    @exposure_mode.setter
    def exposure_mode(self, value: str):
        if not genicam.IsWritable(self.__camera.ExposureAuto):
            self.__exposure_mode = self.__camera.ExposureAuto.GetValue()
            return

        if value == "Once" or value == "Continuous":
            self.set_auto_function_aoi_usage_intensity()
            self.set_auto_function_aoi_usage_white_balance()

        while True:
            if value == "Off":
                self.__update_exposure_time_value()
                break
            if value == "Once":
                self.__update_exposure_time_value()
                break
            if value == "Continuous":
                break
            return

        self.__camera.ExposureAuto.SetValue(value)
        self.__exposure_mode = value

    @property
    def exposure_time_min(self) -> float:
        return self.__exposure_time_min

    @exposure_time_min.setter
    def exposure_time_min(self, t: float) -> None:
        if self.device_class == BaslerCamera.__GIG_E_DEVICE:
            if not genicam.IsWritable(self.__camera.AutoExposureTimeLowerLimitRaw):
                self.__exposure_time_min = self.__camera.AutoExposureTimeLowerLimitRaw.GetValue()
                return

            self.__camera.AutoExposureTimeLowerLimitRaw.SetValue(t)
            self.__exposure_time_min = t
            return

        if self.device_class == BaslerCamera.__USB_DEVICE:
            if not genicam.IsWritable(self.__camera.AutoExposureTimeLowerLimit):
                self.__exposure_time_min = self.__camera.AutoExposureTimeLowerLimit.GetValue()
                return

            self.__camera.AutoExposureTimeLowerLimit.SetValue(t)
            self.__exposure_time_min = t
            return

        raise RuntimeError(f"exposure time min set :: unsupported device class: {self.device_class}")

    @property
    def exposure_time_max(self) -> float:
        return self.__exposure_time_max

    @exposure_time_max.setter
    def exposure_time_max(self, t: float) -> None:
        if self.device_class == BaslerCamera.__GIG_E_DEVICE:
            if not genicam.IsWritable(self.__camera.AutoExposureTimeUpperLimitRaw):
                self.__exposure_time_max = self.__camera.AutoExposureTimeUpperLimitRaw.GetValue()
                return

            self.__camera.AutoExposureTimeUpperLimitRaw.SetValue(t)
            self.__exposure_time_max = t
            return

        if self.device_class == BaslerCamera.__USB_DEVICE:
            if not genicam.IsWritable(self.__camera.AutoExposureTimeUpperLimit):
                self.__exposure_time_max = self.__camera.AutoExposureTimeUpperLimit.GetValue()
                return

            self.__camera.AutoExposureTimeUpperLimit.SetValue(t)
            self.__exposure_time_max = t
            return

        raise RuntimeError(f"exposure time max set :: unsupported device class: {self.device_class}")

    @property
    def exposure_time(self) -> float:
        if self.__exposure_mode == 'Continuous':
            if self.device_class == BaslerCamera.__GIG_E_DEVICE:
                return self.__camera.ExposureTimeAbs.GetValue()

            if self.device_class == BaslerCamera.__USB_DEVICE:
                return self.__camera.ExposureTime.GetValue()

            raise RuntimeError(f"exposure time get :: unsupported device class: {self.device_class}")

        return self.__exposure_time

    @exposure_time.setter
    def exposure_time(self, value) -> None:
        if self.device_class == BaslerCamera.__GIG_E_DEVICE:
            if not genicam.IsWritable(self.__camera.ExposureTimeAbs):
                self.__exposure_time = self.__camera.ExposureTimeAbs.GetValue()
                return

            new_val = mutils.clamp(value, self.exposure_time_min, self.exposure_time_max)
            self.__camera.ExposureTimeAbs.SetValue(new_val)
            self.__exposure_time = new_val
            return

        if self.device_class == BaslerCamera.__USB_DEVICE:
            if not genicam.IsWritable(self.__camera.ExposureTime):
                self.__exposure_time = self.__camera.ExposureTime.GetValue()
                return

            new_val = mutils.clamp(value, self.exposure_time_min, self.exposure_time_max)
            self.__camera.ExposureTime.SetValue(new_val)
            self.__exposure_time = new_val
            return

        raise RuntimeError(f"exposure time max set :: unsupported device class: {self.device_class}")

    @property
    def gain_mode(self) -> str:
        return self.__gain_mode

    def __update_gain_value(self):
        if self.device_class == BaslerCamera.__GIG_E_DEVICE:
            if not genicam.IsWritable(self.__camera.GainRaw):
                self.__gain = self.__camera.GainRaw.GetValue()
                return

        if self.device_class == BaslerCamera.__USB_DEVICE:
            if not genicam.IsWritable(self.__camera.Gain):
                self.__gain = self.__camera.Gain.GetValue()
                return

    @gain_mode.setter
    def gain_mode(self, value: str) -> None:
        if not genicam.IsWritable(self.__camera.GainAuto):
            self.__gain_mode = self.__camera.GainAuto.GetValue()
            return

        while True:
            if value == "Off":
                self.__update_gain_value()
                break
            if value == "Once":
                self.__update_gain_value()
                break
            if value == "Continuous":
                break
            return

        self.__camera.GainAuto.SetValue(value)
        self.__gain_mode = value

    @property
    def gain_min(self) -> float:
        return self.__gain_min

    @gain_min.setter
    def gain_min(self, t: float) -> None:
        if self.device_class == BaslerCamera.__GIG_E_DEVICE:
            if not genicam.IsWritable(self.__camera.AutoGainRawLowerLimit):
                self.__gain_min = self.__camera.AutoGainRawLowerLimit.GetValue()
                return

            self.__camera.AutoGainRawLowerLimit.SetValue(t)
            self.__gain_min = t
            return

        if self.device_class == BaslerCamera.__USB_DEVICE:
            if not genicam.IsWritable(self.__camera.AutoGainLowerLimit):
                self.__gain_min = self.__camera.AutoGainLowerLimit.GetValue()
                return

            self.__camera.AutoGainLowerLimit.SetValue(t)
            self.__gain_min = t
            return

        raise RuntimeError(f"gain min set :: unsupported device class: {self.device_class}")

    @property
    def gain_max(self) -> float:
        return self.__gain_max

    @gain_max.setter
    def gain_max(self, t: float) -> None:
        if self.device_class == BaslerCamera.__GIG_E_DEVICE:
            if not genicam.IsWritable(self.__camera.AutoGainRawUpperLimit):
                self.__gain_max = self.__camera.AutoGainRawUpperLimit.GetValue()
                return

            self.__camera.AutoGainRawUpperLimit.SetValue(t)
            self.__gain_max = t
            return

        if self.device_class == BaslerCamera.__USB_DEVICE:
            if not genicam.IsWritable(self.__camera.AutoGainUpperLimit):
                self.__gain_max = self.__camera.AutoGainUpperLimit.GetValue()
                return

            self.__camera.AutoGainUpperLimit.SetValue(t)
            self.__gain_max = t
            return

        raise RuntimeError(f"gain max set :: unsupported device class: {self.device_class}")

    @property
    def gain(self) -> float:
        if self.__gain_mode == 'Continuous':
            if self.device_class == BaslerCamera.__GIG_E_DEVICE:
                return self.__camera.GainRaw.GetValue()

            if self.device_class == BaslerCamera.__USB_DEVICE:
                return self.__camera.Gain.GetValue()

        return self.__gain

    @gain.setter
    def gain(self, value) -> None:
        if self.device_class == BaslerCamera.__GIG_E_DEVICE:
            if not genicam.IsWritable(self.__camera.GainRaw):
                self.__gain = self.__camera.GainRaw.GetValue()
                return

            new_val = mutils.clamp(value, self.gain_min, self.gain_max)
            self.__camera.GainRaw.SetValue(new_val)
            self.__gain = new_val
            return

        if self.device_class == BaslerCamera.__USB_DEVICE:
            if not genicam.IsWritable(self.__camera.Gain):
                self.__gain = self.__camera.Gain.GetValue()
                return

            new_val = mutils.clamp(value, self.gain_min, self.gain_max)
            self.__camera.Gain.SetValue(new_val)
            self.__gain = new_val
            return

        raise RuntimeError(f"gain set :: unsupported device class: {self.device_class}")

    @property
    def packet_size(self) -> int:
        return self.__packet_size

    @packet_size.setter
    def packet_size(self, value) -> None:
        if self.device_class != BaslerCamera.__GIG_E_DEVICE:
            self.__packet_size = -1
            return

        if not genicam.IsWritable(self.__camera.GevSCPSPacketSize):
            return

        new_val = int(mutils.clamp(value, self.__camera.GevSCPSPacketSize.Min, self.__camera.GevSCPSPacketSize.Max))
        self.__camera.GevSCPSPacketSize.SetValue(new_val)
        self.__packet_size = new_val

    @property
    def packet_delay(self) -> int:
        return self.__packet_delay

    @packet_delay.setter
    def packet_delay(self, value) -> None:
        if self.device_class != BaslerCamera.__GIG_E_DEVICE:
            self.__packet_delay = -1
            return

        if not genicam.IsWritable(self.__camera.GevSCPD):
            return

        new_val = int(mutils.clamp(value, self.__camera.GevSCPD.Min, self.__camera.GevSCPD.Max))
        self.__camera.GevSCPD.SetValue(new_val)
        self.__packet_delay = new_val

    @property
    def last_frame(self) -> np.ndarray:
        if len(self.__frames_buffer) == 0:
            return np.zeros((self.camera_width, self.camera_height), dtype=np.uint8)

        return self.__frames_buffer[len(self.__frames_buffer) - 1]

    def grab_frame(self) -> bool:
        if not self.is_open:
            raise RuntimeError("Unable to grab frame...")

        grab_result = self.__camera.RetrieveResult(10000, pylon.TimeoutHandling_ThrowException)
        if not grab_result.GrabSucceeded():
            grab_result.Release()
            return False
        if self.converting_enable:
            pylon_image = self.__image_converter.Convert(grab_result)
            self.__append_frames_buffer(pylon_image.GetArray())
            grab_result.Release()
            return True
        self.__append_frames_buffer(grab_result.GetArray())
        grab_result.Release()
        return True

    @property
    def next_frame(self) -> np.ndarray:
        if not self.grab_frame():
            pass
        return self.last_frame

    def frames(self) -> np.ndarray:
        self.grab_frame()
        yield self.last_frame

    def __resize(self):
        try:
            cv.resizeWindow("video-viewer", self.camera_width, self.camera_height)
        except:
            pass

        try:
            cv.resizeWindow("video-recorder", self.camera_width, self.camera_height)
        except:
            pass

    def __on_width_change(self, width: int):
        self.camera_width = width
        self.__resize()

    def __on_height_change(self, height: int):
        self.camera_height = height
        self.__resize()

    def __on_offset_x_change(self, offset_x: int):
        self.offset_x = offset_x

    def __on_offset_y_change(self, offset_y: int):
        self.offset_y = offset_y

    def __on_exposure_change(self, exposure: int):
        self.exposure_time = float(exposure)

    def __on_gain_change(self, gain: int):
        self.gain = float(gain)

    def __camera_settings_gui(self, x: int, y: int):
        name = f'{self.device_class} camera settings'
        try:
            cv.destroyWindow(name)
        except:
            pass

        cv.namedWindow(name, cv.WINDOW_NORMAL)

        cv.resizeWindow(name, 400, 300)

        sw, sh = get__scr_size()

        cv.moveWindow(name, max(0, (sw - 400) >> 1), max(0, (sh - 300) >> 1))

        cv.createTrackbar('width   ', name, self.camera_width, self.__camera.Width.Max, self.__on_width_change)

        cv.createTrackbar('height  ', name, self.camera_height, self.__camera.Height.Max, self.__on_height_change)

        cv.createTrackbar('offset x', name, self.offset_x,
                          self.__camera.OffsetX.Max, self.__on_offset_x_change)

        cv.createTrackbar('offset y', name, self.offset_y,
                          self.__camera.OffsetY.Max, self.__on_offset_y_change)

        cv.createTrackbar('exposure', name, round(self.exposure_time), round(self.exposure_time_max),
                          self.__on_exposure_change)

        cv.createTrackbar('gain    ', name, round(self.gain), round(self.gain_max),
                          self.__on_gain_change)

    def __on_mouse_event(self, event, x, y, flags, param):
        if event == cv.EVENT_RBUTTONDOWN:
            self.__camera_settings_gui(x, y)

    def keyboard_input(self) -> bool:

        key = cv.waitKey(2)

        if key == 27:
            return False

        if key == ord('s') or key == 251:
            try:
                now = datetime.datetime.now()
                cv.imwrite(f'frame_at_time_{now.hour}_{now.minute}_{now.second}_{now.microsecond}.png', self.last_frame)
                return True

            except RuntimeError as ex:
                print(f"{ex.args}")
                return True

        if key == ord('e') or key == 243:
            self.auto_exp_calibration()
            return True

        if key == ord('i') or key == 248:
            self.__show_info = (not self.__show_info)
            return True

        if key == ord('r') or key == 234:
            self.record_video()
            return False

        if key == ord('v') or key == 236:
            self.show_video()
            return False

        return True

    def draw_camara_data(self, frame: np.ndarray, fps: int = 0) -> np.ndarray:
        w_, h_ = 900, 600

        fnt_sz = max(0.50, 0.0005 * math.sqrt(w_**2 + h_**2))

        col_1_pos = int(0.05 * w_)

        col_2_pos = int(0.207 * w_)

        col = (250, 245, 240)

        dh: int = int(0.04 * h_)
        h: int = dh
        col = (187, 151, 104)
        frame = cv.putText(frame, "camera fps     :", (col_1_pos, h),
                           cv.FONT_HERSHEY_SIMPLEX, fnt_sz, col, 2, cv.LINE_AA)
        while True:
            if fps < 10:
                frame = cv.putText(frame, f"{fps}", (col_2_pos + 13, h),
                                   cv.FONT_HERSHEY_SIMPLEX, fnt_sz, (0, 0, 255), 2, cv.LINE_AA)
                break

            if fps < 20:
                frame = cv.putText(frame, f"{fps}", (col_2_pos + 13, h),
                                   cv.FONT_HERSHEY_SIMPLEX, fnt_sz, (0, 128, 255), 2, cv.LINE_AA)
                break

            if fps < 30:
                frame = cv.putText(frame, f"{fps}", (col_2_pos + 13, h),
                                   cv.FONT_HERSHEY_SIMPLEX, fnt_sz, (0, 255, 255), 2, cv.LINE_AA)
                break

            frame = cv.putText(frame, f"{fps}", (col_2_pos + 13, h),
                               cv.FONT_HERSHEY_SIMPLEX, fnt_sz, (0, 255, 0), 2, cv.LINE_AA)
            break

        if not self.__show_info:
            return frame

        cam_info = self.__str__().split('\n')

        for info_str in cam_info:
            if len(info_str) == 0:
                continue

            h += dh
            strs = info_str.split(':')
            frame = cv.putText(frame, strs[0], (col_1_pos, h), cv.FONT_HERSHEY_SIMPLEX, fnt_sz, col, 2, cv.LINE_AA)
            frame = cv.putText(frame, ":" + strs[1], (col_2_pos, h), cv.FONT_HERSHEY_SIMPLEX, fnt_sz, col, 2, cv.LINE_AA)

        return frame

    def show_video(self):
        try:
            cv.destroyWindow("video-recorder")
        except:
            pass
        cv.namedWindow("video-viewer", cv.WINDOW_NORMAL)
        cv.resizeWindow("video-viewer", self.camera_width, self.camera_height)
        sw, sh = get__scr_size()
        cv.moveWindow("video-viewer", max(0, (sw - self.camera_width) >> 1), max(0, (sh - self.camera_height) >> 1))
        cv.setMouseCallback("video-viewer", self.__on_mouse_event)
        t1: float = time.time()
        t0: float = time.time()
        while True:
            #    break
            if not self.is_open or not self.keyboard_input():
                break
            try:
                t1 = time.time()
                if not self.grab_frame():
                    continue
                dt = t1 - t0
                cv.imshow("video-viewer", self.draw_camara_data(self.last_frame, round(1 / (dt + 1e-6))))
                if dt > self.frame_time:
                    t0 = t1
                    continue
                time.sleep(self.frame_time - dt)
                t0 = t1
            except RuntimeError as ex:
                print(f"{ex.args}")
        try:
            cv.destroyWindow("video-viewer")
        except:
            pass

    def record_video(self, record_path: str = None):
        try:
            cv.destroyWindow("video-viewer")
        except:
            pass

        while True:
            if record_path is None:
                record_path = f"camera record {datetime.datetime.now().strftime('%H; %M; %S')}.avi"
                break
            if len(record_path) == 0:
                record_path = f"camera record {datetime.datetime.now().strftime('%H; %M; %S')}.avi"
                break
            break
        cv.namedWindow("video-recorder", cv.WINDOW_NORMAL)
        cv.resizeWindow("video-recorder", self.camera_width, self.camera_height)
        sw, sh = get__scr_size()
        cv.moveWindow("video-viewer", max(0, (sw - self.camera_width) >> 1), max(0, (sh - self.camera_height) >> 1))
        t1: float = time.time()
        t0: float = time.time()
        fourcc = cv.VideoWriter_fourcc('m', 'p', '4', 'v')
        writer = cv.VideoWriter(record_path, fourcc, 30, (self.camera_width, self.camera_height))
        while True:
            if cv.getWindowProperty('video-recorder', cv.WND_PROP_VISIBLE) < 1:
                break
            # esc to exit
            t1 = time.time()
            dt = t1 - t0
            if not self.grab_frame():
                t0 = t1
                continue
            if not self.is_open or not self.keyboard_input():
                break
            frame = self.last_frame

            writer.write(frame)

            cv.imshow("video-recorder", self.draw_camara_data(frame, round(1 / (dt + 1e-6))))

            if dt > self.frame_time:
                t0 = t1
                continue
            time.sleep(self.frame_time - dt)
            t0 = t1
        writer.release()
        try:
            cv.destroyWindow("video-recorder")
        except:
            pass

    def camera_info(self):
        print(self.__str__())


def camera_test():
    global run_in_debug_mode
    run_in_debug_mode = False
    cam = BaslerCamera()
    cam.start()
    if not cam.is_open:
        exit(-1)
    cam.camera_info()
    cam.show_video()


if __name__ == "__main__":
    camera_test()
