from pymavlink import mavutil
from math import isnan
connection = mavutil.mavlink_connection("COM5")

connection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)


messages = ('MAV',
            'HOME',
            'SYS_STATUS',
            'TIMESYNC',
            'ALTITUDE',
            'SERVO_OUTPUT_RAW',
            'SERVO_OUTPUT_RAW[0]',
            'VFR_HUD',
            'HEARTBEAT',
            'STATUSTEXT',
            'ATTITUDE',
            'ATTITUDE_QUATERNION',
            'ATTITUDE_TARGET',
            'BATTERY_STATUS',
            'BATTERY_STATUS[0]',
            'ESTIMATOR_STATUS',
            'EXTENDED_SYS_STATE',
            'HIGHRES_IMU',
            'SCALED_IMU',
            'ACTUATOR_CONTROL_TARGET',
            'VIBRATION',
            'PING')


def read_whole_mav_state(pix_connection):
    if 'MAV' not in pix_connection.messages:
        return f"{{\n\"MAV\":\n\t{{\n\t\"error\": \"Param name: \"{'MAV'}\" not presented in current message\"\n\t}}\n}}"
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
    lines.append(f"\t\"messages\":\n[{nl.join(get_values_of_pix_param(pix_connection, p_name) for p_name in messages if p_name != 'MAV')}]")
    return f'{{\n\"MAV\":\n\t{{\n{nl.join(v for v in lines)}\n\t}}\n}}'


def get_values_of_pix_param(pix_connection, param_name):
    if param_name == "MAV":
        return read_whole_mav_state(pix_connection)

    if param_name not in pix_connection.messages:
        return f"\"{param_name}\":\n\t{{\n\t\"error\": \"Param name: {param_name} not presented in current message\"\n\t}}"
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
        return f'\"{param_name}\":\n\t{{\n{nl.join(v for v in lines)}\n\t}}'
    except Exception as ex:
        return f"\"{param_name}\":\n\t{{\n\t\"error\": \"Param name: {param_name} cause error: {ex}\"\n\t}}"


def get_full_status(pix_connection):
    list = {}
    for message in messages:
        if message != "MAV":
            print(get_values_of_pix_param(connection, message))

imu_scaled = None
imu_pured  = None
for i in range(2):
    try:
        connection.wait_heartbeat(timeout=5.5)
        # print()
        # print(f"Heartbeat from system {connection.target_system} and component {connection.target_component}")
        try:
            print(get_values_of_pix_param(connection, 'MAV'))
            #for message in messages:

            # print(f"[{', '.join(str(m_key) for m_key in connection.messages)}]")
        except:
            print('No GPS_RAW_INT message received')
    except Exception as ex:
        print(f"Heartbeat waiting failed...\n{ex}")
    # v = input()
