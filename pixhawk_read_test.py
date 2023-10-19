from pymavlink import mavutil

connection = mavutil.mavlink_connection("COM5")

connection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
# connection.recv_match(type='HEARTBEAT', blocking=True)
# print(connection.recv_match(blocking=True))

"""
messages
MAV,
HOME,
SYS_STATUS,
TIMESYNC,
ALTITUDE,
SERVO_OUTPUT_RAW,
SERVO_OUTPUT_RAW[0],
VFR_HUD, 
HEARTBEAT, 
STATUSTEXT, 
ATTITUDE, 
ATTITUDE_QUATERNION, 
ATTITUDE_TARGET, 
BATTERY_STATUS, 
BATTERY_STATUS[0], 
ESTIMATOR_STATUS, 
EXTENDED_SYS_STATE, 
HIGHRES_IMU, 
SCALED_IMU, 
ACTUATOR_CONTROL_TARGET, 
VIBRATION, 
PING]
"""
imu_scaled = None
imu_pured  = None
for i in range(10):
    try:
        print(connection.wait_heartbeat(timeout=5.5))
        print(f"Heartbeat from system {connection.target_system} and component {connection.target_component}")
        try:
            # print(f"[{', '.join(str(m_key) for m_key in connection.messages)}]")
            imu_scaled = connection.messages['HIGHRES_IMU']
            imu_pured = connection.messages['SCALED_IMU']
            print(f"SCALED_IMU: {imu_scaled}")
            print(f"SCALED_IMU: {connection.messages['SCALED_IMU']}")
        except:
            print('No GPS_RAW_INT message received')
    except Exception as ex:
        print(f"Heartbeat waiting failed...\n{ex}")
    v = input()
