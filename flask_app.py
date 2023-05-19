from flask import Flask, render_template, redirect, url_for, Response, request
import cv2


app = Flask(__name__, template_folder="./templates", static_folder='./static')
cam = cv2.VideoCapture(0)


def generate_frames():
    last_frame = None
    while True:
        global cam
        success, frame = cam.read()
        if not success:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + last_frame + b'\r\n')
        ret, buff = cv2.imencode('.jpg', frame)
        frame = buff.tobytes()
        last_frame = frame
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        cam_res_select = request.form.get('cam_res_select')

        cam_frametime = request.form.get('cam_framerate_time') if "cam_fps_form" in request.form else None
        cam_fps = request.form.get('cam_framerate_select') if "cam_fps_form" in request.form else None

        cam_offset_x = request.form.get('cam_offset_x')
        cam_offset_y = request.form.get('cam_offset_y')
        cam_width = request.form.get('cam_width')
        cam_height = request.form.get('cam_height')

        cam_video_format = request.form.get('cam_video_format')

        print(f"resolution: {cam_res_select}\n" + \
              f"FPS: {cam_fps}\n" + \
              f"framerate time: {cam_frametime}\n" + \
              f"offset_x: {cam_offset_x}\n" + \
              f"offset_y: {cam_offset_y}\n" +
              f"width: {cam_width}\n" + \
              f"height: {cam_height}\n" + \
              f"video format: {cam_video_format}\n" + \
              f"")

        global cam

        if cam_fps:
            cam.set(cv2.CAP_PROP_FPS, int(cam_fps))
        if cam_width:
            cam.set(cv2.CV_CAP_PROP_FRAME_WIDTH, cam_width)
            cam.set(cv2.CV_CAP_PROP_FRAME_HEIGHT, cam_height)

    '''
    В render_template можно передавать аргументы, например, списки параметров.
    То есть, в одном месте мы можем определить список возможных параметров камеры (к примеру, массив значений FPS) и там
    же реализовать изменение объекта cam от этих параметров, а сюда просто передавать в render_template списки параметров
    для каждого селектора.
    '''

    FPS_MAX = 60
    fps_list = [1, 5, 10, 20, 30, 40, FPS_MAX]
    return render_template('index.html', fps_list=fps_list)

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/set_cam_settings', methods=['POST'])
def set_cam_settings():
    print(request.form)
    redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
