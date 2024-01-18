import rospy
import cv2
import numpy as np

from sensor_msgs.msg import Image, Imu
from geometry_msgs.msg import PoseStamped
from cv_bridge import CvBridge
from Utilities.CV import FlightOdometer
from Utilities import io_utils
from Utilities.Geometry import Quaternion
from matplotlib import pyplot as plt
from threading import Thread, Event, Lock


rospy.init_node("test_odometry")

cv_bridge = CvBridge()

image = None
local_position = None
imu = None


def long_callback(fn):
    """
    Decorator fixing a rospy issue for long-running topic callbacks, primarily
    for image processing.

    See: https://github.com/ros/ros_comm/issues/1901.

    Usage example:

    @long_callback
    def image_callback(msg):
        # perform image processing
        # ...

    rospy.Subscriber('main_camera/image_raw', Image, image_callback, queue_size=1)
    """
    e = Event()

    def thread():
        while not rospy.is_shutdown():
            e.wait()
            e.clear()
            fn(thread.current_msg)

    thread.current_msg = None
    Thread(target=thread, daemon=True).start()

    def wrapper(msg):
        thread.current_msg = msg
        e.set()

    return wrapper


@long_callback
def image_update(data):
    global image
    image = cv_bridge.imgmsg_to_cv2(data, 'mono8')


def local_position_update(data):
    global local_position
    local_position = data


def imu_update(data):
    global imu
    imu = data


rospy.Subscriber("/iris/usb_cam/image_raw", Image, image_update)
rospy.Subscriber("/mavros/local_position/pose", PoseStamped, local_position_update)
rospy.Subscriber("/mavros/imu/data", Imu, imu_update)


def drone_odometry_test(log_file_path: str = None):
    global image

    flight_odometer = FlightOdometer()

    rot_q = Quaternion.from_euler_angles(0.0, 0.0, 0.0, False)
    positions_x = []
    positions_y = []

    try:
        if log_file_path is None:
            while True:
                rospy.sleep(0.5)
                quat = Quaternion(imu.orientation.w, imu.orientation.x, imu.orientation.y, imu.orientation.z)
                flight_odometer.compute(image, quat, local_position.pose.position.z)
                positions_x.append(0.00515 * flight_odometer.position.x)
                positions_y.append(0.00515 * flight_odometer.position.y)
                print(positions_x[-1], positions_y[-1])
        else:
            with open(log_file_path, 'wt', encoding='utf-8') as log_file:
                flight_odometer.enable_logging(log_file)
                while True:
                    rospy.sleep(0.5)
                    quat = Quaternion(imu.orientation.w, imu.orientation.x, imu.orientation.y, imu.orientation.z)
                    flight_odometer.compute(image, quat, local_position.pose.position.z)
                    positions_x.append(0.00515 * flight_odometer.position.x)
                    positions_y.append(0.00515 * flight_odometer.position.y)
                    print(positions_x[-1], positions_y[-1])
    except KeyboardInterrupt:
        print('Exit...')

    fig, axs = plt.subplots(1)
    axs.plot(positions_x, positions_y, 'r')
    axs.set_aspect('equal', 'box')
    plt.show()
    if log_file_path:
        flight_odometer.disable_logging()


if __name__ == '__main__':
    drone_odometry_test('odom_log.json')
