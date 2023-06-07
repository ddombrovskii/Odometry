from Accelerometer.accelerometer_core import GRAVITY_CONSTANT
from Utilities.Geometry import Vector3
from application import*
from threading import Lock


imu = IMU()
imu.accelerometer.use_filtering = False
imu.enable_logging = False
imu_record_file_path = None
imu_clib_file_path = None
imu_lock = Lock()


#################################
#            BINGINGS           #
#################################
IMU_READ = "/imu_read"
IMU_PAUSE = "/imu_pause"
IMU_EXIT = "/imu_exit"
IMU_RESET = "/imu_reset"
IMU_CALIBRATE = "/imu_calibrate"
IMU_RECORD = "/imu_record"
IMU_SET_UPDATE_TIME = "/imu_set_update_time"
IMU_SET_RECORD_FILE_PATH = "/imu_set_record_file_path"
IMU_SET_CALIB_FILE_PATH = "/imu_set_calib_file_path"
IMU_SET_GRAVITY_SCALE = "/imu_set_gravity_scale"
IMU_SET_ANGLES_RATE = "/imu_set_angles_rate"
IMU_SET_TRUSTABLE_TIME = "/imu_set_trustable_time"
IMU_SET_ACCEL_THRESHOLD = "/imu_set_accel_threshold"
IMU_K_ARG = "/imu_set_k_arg"

vel = Vector3()
pos = Vector3()


@web_app.route(IMU_READ)
def imu_read():
    imu.update()
    accel  = imu.accelerometer.acceleration_local_space
    omega  = imu.omega
    angles = imu.position

    # global vel
    # global pos
    # accel = imu.acceleration - imu.accelerometer.basis * Vector3(0, 0, GRAVITY_CONSTANT)
    # vel += accel * imu.delta_t
    # omega = imu.accelerometer.basis.transpose() * vel
    # pos += vel * imu.delta_t
    # angles = imu.accelerometer.basis.transpose() * pos  # imu.angles  # - imu.velocity_clean # * Vector3(1, 1, 0)# 10 * Vector3(imu.position.x, 0, imu.position.y) #angles / math.pi * 180

    data = "{\n" \
           f"\"dtime\":  {imu.delta_t},\n" \
           f"\"accel\":  {{\"x\": {accel.x},  \"y\": {accel.y},  \"z\": {accel.z}}},\n" \
           f"\"omega\":  {{\"x\": {omega.x},  \"y\": {omega.y},  \"z\": {omega.z}}},\n" \
           f"\"angles\": {{\"x\": {angles.x}, \"y\": {angles.y}, \"z\": {angles.z}}}\n" \
           "}"
    print(data)
    return data


@web_app.route(IMU_PAUSE)
def imu_pause():
    imu.suspend()
    return NOTHING


@web_app.route(IMU_EXIT)
def imu_exit():
    imu.exit()
    return NOTHING


@web_app.route(IMU_RESET)
def imu_reset():
    imu.reset()
    return NOTHING


@web_app.route(IMU_CALIBRATE)
def imu_calibrate():
    if imu_clib_file_path is None:
        imu.calibrate()
        return NOTHING
    imu.calibrate(imu_clib_file_path)
    return NOTHING


@web_app.route(IMU_RECORD)
def imu_record():
    if imu_record_file_path is None:
        imu.begin_record()
        return NOTHING
    imu.begin_record(imu_record_file_path)
    return NOTHING


@web_app.route(IMU_SET_UPDATE_TIME, methods=['POST'])
def imu_set_update_time():
    imu_update_time = request.form.get('imu_update_time')
    if not imu_update_time:
        return NOTHING

    imu_update_time = imu_update_time.split(' ')[0].lstrip()  # ex: 30 FPS
    if web_app.debug:
        print(f"{{\"imu : imu_update_time\":  {imu_update_time}}}")
    with imu_lock:
        imu.update_time = float(imu_update_time)
    return NOTHING


@web_app.route(IMU_SET_RECORD_FILE_PATH, methods=['POST'])
def imu_set_record_file_path():
    ...


@web_app.route(IMU_SET_CALIB_FILE_PATH, methods=['POST'])
def imu_set_calib_file_path():
    ...


@web_app.route(IMU_SET_GRAVITY_SCALE, methods=['POST'])
def imu_set_gravity_scale():
    ...


@web_app.route(IMU_SET_ANGLES_RATE, methods=['POST'])
def imu_set_angles_rate():
    ...


@web_app.route(IMU_SET_TRUSTABLE_TIME, methods=['POST'])
def imu_set_trustable_time():
    trust_acc_time = request.form.get('trust_acc_time')
    if not trust_acc_time:
        return NOTHING

    trust_acc_time = trust_acc_time.split(' ')[0].lstrip()  # ex: 30 FPS
    if web_app.debug:
        print(f"{{\"imu : imu_update_time\":  {trust_acc_time}}}")
    with imu_lock:
        imu.trust_acc_time = float(trust_acc_time)
    return NOTHING


@web_app.route(IMU_SET_ACCEL_THRESHOLD, methods=['POST'])
def imu_set_accel_threshold():
    accel_threshold = request.form.get('accel_threshold')
    if not accel_threshold:
        return NOTHING

    accel_threshold = accel_threshold.split(' ')[0].lstrip()  # ex: 30 FPS
    if web_app.debug:
        print(f"{{\"imu : accel_threshold\":  {accel_threshold}}}")
    with imu_lock:
        imu.accel_threshold = float(accel_threshold)
    return NOTHING


@web_app.route(IMU_K_ARG, methods=['POST'])
def imu_set_k_arg():
    k_arg = request.form.get('k_arg')
    if not k_arg:
        return NOTHING

    k_arg = k_arg.split(' ')[0].lstrip()  # ex: 30 FPS
    if web_app.debug:
        print(f"{{\"imu : k_arg\":  {k_arg}}}")
    with imu_lock:
        imu.k_arg = float(k_arg)
    return NOTHING


@web_app.route('/', methods=['GET', 'POST'])
def index():
    # TODO MOVE TO MAIN FILE
    """
    В render_template можно передавать аргументы, например, списки параметров.
    То есть, в одном месте мы можем определить список возможных параметров камеры (к примеру, массив значений FPS) и там
    же реализовать изменение объекта cam от этих параметров, а сюда просто передавать в render_template списки параметров
    для каждого селектора.
    """
    return render_template('index.html', fps_list=FRAME_RATES, resolutions_list=RESOLUTIONS)


if __name__ == "__main__":
    imu.update()
    print(imu_read())
    # imu.calibrate(50)
    #t = 0.0
    #while t < 71.0:
    #    imu.update()
    #    print(imu.acceleration)
    #    t += imu.delta_t
    web_app.run(use_reloader=False)