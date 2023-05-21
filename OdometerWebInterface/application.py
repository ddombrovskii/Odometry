from Cameras import CAMERA_RESOLUTIONS
from flask import Flask, render_template, Response, request
from Cameras import CameraCV, CALIBRATION_MODE, RECORD_VIDEO_MODE, SLAM_MODE
from Accelerometer.accelerometer_core.inertial_measurement_unit import IMU

NOTHING = "nothing"
web_app = Flask(__name__, template_folder="./templates", static_folder='./static')
RESOLUTIONS = [f"{res:<10}({w:^5},{h:^5})" for res, (w, h) in CAMERA_RESOLUTIONS.items()]
FRAME_RATES = [f"{10 * i:<3}FPS" for i in range(1, 7)]