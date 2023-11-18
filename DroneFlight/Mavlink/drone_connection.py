from .wait_until_position_aiding import wait_until_position_aiding
from .get_autopilot_info import get_autopilot_info
from collections import namedtuple
from pymavlink import mavutil
from typing import Union, Tuple
from math import isnan
import asyncio
import time

try:
    from serial import SerialException
    import serial
    from serial.tools.list_ports import comports
except ImportError as er:
    print(er)

MAV = 'MAV'
HOME = 'HOME'
SYS_STATUS = 'SYS_STATUS'
TIMESYNC = 'TIMESYNC'
ALTITUDE = 'ALTITUDE'
SERVO_OUTPUT_RAW = 'SERVO_OUTPUT_RAW'
SERVO_OUTPUT_RAW_0 = 'SERVO_OUTPUT_RAW[0]'
VFR_HUD = 'VFR_HUD'
HEARTBEAT = 'HEARTBEAT'
STATUSTEXT = 'STATUSTEXT'
ATTITUDE = 'ATTITUDE'
ATTITUDE_QUATERNION = 'ATTITUDE_QUATERNION'
ATTITUDE_TARGET = 'ATTITUDE_TARGET'
BATTERY_STATUS = 'BATTERY_STATUS'
BATTERY_STATUS_0 = 'BATTERY_STATUS[0]'
ESTIMATOR_STATUS = 'ESTIMATOR_STATUS'
EXTENDED_SYS_STATE = 'EXTENDED_SYS_STATE'
HIGHRES_IMU = 'HIGHRES_IMU'
SCALED_IMU = 'SCALED_IMU'
ACTUATOR_CONTROL_TARGET = 'ACTUATOR_CONTROL_TARGET'
VIBRATION = 'VIBRATION'
PING = 'PING'

SYSTEM_TIME = 'SYSTEM_TIME'
PARAM_VALUE = 'PARAM_VALUE'
GPS_RAW_INT = 'GPS_RAW_INT'
SCALED_PRESSURE = 'SCALED_PRESSURE'
SCALED_PRESSURE2 = 'SCALED_PRESSURE2'
GLOBAL_POSITION_INT = 'GLOBAL_POSITION_INT'
RC_CHANNELS_RAW = 'RC_CHANNELS_RAW'
HIL_GPS = 'HIL_GPS'
SCALED_IMU2 = 'SCALED_IMU2'
SCALED_IMU3 = 'SCALED_IMU3'
POWER_STATUS =  'POWER_STATUS'
AHRS = 'AHRS'
AHRS1 = 'AHRS1'
AHRS2 = 'AHRS2'
MEMINFO = 'MEMINFO'
HWSTATUS = 'HWSTATUS'
STATUSEXT = 'STATUSEXT'

MESSAGES = (MAV,
            HOME,
            SYS_STATUS,
            TIMESYNC,
            ALTITUDE,
            SERVO_OUTPUT_RAW,
            SERVO_OUTPUT_RAW_0,
            VFR_HUD,
            HEARTBEAT,
            STATUSTEXT,
            ATTITUDE,
            ATTITUDE_QUATERNION,
            ATTITUDE_TARGET,
            BATTERY_STATUS,
            BATTERY_STATUS_0,
            ESTIMATOR_STATUS,
            EXTENDED_SYS_STATE,
            HIGHRES_IMU,
            SCALED_IMU,
            ACTUATOR_CONTROL_TARGET,
            VIBRATION,
            PING,
            SYSTEM_TIME,
            PARAM_VALUE,
            GPS_RAW_INT,
            SCALED_PRESSURE,
            SCALED_PRESSURE2,
            GLOBAL_POSITION_INT,
            RC_CHANNELS_RAW,
            HIL_GPS,
            SCALED_IMU2,
            SCALED_IMU3,
            POWER_STATUS,
            AHRS,
            AHRS1,
            AHRS2,
            MEMINFO,
            HWSTATUS,
            STATUSEXT
            )

MAIN_MODE_MAPPING_PX4 = {
    'MANUAL': 0,
    'ALTCTL': 1,
    'POSCTL': 2,
    'AUTO': 3,
    'ACRO': 4,
    'OFFBOARD': 5,
    'STABILIZED': 6,
    'RATTITUDE': 7,
}

