from drone_controller import DroneController

if __name__ == "__main__":
    # 4 Linux or other OS's.
    # connection  = DroneConnection("udpin:localhost:14551")
    # 4 Windows like OS's
    calib_info_src = "Utilities/CV/calibration_results.json"  # эти результаты только в качестве примера!!!
    controller = DroneController(0, calib_info_src)
    # следующие два параметра устанавливаются исходя из параметров камеры!!!
    # У КАЖОЙ КАМЕРЫ РАЗНЫЕ
    # ЕСЛИ ПОМЕНЯТЬ НАСТРОКУ ОБЪЕКТИВА, ТО ОНИ ИЗМЕНЯТСЯ ТАК ЖЕ, КАК И КАЛИБРОВОЧНЫЕ!!!
    controller.odometer.pinhole_camera.fov = 45
    controller.odometer.pinhole_camera.aspect = 1.0
    controller.update_time = 1.0
    # Полётное задание, если таково необходимо, можно напрямую отправить в MAV
    # controller.drone.drone_connection.mav...
    # ПОТОК ВЫПОЛНЯЕТСЯ БЕСКОНЕЧНО !!!
    # ДЛЯ ОГРАНИЧЕНИЯ ВРЕМЕНИ ВЫПОЛНЕНИЯ НЕОБХОДИМО ОТСЛЕЖИВАТЬ СТАТУС ПОДКЛЮЧЕНИЯ К PIXHAWK
    controller.run_in_separated_thread()
