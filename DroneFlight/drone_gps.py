from Mavlink import DroneConnection, GPSLocation
import time


if __name__ == "__main__":
    # Устанавливает соединение.
    # arm.
    # Выводим текущие GPS координаты.
    # Ожидает 10 секунд.
    # Вводим новые GPS координаты.
    # Ожидает 10 секунд.
    # Выводим новые GPS координаты.
    # disarm.
    # 4 Linux or other OS's.
    # connection  = DroneConnection("udpin:localhost:14551")
    # 4 Windows like OS's
    connection  = DroneConnection()
    connection.arm()
    print(connection.curr_gps)
    time.sleep(10)
    print(f"GPS coordinates sending status: {connection.send_gps(GPSLocation(1.0, 1.0, 1.0, 1.0))}")
    time.sleep(10)
    print(connection.curr_gps)
    connection.disarm()
