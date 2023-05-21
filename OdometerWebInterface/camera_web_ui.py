from application import*
from threading import Lock
import cv2


camera = CameraCV()
camera.enable_logging = False
record_video_file_path = None
camera_clib_file_path = None
camera_slam_file_path = None
camera_lock = Lock()

#################################
#            BINGINGS           #
#################################
CAM_READ_FRAME = "/cam_read"
CAM_PAUSE = "/cam_pause"
CAM_EXIT = "/cam_exit"
CAM_RESET = "/cam_reset"
CAM_CALIBRATE = "/cam_calibrate"
CAM_RECORD_VIDEO = "/cam_record"
CAM_SHOW_VIDEO = "/cam_video"
CAM_SLAM_MODE = "/cam_slam"
CAM_DEPTH_MODE = "/cam_depth"
CAM_SET_FRAME_RATE = "/cam_set_frame_rate"
CAM_SET_FRAME_TIME = "/cam_set_frame_time"
CAM_SET_RESOLUTION = "/cam_set_resolution"
CAM_SET_GEOMETRY = "/cam_set_geometry"
CAM_SET_VIDEO_FILE_PATH = "/cam_set_record_file_path"
CAM_SET_CALIB_FILE_PATH = "/cam_set_calib_file_path"
CAM_SET_DEPTH_FILE_PATH = "/cam_set_depth_file_path"
CAM_SET_SLAM_FILE_PATH = "/cam_set_slam_file_path"


@web_app.route('/', methods=['GET', 'POST'])
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
        with camera_lock:
            camera.update()
            ret, buff = cv2.imencode('.jpg', camera.curr_frame)
            frame = buff.tobytes()
            yield b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'


@web_app.route(CAM_READ_FRAME)
def cam_read():
    return Response(next_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')


@web_app.route(CAM_PAUSE)
def cam_pause():
    camera.suspend()
    return NOTHING


@web_app.route(CAM_EXIT)
def cam_exit():
    camera.exit()
    return NOTHING


@web_app.route(CAM_RESET)
def cam_reset():
    camera.reset()
    return NOTHING


@web_app.route(CAM_CALIBRATE)
def cam_calibrate():
    if camera_clib_file_path is None:
        camera.calibrate()
        return NOTHING
    camera.calibrate(camera_clib_file_path)
    return NOTHING


@web_app.route(CAM_RECORD_VIDEO)
def cam_record():
    if record_video_file_path is None:
        camera.record_video()
        return NOTHING
    camera.record_video(record_video_file_path)
    return NOTHING


@web_app.route(CAM_SHOW_VIDEO)
def cam_video():
    camera.stop_mode(CALIBRATION_MODE)
    camera.stop_mode(RECORD_VIDEO_MODE)
    camera.stop_mode(SLAM_MODE)
    return NOTHING


@web_app.route(CAM_SET_FRAME_RATE, methods=['POST'])
def cam_set_frame_rate():
    frame_rate = request.form.get('cam_frame_rate')
    if not frame_rate:
        return NOTHING
    frame_rate = frame_rate.split(' ')[0].lstrip()  # ex: 30 FPS
    if web_app.debug:
        print(f"{{\"frame_rate\":  {frame_rate}}}")
    with camera_lock:
        camera.fps = int(frame_rate)
    return NOTHING


@web_app.route(CAM_SET_FRAME_TIME, methods=['POST'])
def cam_set_frame_time():
    frame_time = request.form.get('cam_frame_time')
    if not frame_time:
        return NOTHING

    frame_time = frame_time.split(' ')[0].lstrip()  # ex: 30 FPS
    if web_app.debug:
        print(f"{{\"frame_time\":  {frame_time}}}")
    with camera_lock:
        camera.update_time = float(frame_time)
    return NOTHING


@web_app.route(CAM_SET_RESOLUTION, methods=['POST'])
def cam_set_resolution():
    while True:
        if request.method != 'POST':
            break
        cam_res_select = request.form.get('cam_res_select')
        if not cam_res_select:
            break
        cam_res_select = cam_res_select.split('(')[0].lstrip().rstrip()  # ex: minimal ( 424, 240 )
        if web_app.debug:
            print(f"{{\"cam_res_select\":  \"{cam_res_select}\"}}")
        with camera_lock:
            if cam_res_select in CAMERA_RESOLUTIONS:
                if not camera.set_resolution(cam_res_select):
                    print(f"unsupported resolution :: {{\"cam_res_select\":  \"{cam_res_select}\"}}")
        break
    return NOTHING


@web_app.route(CAM_SET_GEOMETRY, methods=['POST'])
def cam_set_geometry():
    while True:
        if request.method != 'POST':
            break
        off_x  = request.form.get('offset_x')
        off_y  = request.form.get('offset_y')
        width  = request.form.get('width')
        height = request.form.get('height')

        if web_app.debug:
            print(f"{{\n"
                  f"\"off_x\" :{off_x},\n"
                  f"\"off_x\" :{off_y},\n"
                  f"\"width\" :{width},\n"
                  f"\"height\":{height}"
                  f"\n}}")

        if not off_x or not off_y or not width or not height:
            break

        with camera_lock:
            camera.width    = int(width)
            camera.height   = int(height)
            camera.offset_x = int(off_y)
            camera.offset_y = int(off_x)
    return NOTHING


@web_app.route(CAM_SET_CALIB_FILE_PATH, methods=['POST'])
def cam_set_calib_file_path():
    ...


@web_app.route(CAM_SET_VIDEO_FILE_PATH, methods=['POST'])
def cam_set_record_file_path():
    ...


@web_app.route(CAM_SET_SLAM_FILE_PATH, methods=['POST'])
def set_slam_file_path():
    ...


@web_app.route(CAM_SET_DEPTH_FILE_PATH, methods=['POST'])
def set_depth_file_path():
    ...


if __name__ == "__main__":
    web_app.run(debug=True, use_reloader=False)
