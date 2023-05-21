from flask import Flask, render_template, redirect, url_for, Response, request
from Cameras import CameraCV, CAMERA_RESOLUTIONS, CALIBRATION_MODE, RECORD_VIDEO_MODE, SLAM_MODE
from threading import Lock
import cv2


app = Flask(__name__, template_folder="./templates", static_folder='./static')
camera = CameraCV()
camera.enable_logging = False
record_video_file_path = None
camera_clib_file_path = None
camera_slam_file_path = None
lock = Lock()
RESOLUTIONS = [f"{res:<10}({w:^5},{h:^5})" for res, (w, h) in CAMERA_RESOLUTIONS.items()]
FRAME_RATES = [f"{10 * i:<3}FPS" for i in range(1, 7)]


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    В render_template можно передавать аргументы, например, списки параметров.
    То есть, в одном месте мы можем определить список возможных параметров камеры (к примеру, массив значений FPS) и там
    же реализовать изменение объекта cam от этих параметров, а сюда просто передавать в render_template списки параметров
    для каждого селектора.
    """
    return render_template('index.html', fps_list=FRAME_RATES, resolutions_list=RESOLUTIONS)


def next_frame():
    while not camera.is_complete:
        with lock:
            camera.update()
            ret, buff = cv2.imencode('.jpg', camera.curr_frame)
            frame = buff.tobytes()
            yield b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'


@app.route('/get_frame')
def get_frame():
    return Response(next_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/pause')
def pause():
    camera.suspend()
    return "nothing"


@app.route('/exit')
def exit():
    camera.exit()
    return "nothing"


@app.route('/reset')
def reset():
    camera.reset()
    return "nothing"


@app.route('/calibrate')
def calibrate():
    if camera_clib_file_path is None:
        camera.calibrate()
        return "nothing"
    camera.calibrate(camera_clib_file_path)
    return "nothing"


@app.route('/record_video')
def record_video():
    if record_video_file_path is None:
        camera.record_video()
        return "nothing"
    camera.record_video(record_video_file_path)
    return "nothing"


@app.route('/show_video')
def show_video():
    camera.stop_mode(CALIBRATION_MODE)
    camera.stop_mode(RECORD_VIDEO_MODE)
    camera.stop_mode(SLAM_MODE)
    return "nothing"


@app.route('/set_frame_rate', methods=['POST'])
def set_frame_rate():
    frame_rate = request.form.get('cam_frame_rate')
    if not frame_rate:
        return "nothing"
    frame_rate = frame_rate.split(' ')[0].lstrip()  # ex: 30 FPS
    with lock:
        camera.fps = int(frame_rate)
    return "nothing"


@app.route('/set_frame_time', methods=['POST'])
def set_frame_time():
    frame_rate = request.form.get('cam_frame_time')
    if not frame_rate:
        return "nothing"

    frame_rate = frame_rate.split(' ')[0].lstrip()  # ex: 30 FPS
    with lock:
        camera.update_time = float(frame_rate)
    return "nothing"


@app.route('/set_resolution', methods=['POST'])
def set_resolution():
    while True:
        if request.method != 'POST':
            break
        cam_res_select = request.form.get('cam_res_select')
        if not cam_res_select:
            break
        cam_res_select = cam_res_select.split('(')[0].lstrip().rstrip()  # ex: minimal ( 424, 240 )
        print(f"|{cam_res_select}|")
        with lock:
            if cam_res_select in CAMERA_RESOLUTIONS:
                if not camera.set_resolution(cam_res_select):
                    print(f"unsupported resolution {cam_res_select}")
        break
    return "nothing"


@app.route('/set_geometry', methods=['POST'])
def set_geometry():
    while True:
        if request.method != 'POST':
            break
        off_x  = request.form.get('offset_x')
        off_y  = request.form.get('offset_y')
        width  = request.form.get('width')
        height = request.form.get('height')

        if not off_x or not off_y or not width or not height:
            break

        with lock:
            camera.width    = int(width)
            camera.height   = int(height)
            camera.offset_x = int(off_y)
            camera.offset_y = int(off_x)
    return "nothing"


@app.route('/set_calib_results_fp', methods=['POST'])
def set_calib_results_fp():
    ...


@app.route('/set_video_recording_fp', methods=['POST'])
def set_video_recording_fp():
    ...


@app.route('/set_slam_results_fp', methods=['POST'])
def set_slam_results_fp():
    ...


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
