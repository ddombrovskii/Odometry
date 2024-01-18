import asyncio
import rospy
import cv2
import tf
import numpy as np

from nav_msgs.msg import Odometry
from sensor_msgs.msg import Image, Imu, Range
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import CompanionProcessStatus
from cv_bridge import CvBridge, CvBridgeError

from Utilities.flight_odometer import FlightOdometer
from Utilities.Geometry import Quaternion

from threading import Thread, Event, Lock

MAV_STATE_UNINIT = 0
MAV_STATE_BOOT = 1
MAV_STATE_CALIBRATING = 2
MAV_STATE_STANDBY = 3
MAV_STATE_ACTIVE = 4
MAV_STATE_CRITICAL = 5
MAV_STATE_EMERGENCY = 6
MAV_STATE_POWEROFF = 7
MAV_STATE_FLIGHT_TERMINATION = 8

MAV_COMP_ID_OBSTACLE_AVOIDANCE = 196
MAV_COMP_ID_VISUAL_INERTIAL_ODOMETRY = 197

rospy.init_node("publish_odometry")

odometry_pub = rospy.Publisher("/mavros/odometry/out", Odometry, queue_size=50)
odometry_status_pub = rospy.Publisher("/mavros/companion_process/status", CompanionProcessStatus, queue_size=50)
odom_broadcaster = tf.TransformBroadcaster()

cv_bridge = CvBridge()

image = None
imu = None
local_position = None
height = None
odom = FlightOdometer()


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
    """
    Обработчик изображения
    simulation: /iris/usb_cam/image_raw
    real drone: /main_camera/image_raw
    CvBridge used
    """
    global image
    image = cv_bridge.imgmsg_to_cv2(data, 'mono8')


def imu_update(data):
    """
    Обработчик данных IMU
    /mavros/imu/data
    """
    global imu
    imu = data


def range_update(data):
    """
    Обработчик данных с дальномера
    /rangefinder/range
    """
    global height
    height = data


def local_position_update(data):
    """
    Обработчик локальной позиции для получения высоты
    /mavros/local_position/pose
    """
    global local_position
    local_position = data


rospy.Subscriber("/iris/usb_cam/image_raw", Image, image_update)
rospy.Subscriber("/mavros/imu/data", Imu, imu_update)
rospy.Subscriber("/mavros/local_position/pose", PoseStamped, local_position_update)
rospy.Subscriber('rangefinder/range', Range, range_update)

rospy.loginfo("Publish Odometry started")


def compute_odometry():
    """
    Асинхронная функция расчета одометрии
    """
    global odom, image, imu, local_position

    while not rospy.is_shutdown():
        try:
            if image is not None and imu is not None and local_position is not None:
                odom.compute(image,
                             Quaternion(imu.orientation.w, imu.orientation.x,
                                        imu.orientation.y, imu.orientation.z),
                             local_position.pose.position.z)  # TODO: на реальном дроне заменить на height.range
                '''odom.compute(image,
                             Quaternion.from_euler_angles(0, 0, 0),
                             local_position.pose.position.z)  # TODO: на реальном дроне заменить на height.range'''
        except Exception as e:
            rospy.logwarn(e)


def pub_odometry():
    """
    Функция публикации данных в топик /mavros/odometry/out
    """
    global odom, imu, local_position

    r = rospy.Rate(50)
    while not rospy.is_shutdown():

        current_time = rospy.Time.now()

        odometry_status_msg = CompanionProcessStatus()
        odometry_status_msg.header.stamp = current_time
        odometry_status_msg.header.frame_id = 'base_link'

        try:
            # print('publish odom')

            odometry_msg = Odometry()

            odometry_msg.header.stamp = current_time

            odom_quat = np.array([imu.orientation.x, imu.orientation.y, imu.orientation.z, imu.orientation.w])
            odom_broadcaster.sendTransform(
                (odom.position.x, -odom.position.y, odom.position.z),
                odom_quat,
                current_time,
                "base_link",
                "odom"
            )

            odometry_msg.header.frame_id = "odom"
            odometry_msg.child_frame_id = "base_link"

            odometry_msg.pose.pose.position.x = odom.position.x
            odometry_msg.pose.pose.position.y = -odom.position.y
            odometry_msg.pose.pose.position.z = odom.position.z

            # quaternion orientation from imu!!!
            odometry_msg.pose.pose.orientation.x = imu.orientation.x
            odometry_msg.pose.pose.orientation.y = imu.orientation.y
            odometry_msg.pose.pose.orientation.z = imu.orientation.z
            odometry_msg.pose.pose.orientation.w = imu.orientation.w

            odometry_msg.twist.twist.linear.x = odom.velocity.x
            odometry_msg.twist.twist.linear.y = -odom.velocity.y
            odometry_msg.twist.twist.linear.z = odom.velocity.z

            # angular velocity from imu!!!
            odometry_msg.twist.twist.angular.x = imu.angular_velocity.x
            odometry_msg.twist.twist.angular.y = imu.angular_velocity.y
            odometry_msg.twist.twist.angular.z = imu.angular_velocity.z

            rospy.loginfo(odometry_msg)
            odometry_pub.publish(odometry_msg)

            odometry_status_msg.state = MAV_STATE_ACTIVE
            odometry_status_msg.component = MAV_COMP_ID_VISUAL_INERTIAL_ODOMETRY
            odometry_status_pub.publish(odometry_status_msg)

        except Exception as e:
            odometry_status_msg.state = MAV_STATE_CRITICAL
            odometry_status_msg.component = MAV_COMP_ID_VISUAL_INERTIAL_ODOMETRY
            odometry_status_pub.publish(odometry_status_msg)

            rospy.logwarn(e)

        r.sleep()


def main():
    thread1 = Thread(target=compute_odometry)
    thread2 = Thread(target=pub_odometry)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()


if __name__ == '__main__':
    main()