SUB_MODE_MAPPING_PX4 = {
    'READY': 0,
    'TAKEOFF': 1,
    'HOLD': 2,  # LOITER in MAVLink
    'MISSION': 3,
    'RETURN_TO_LAUNCH': 4,
    'LAND': 5,
    'FOLLOW_ME': 6,
}


class GPSLocation(namedtuple("GPSLocation", "longitude, latitude, altitude, heading")):
    """
    longitude scaled up to 1.0e-7
    latitude scaled up to 1.0e-7
    """
    def __new__(cls, *args):
        assert len(args) == 4
        return super().__new__(cls, *args)

    def __str__(self):
        return f"{{\n" \
               f"\t\"longitude\" : {self.longitude},\n" \
               f"\t\"latitude\"  : {self.latitude},\n" \
               f"\t\"altitude\"  : {self.altitude},\n" \
               f"\t\"heading\"   : {self.heading}\n" \
               f"}}"


class DroneConnection:
    def _validate_mode(self, mode_key, autopilot='ardupilot', sub_mode_key=""):
        if autopilot == 'ardupilot':
            # Check if mode is available
            if mode_key not in self.drone_connection.mode_mapping():
                print(f'Unknown mode : {mode_key}')
                print(f"available modes: {list(self.drone_connection.mode_mapping().keys())}")
                raise Exception('Unknown mode')
            # Get mode ID
            return self.drone_connection.mode_mapping()[mode_key], 0
        if autopilot == 'px4':
            # Get mode ID
            return MAIN_MODE_MAPPING_PX4[mode_key], SUB_MODE_MAPPING_PX4[sub_mode_key]
        print(f"unsupported autopilot of type \"{autopilot}\"")
        return -1, -1

    def _change_mode(self, mode_key, autopilot='ardupilot', sub_mode_key=""):
        mode_id, sub_mode = self._validate_mode(mode_key, autopilot, sub_mode_key)
        if mode_id == -1:
            print(f"unsupported autopilot of type \"{autopilot}\"")
            return -1
        self.drone_connection.mav.command_long_send(self.drone_connection.target_system,
                                                    self.drone_connection.target_component,
                                                    mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
                                                    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                                                    mode_id, sub_mode, 0, 0, 0, 0)
        ack_msg = self.drone_connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
        print(ack_msg)
        return ack_msg.result

    async def _change_mode_async(self, mode_key, autopilot='ardupilot', sub_mode_key=""):
        mode_id, sub_mode = self._validate_mode(mode_key, autopilot, sub_mode_key)
        if mode_id == -1:
            print(f"unsupported autopilot of type \"{autopilot}\"")
            return -1
        self.drone_connection.mav.command_long_send(self.drone_connection.target_system,
                                                    self.drone_connection.target_component,
                                                    mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
                                                    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                                                    mode_id, sub_mode, 0, 0, 0, 0)
        ack_msg = await self._recv_match_async('COMMAND_ACK', 3.0)
        print(ack_msg)
        return ack_msg.result

    @staticmethod
    def _read_whole_mav_state(pix_connection):
        if 'MAV' not in pix_connection.messages:
            return f"{{\n\"MAV\":\n\t{{\n\t\"error\": \"Param name: \"{'MAV'}\"" \
                   f" not presented in current message\"\n\t}}\n}}"
        data = pix_connection.messages['MAV']
        nl = ',\n'
        q2 = '\"'
        lines = []
        for f_name, f_data in data.__dict__.items():
            if isinstance(f_data, int) or isinstance(f_data, float):
                f_data = '"nan"' if isnan(f_data) else f_data
                lines.append(f"\t{f'{q2}{f_name}{q2}:':<22}{str(f_data):<8}")
            if isinstance(f_data, str):
                lines.append(f"\t{f'{q2}{f_name}{q2}:':<22}\"{f_data}\"")
        lines.append(
            f"\t\"messages\":\n[{nl.join(DroneConnection._get_values_of_pix_param(pix_connection, p_name) for p_name in MESSAGES if p_name != 'MAV')}]")
        return f'{{\n\"MAV\":\n\t{{\n{nl.join(v for v in lines)}\n\t}}\n}}'

    @staticmethod
    def _get_values_of_pix_param(pix_connection, param_name):
        if param_name == "MAV":
            return DroneConnection._read_whole_mav_state(pix_connection)

        if param_name not in pix_connection.messages:
            return f"{{\n\t\"{param_name}\":\n\t{{\n\t\"error\": \"Param name: {param_name} " \
                   f"not presented in current message\"\n\t}}\n}}"
        data = pix_connection.messages[param_name]
        try:
            lines = []
            q2 = '\"'
            nl = ',\n'
            for f_name in data.fieldnames:
                f_data = getattr(data, f_name)
                if isinstance(f_data, list) or isinstance(f_data, tuple):
                    lines.append(f"\t{f'{q2}{f_name}{q2}:':<22}[{','.join(str(v) for v in f_data)}]")
                    continue
                if isinstance(f_data, int) or isinstance(f_data, float):
                    f_data = '"nan"' if isnan(f_data) else f_data
                    lines.append(f"\t{f'{q2}{f_name}{q2}:':<22}{str(f_data):<8}")
            return f'{{\n\t\"{param_name}\":\n\t{{\n{nl.join(v for v in lines)}\n\t}}\n}}'
        except Exception as ex:
            return f"{{\n\t\"{param_name}\":\n\t{{\n\t\"error\": \"Param name: {param_name} cause error: {ex}\"\n\t}}\n}}"

    @staticmethod
    def _establish_connection(port: str, timeout: float = 2.0):
        connection = mavutil.mavlink_connection(port, source_system=1)  # for faking gps ability?
        # connection = mavutil.mavlink_connection(port) # previous
        connection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
        if not connection.wait_heartbeat(timeout=timeout):
            raise TimeoutError(f"Mavlink connection to port: {port} time out error")
        return connection

    def __init__(self, port: Union[str, None] = None):
        self._external_gps_src = False
        self._connection = None
        # start pt GPS
        self._start_gps = GPSLocation(0.0, 0.0, 0.0, 0.0)
        # prev pt GPS
        self._prev_gps = GPSLocation(0.0, 0.0, 0.0, 0.0)
        # curr pt GPS
        self._curr_gps = GPSLocation(0.0, 0.0, 0.0, 0.0)
        if port is None:
            coms = [p.device for p in comports()]
            if len(coms) == 0:
                raise SystemError("No com ports found!!!")
            for p in coms:
                try:
                    self._connection = DroneConnection._establish_connection(p)
                    self.arm()
                    self._update_gps_at_start()
                    self._prev_gps = self._curr_gps =  self._read_gps()
                    self.disarm()
                    if self._connection:
                        self._port = p
                        print(self.drone_connection.mav)
                        print(f"Mavlink connected to port: {p}")
                        break
                except TimeoutError as ex:
                    print(ex)
            return
        try:
            assert isinstance(port, str)
            self._connection = DroneConnection._establish_connection(port)
            self._port = port
            self.arm()
            self._update_gps_at_start()
            self._prev_gps = self._curr_gps = self._read_gps()
            self.disarm()
            print(f"Mavlink connected to port: {port}")
            if not connection:
                raise RuntimeError(f"Mavlink connection to port: {port} error")
        except TimeoutError as ex:
            print(ex)

    def __str__(self) -> str:
        return self.get_mav_state_str()

    @property
    def start_gps(self) -> GPSLocation:
        return self._start_gps

    @property
    def prev_gps(self) -> GPSLocation:
        return self._prev_gps

    @property
    def curr_gps(self) -> GPSLocation:
        return self._curr_gps

    async def _recv_match_async(self, command_type: str, time_out: float):
        t_0 = time.perf_counter()
        ack = None
        while time.perf_counter() - t_0 <= time_out:
            ack = self.drone_connection.recv_match(type=command_type)
            if ack is not None:
                break
            await asyncio.sleep(0.01)
        return -1 if ack is None else ack.result

    # https://discuss.ardupilot.org/t/solved-how-to-read-gps-data-from-pixhawk-to-mavlink/28171

    def _read_gps(self, relative_alt: bool = False):
        # wait for another VFR_HUD, to ensure we have correct altitude
        self.drone_connection.recv_match(type='VFR_HUD', blocking=True)
        self.drone_connection.recv_match(type='GLOBAL_POSITION_INT', blocking=False, timeout=4)
        try:
            vfr        = self.drone_connection.messages['VFR_HUD']
            global_pos = self.drone_connection.messages['GLOBAL_POSITION_INT']
            gps_pos    = self.drone_connection.messages['GPS_RAW_INT']
            alt = global_pos.relative_alt * 0.001 if relative_alt else vfr.alt
            return GPSLocation(gps_pos.lat * 1.0e-7, gps_pos.lon * 1.0e-7, alt, vfr.heading)
        except KeyError as er:
            print(er)
        return self._curr_gps

    async def _read_gps_async(self, relative_alt: bool = False, timeout: float = 4.0):
        # wait for another VFR_HUD, to ensure we have correct altitude
        await self._recv_match_async('VFR_HUD', timeout)
        await self._recv_match_async('GLOBAL_POSITION_INT', timeout)
        try:
            vfr        = self.drone_connection.messages['VFR_HUD']
            global_pos = self.drone_connection.messages['GLOBAL_POSITION_INT']
            gps_pos    = self.drone_connection.messages['GPS_RAW_INT']
            alt = global_pos.relative_alt * 0.001 if relative_alt else vfr.alt
            return GPSLocation(gps_pos.lat * 1.0e-7, gps_pos.lon * 1.0e-7, alt, vfr.heading)
        except KeyError as er:
            print(er)
        return self._curr_gps

    def _update_gps_at_start(self, relative_alt: bool = False):
        self._start_gps = self._read_gps(relative_alt)

    async def _update_gps_at_start_async(self, relative_alt: bool = False):
        self._start_gps = await self._read_gps_async(relative_alt)

    def update_gps_values(self, relative_alt: bool = False):
        self._prev_gps, self._curr_gps = self._curr_gps, self._read_gps(relative_alt)

    async def _update_gps_values_async(self, relative_alt: bool = False):
        self._prev_gps, self._curr_gps = self._curr_gps, await self._read_gps(relative_alt)

    def get_param_str(self, p_name: str) -> str:
        assert isinstance(p_name, str)
        return DroneConnection._get_values_of_pix_param(self.drone_connection, p_name)

    def get_mav_state_str(self) -> str:
        return DroneConnection._read_whole_mav_state(self.drone_connection)

    def get_param(self, p_name: str):
        assert isinstance(p_name, str)
        return None if p_name not in self.drone_connection.messages else self.drone_connection.messages[p_name]

    def get_mav_state(self):
        return self.get_param(MAV)

    def set_mode(self, mode: str, sub_mode: str, autopilot: str = "px4") -> int:
        return self._change_mode(mode, autopilot, sub_mode)

    async def set_mode_async(self, mode: str, sub_mode: str, autopilot: str = "px4") -> int:
        return await self._change_mode_async(mode, autopilot, sub_mode)

    @property
    def drone_connection(self):
        return self._connection

    @property
    def port(self):
        return self._port

    def _arm_disarm(self, arm_state: bool = True, timeout: float = 5.0):
        # self.drone_connection.wait_heartbeat()
        if not self.drone_connection.wait_heartbeat(timeout=timeout):
            raise TimeoutError(f"Mavlink connection to port: {self.port} time out error")
        self.drone_connection.mav.command_long_send(self.drone_connection.target_system,
                                                    self.drone_connection.target_component,
                                                    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                                                    0, 1 if arm_state else 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        msg = self.drone_connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=3.0)
        if not msg:
            raise RuntimeError(f"Mavlink failed to recv match")
        return msg

    def arm(self, timeout: float = 5.0):
        return self._arm_disarm(True, timeout)

    def disarm(self, timeout: float = 5.0):
        return self._arm_disarm(False, timeout)

    def takeoff(self, takeoff_altitude: float, tgt_sys_id: int = 1, tgt_comp_id: int = 1):

        print(f"Heartbeat from system (system{self.drone_connection.target_system} "
              f"component {self.drone_connection.target_component})" )

        wait_until_position_aiding(self.drone_connection)
        # GPS в начале
        self._update_gps_at_start()

        autopilot_info = get_autopilot_info(self.drone_connection, tgt_sys_id)

        if autopilot_info["autopilot"] == "ardupilotmega":
            print("Connected to ArduPilot autopilot")
            mode_id = self.drone_connection.mode_mapping()["GUIDED"]
            takeoff_params = (0, 0, 0, 0, 0, 0, takeoff_altitude)
        elif autopilot_info["autopilot"] == "px4":
            print("Connected to PX4 autopilot")
            print(self.drone_connection.mode_mapping())
            mode_id = self.drone_connection.mode_mapping()["TAKEOFF"][1]
            print(mode_id)
            msg = self.drone_connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
            starting_alt = msg.alt / 1000
            takeoff_params = (0, 0, 0, 0, float("NAN"), float("NAN"), starting_alt + takeoff_altitude)
        else:
            raise ValueError("Autopilot not supported")

        # Change mode to guided (Ardupilot) or takeoff (PX4)
        self.drone_connection.mav.command_long_send(tgt_sys_id, tgt_comp_id, mavutil.mavlink.MAV_CMD_DO_SET_MODE,
                                                    0, mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, mode_id,
                                                    0, 0, 0, 0, 0)
        ack_msg = self.drone_connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
        print(f"Change Mode ACK:  {ack_msg}")

        # Arm the UAS
        print(f"Arm ACK:  {self.arm()}")

        # Command Takeoff
        self.drone_connection.mav.command_long_send(tgt_sys_id, tgt_comp_id,
                                                    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, takeoff_params[0],
                                                    takeoff_params[1], takeoff_params[2], takeoff_params[3],
                                                    takeoff_params[4], takeoff_params[5], takeoff_params[6])

        # takeoff_msg = self.drone_connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
        # print(f"Takeoff ACK:  {takeoff_msg}")
        # disable gps
        # enable odometry
        return self.command_acknowledgment_wait(timeout=5.0)

    def command_acknowledgment_wait(self, blocking: bool = True, timeout: float = 3.0):
        ack = self.drone_connection.recv_match(type='COMMAND_ACK', blocking=blocking, timeout=timeout)
        if ack is None:
            print('No acknowledgment received within the timeout period.')
            return None
        return ack.result

    def land(self, timeout: float = 10.0) -> Union[int, None]:
        """
        Sends a command for the drone to land.

        Args:
            the_connection (mavutil.mavlink_connection): The MAVLink connection to use.
            timeout (int): Time in seconds to wait for an acknowledgment.

        Returns:
            int: mavutil.mavlink.MAV_RESULT enum value.
        """

        # Send a command to land
        self.drone_connection.mav.command_long_send(self.drone_connection.target_system,
                                                    self.drone_connection.target_component,
                                                    mavutil.mavlink.MAV_CMD_NAV_LAND,
                                                    0, 0, 0, 0, 0, 0, 0, 0)
        # Wait for the acknowledgment
        # ack = self.drone_connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=timeout)
        # if ack is None:
        #     print('No acknowledgment received within the timeout period.')
        #     return None
        return self.command_acknowledgment_wait(timeout=timeout)

    def send_gps(self, gps: GPSLocation):
        if not self._external_gps_src:
            self._external_gps_src = True
            # TODO
            # GPS_TYPE need to be MAV !!!!
            # 2xGPS: GPS_TYPE=1 (AUTO); GPS2_TYPE=14 (MAV)
            # GPS_AUTO_CONFIG  2
            # GPS_AUTO_SWITCH  1
            # GPS_TYPE         1
            # GPS_TYPE2        14
            # GPS_PRIMARY      0
            #
            # FS_EKF_THRESH    0   (changed to 0 just to Off failsafe actions)
            # AHRS_GPS_USE     2
            # AHRS_EKF_TYPE    0
            # EK2_ENABLE       1
            # EK3_ENABLE       0
            # FS_EKF_ACTION    2

        """
        # Set some information !
        self.drone_connection.mav.gps_input_send(
        0,  # Timestamp (micros since boot or Unix epoch)
        0,  # ID of the GPS for multiple GPS inputs
        # Flags indicating which fields to ignore (see GPS_INPUT_IGNORE_FLAGS enum).
        # All other fields must be provided.
        8 | 16 | 32,
        0,  # GPS time (milliseconds from start of GPS week)
        0,  # GPS week number
        3,  # 0-1: no fix, 2: 2D fix, 3: 3D fix. 4: 3D with DGPS. 5: 3D with RTK
        0,  # Latitude (WGS84), in degrees * 1E7
        0,  # Longitude (WGS84), in degrees * 1E7
        60,  # Altitude (AMSL, not WGS84), in m (positive for up)
        1,  # GPS HDOP horizontal dilution of position in m
        1,  # GPS VDOP vertical dilution of position in m
        0,  # GPS velocity in m/s in NORTH direction in earth-fixed NED frame
        0,  # GPS velocity in m/s in EAST direction in earth-fixed NED frame
        0,  # GPS velocity in m/s in DOWN direction in earth-fixed NED frame
        0,  # GPS speed accuracy in m/s
        0,  # GPS horizontal accuracy in m
        0,  # GPS vertical accuracy in m
        7   # Number of satellites visible.
        )
        """
        time_us = 0
        gps_week_ms = 0
        gps_week = 0
        fix_type = 3  # if gps_nsats (visible satellites) > 3 else 1
        # gps_lat = 33.012
        # gps_lon = 13.012
        # gps_alt = 12.44

        satellites_visible = 10
        # drone_connection === mavutil.mavlink_connection(port, source_system=1)
        msg = self.drone_connection.mav.gps_input_encode(
            #    msg = master.mav.gps_input(
            time_us,  # Timestamp (not used)
            0,  # GPS ID (not used)
            0,  # Ignore flags (not used)
            3424,  # gps_week_ms
            23,  # gps_week
            fix_type,  # Fix type: 3 = 3D fix
            int(gps.latitude),  # Latitude (scaled to 1e7 all ready in GPSLocation)
            int(gps.longitude),  # Longitude (scaled to 1e7 all ready in GPSLocation)
            gps.altitude,  # Altitude in meters
            0.1, 0.1,
            0.01, 0.01, 0.1,  # vn ve vd
            0.001, 0.001, 0.001,  # spac, hac, vac
            satellites_visible  # Number of visible satellites        yaw * 1e2
        )
        self.drone_connection.mav.send(msg)
        status = self.command_acknowledgment_wait(timeout=5.0)
        self.update_gps_values()
        return status

    def get_altitude_mono(self) -> float:
        """
        altitude_monotonic
        :return:
        """
        self.drone_connection.recv_match(type='ALTITUDE', blocking=False, timeout=1)
        try:
            self.drone_connection.recv_match(type='ALTITUDE', blocking=False, timeout=1)
            return float(self.drone_connection.messages['ALTITUDE']['altitude_monotonic'])
        except KeyError as _:
            ...
        except ValueError as _:
            ...
        return 0.0

    def get_altitude_amsl(self) -> float:
        """
        altitude_monotonic
        :return:
        """
        self.drone_connection.recv_match(type='ALTITUDE', blocking=False, timeout=1)
        try:
            self.drone_connection.recv_match(type='ALTITUDE', blocking=False, timeout=1)
            return float(self.drone_connection.messages['ALTITUDE']['altitude_amsl'])
        except KeyError as _:
            ...
        except ValueError as _:
            ...
        return 0.0

    def get_quaternion(self) -> Tuple[float, ...]:
        """
         ATTITUDE_QUATERNION
         ATTITUDE_TARGET
         :return:
         """
        try:
            self.drone_connection.recv_match(type='ATTITUDE_QUATERNION', blocking=False, timeout=1)
            return tuple(float(v) for v in self.drone_connection.messages['ATTITUDE_QUATERNION']['q'])
        except KeyError as _:
            ...
        except ValueError as _:
            ...
        return 0.0,

    def get_quaternion_target(self) -> Tuple[float, ...]:
        """
         ATTITUDE_QUATERNION
         ATTITUDE_TARGET
         :return:
         """
        try:
            self.drone_connection.recv_match(type='ATTITUDE_TARGET', blocking=False, timeout=1)
            return tuple(float(v) for v in self.drone_connection.messages['ATTITUDE_TARGET']['q'])
        except KeyError as _:
            ...
        except ValueError as _:
            ...
        return 0.0,


if __name__ == "__main__":
    # Взлетает.
    # Висит минут.
    # Садится.
    connection  = DroneConnection()
    print(connection.get_mav_state_str())
    print(connection.arm())
    # connection.arm()
    # mode changing
    # print(connection.set_mode("AUTO", "px4", "READY"))
   # connection.takeoff(4)
   # time.sleep(60)
   # connection.land()
